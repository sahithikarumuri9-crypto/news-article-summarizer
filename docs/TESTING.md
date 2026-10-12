# Testing Guide

## Automated unit tests
Run:

```powershell
python -m unittest discover -s tests -v
```

These tests cover whitespace cleanup, word counting, and compression percentage. They do not download the transformer model.

## Manual functional tests
1. Paste a short news article of at least 80 characters and summarize it.
2. Try Short, Medium, and Long settings.
3. Enter a valid publicly accessible news URL.
4. Try an invalid URL such as `not-a-url`; the app should show a readable error.
5. Try a URL that requires login; the app should report that extraction failed rather than bypass access controls.
6. Test an article longer than one model input chunk.
7. Verify word counts and compression statistics are plausible.
8. Compare summary statements with the original article for factual consistency.

## Evaluation
Prepare article/reference text files and run `evaluation.py`. Keep a results table for several examples with ROUGE scores and manual observations. Do not treat one score as proof of overall quality.
