# News Article Summarizer Using NLP and a Pretrained Transformer

A student project that summarizes pasted news text or an accessible public article URL with the pretrained Hugging Face model `sshleifer/distilbart-cnn-12-6`.

## Features

- Paste article text or enter a public article URL.
- Extract main article text from supported webpages using Trafilatura.
- Split long articles into token-sized sections before summarizing.
- Combine section summaries hierarchically instead of silently dropping content.
- Display summary length, word counts, compression percentage, and elapsed time.
- Optional ROUGE evaluation against a human-written reference summary.
- Optional simple TF-IDF extractive baseline for comparison.

## Project workflow

1. User enters article text or URL.
2. For URL input, validate and fetch a public HTML page, then extract the main article.
3. Clean whitespace and validate article length.
4. Tokenize and split long text into manageable chunks.
5. Generate summaries with pretrained DistilBART.
6. Combine chunk summaries if necessary.
7. Display the summary and basic processing statistics.

## Setup on Windows / VS Code

Use Python 3.10 or 3.11 if possible.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:7860` in your browser. The first run downloads model files, so it may take time and requires internet access.

For evaluation features:

```powershell
python -m pip install -r requirements-eval.txt
```

## Evaluation

Create two UTF-8 text files:
- `article.txt`: original article
- `reference_summary.txt`: a human-written reference summary

Then run:

```powershell
python evaluation.py --article article.txt --reference reference_summary.txt --length Medium
```

Optional baseline comparison:

```powershell
python evaluation.py --article article.txt --reference reference_summary.txt --textrank
```

ROUGE measures word/phrase overlap with a reference; it is not proof of factual correctness. Use multiple articles and human review for a fair project evaluation.

## Run tests

```powershell
python -m unittest discover -s tests -v
```

## Model

- Model ID: `sshleifer/distilbart-cnn-12-6`
- Model family: encoder-decoder transformer based on DistilBART/BART.
- Intended task: abstractive summarization.
- The project uses a pretrained model; it does not train a new transformer from scratch.
- Output can contain errors or unsupported claims. Always compare important summaries with the source.

## URL fetching and limitations

The URL fetcher blocks many private/local addresses, limits response size and time, checks redirects, and only accepts standard HTTP/HTTPS ports. These checks are defense-in-depth, not a complete production security boundary: DNS rebinding and network-routing edge cases require infrastructure-level outbound network restrictions or an isolated fetch service. This demo does not bypass paywalls, logins, CAPTCHAs, or anti-bot systems. Some news sites may not expose article text to automated fetchers.

## Deployment

For a public demo, Hugging Face Spaces with Gradio is one option. Before public deployment, review `docs/DEPLOYMENT.md`, configure resource limits, and strengthen URL-fetch isolation. Large model downloads and CPU inference can be slow or exceed small free-tier memory limits.

## Main files

- `app.py`: Gradio interface and input routing
- `url_extractor.py`: public webpage fetching and article extraction
- `summarizer.py`: transformer loading, chunking, and summarization
- `utils.py`: text cleanup and statistics
- `evaluation.py`: ROUGE and optional extractive baseline
- `docs/`: model, workflow, testing, and deployment notes
