# Project Documentation

## Title
Automatic News Article Summarizer Using NLP and a Pretrained Transformer

## Problem statement
News articles can be long and time-consuming to read. This project produces a shorter version that retains the main ideas, allowing readers to understand the central information more quickly.

## Objectives
1. Accept pasted article text or a publicly accessible article URL.
2. Extract article content from supported webpages.
3. Generate an abstractive summary with a pretrained transformer.
4. Handle long inputs by chunking and combining section summaries.
5. Display useful statistics and provide a basic evaluation path.

## Scope
This is a prototype for educational use. It is not a fact-checking system and cannot guarantee that every generated sentence is correct. The URL feature depends on website accessibility and page structure.

## High-level architecture
User input -> input validation -> optional URL extraction -> text cleanup -> token-aware chunking -> pretrained DistilBART -> hierarchical summary reduction -> output and metrics.

## Technology stack
- Python
- Hugging Face Transformers
- PyTorch
- Gradio
- Trafilatura
- Requests
- ROUGE Score (optional evaluation)

## Expected output
A concise generated summary, detected title when available, source URL or pasted-text label, original and summary word counts, compression percentage, and elapsed time.

## Evaluation plan
Use a set of articles with human-written reference summaries. Record ROUGE-1, ROUGE-2, and ROUGE-L, then manually inspect factual consistency, readability, and whether key facts were omitted. Compare with the optional simple extractive baseline. Do not claim accuracy from a single article.

## Limitations
- Summary quality depends on the pretrained model and input article.
- Very long articles require multiple generation passes and may be slower.
- Article extraction may fail on dynamic, protected, or paywalled websites.
- CPU inference can be slow.
- ROUGE is a text-overlap metric and does not fully measure factual correctness.
