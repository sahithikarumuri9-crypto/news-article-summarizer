"""Gradio interface for the News Article Summarizer."""
import time
import gradio as gr

from summarizer import NewsSummarizer, SummarizationError
from url_extractor import extract_article_from_url, URLExtractionError
from utils import (
    clean_text, word_count, compression_percent,
    split_headline, title_from_summary, tidy_summary,
)

MODEL_NAME = "sshleifer/distilbart-cnn-12-6"
summarizer = NewsSummarizer(model_name=MODEL_NAME)


def summarize_article(text, url, length):
    """Summarize either pasted text or an article URL."""
    started = time.perf_counter()
    source_url = ""
    title = ""
    title_is_generated = False
    try:
        if url and url.strip():
            article = extract_article_from_url(url.strip())
            text = article["text"]
            title = article.get("title", "")
            source_url = article.get("url", url.strip())
        else:
            # Pasted text: look for a headline BEFORE clean_text(), because
            # clean_text() removes all line breaks (that is why the title was lost).
            title, text = split_headline(text or "")
        text = clean_text(text or "")
        if len(text) < 80:
            raise ValueError("Please paste a longer article (at least 80 characters) or enter a valid article URL.")
        if len(text) > 100_000:
            raise ValueError("The article is too long for this demo (maximum 100,000 characters).")
        summary = tidy_summary(summarizer.summarize(text, length=length))
        if not title:
            title = title_from_summary(summary)
            title_is_generated = bool(title)
        title_line = f"{title} *(auto-generated from the summary)*" if title_is_generated else title
        elapsed = time.perf_counter() - started
        info = (
            f"**Title:** {title_line or 'Not detected'}\n\n"
            f"**Source URL:** {source_url or 'Pasted text'}\n\n"
            f"**Original words:** {word_count(text)}  |  "
            f"**Summary words:** {word_count(summary)}  |  "
            f"**Compression:** {compression_percent(text, summary)}%  |  "
            f"**Time:** {elapsed:.1f} seconds"
        )
        return summary, info
    except (ValueError, URLExtractionError, SummarizationError) as exc:
        return "", f"**Could not summarize:** {exc}"
    except Exception as exc:
        # Keep technical details in the terminal, not in the public UI.
        print("Unexpected summarization error:", repr(exc))
        return "", "An unexpected error occurred. Check the VS Code terminal for details."


with gr.Blocks(title="News Article Summarizer") as demo:
    gr.Markdown(
        "# News Article Summarizer\n"
        "Summarize a news article using a pretrained DistilBART transformer. "
        "Paste article text or provide a publicly accessible article URL."
    )
    with gr.Row():
        with gr.Column():
            article_text = gr.Textbox(
                label="Article text",
                placeholder="Paste the full article here. Leave blank if using a URL.",
                lines=12,
            )
            article_url = gr.Textbox(
                label="Article URL (optional)",
                placeholder="https://example.com/news/article",
            )
            length = gr.Radio(
                choices=["Short", "Medium", "Long"],
                value="Medium",
                label="Summary length",
            )
            run_button = gr.Button("Summarize article", variant="primary")
        with gr.Column():
            summary_output = gr.Textbox(label="Generated summary", lines=12)
            details_output = gr.Markdown(label="Article details")
    run_button.click(
        fn=summarize_article,
        inputs=[article_text, article_url, length],
        outputs=[summary_output, details_output],
    )
    gr.Markdown(
        "**Note:** Some sites block automated access or require login. "
        "This app does not bypass paywalls, logins, or anti-bot controls."
    )

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)



