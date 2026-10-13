import streamlit as st
from summarizer import NewsSummarizer, SummarizationError
from url_extractor import extract_article_from_url, URLExtractionError

st.set_page_config(page_title="News Article Summarizer", page_icon="📰")

st.title("📰 News Article Summarizer")
st.write("Summarize news articles using a pretrained AI transformer model.")

source = st.radio("Choose article source", ["Paste Text", "Article URL"])

article_text = ""
article_title = ""

if source == "Paste Text":
    article_text = st.text_area(
        "Paste your news article here",
        height=250
    )
else:
    article_url = st.text_input("Enter the public news article URL")

    if st.button("Extract Article"):
        if article_url.strip():
            try:
                article = extract_article_from_url(article_url.strip())
                st.session_state["article_text"] = article["text"]
                st.session_state["article_title"] = article["title"]
                st.success("Article extracted successfully!")
            except URLExtractionError as error:
                st.error(str(error))

    article_text = st.session_state.get("article_text", "")
    article_title = st.session_state.get("article_title", "")

if article_title:
    st.subheader(article_title)

length = st.selectbox(
    "Summary length",
    ["Short", "Medium", "Long"],
    index=1
)

if st.button("Generate Summary"):
    if len(article_text.strip()) < 80:
        st.error("Please provide at least 80 characters of article text.")
    else:
        try:
            with st.spinner("Loading AI model and generating summary..."):
                if "summarizer" not in st.session_state:
                    st.session_state["summarizer"] = NewsSummarizer()

                summarizer = st.session_state["summarizer"]
                summary = summarizer.summarize(article_text, length)

            st.subheader("Generated Summary")
            st.write(summary)

        except SummarizationError as error:
            st.error(str(error))
        except Exception as error:
            st.error(f"Something went wrong: {error}")
