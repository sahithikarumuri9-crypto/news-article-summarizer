# System Workflow

```text
Start
  |
  v
Enter pasted article text OR public article URL
  |
  +--> URL supplied? --> Validate URL --> Download public HTML
  |                                      |
  |                                      v
  |                              Extract article with Trafilatura
  |                                      |
  +--------------------------------------+
  |
  v
Clean whitespace and validate article length
  |
  v
Tokenize and split into chunks within the model input budget
  |
  v
Generate a summary for each chunk with DistilBART
  |
  v
Are combined summaries too long?
  | yes
  v
Summarize groups of summaries (bounded reduction passes)
  |
  v
Display final summary and processing statistics
  |
  v
End
```

## Module responsibilities
- `app.py`: user interface, selects text or URL input, displays output.
- `url_extractor.py`: validates and fetches public webpages and extracts main article text.
- `utils.py`: whitespace normalization and summary statistics.
- `summarizer.py`: tokenizer, chunk creation, model inference, hierarchical reduction.
- `evaluation.py`: compares model output with a reference summary using ROUGE.
