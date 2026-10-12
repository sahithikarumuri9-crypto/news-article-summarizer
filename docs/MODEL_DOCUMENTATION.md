# Model Documentation

## Selected model
`sshleifer/distilbart-cnn-12-6`, loaded using Hugging Face Transformers.

## Model type
A pretrained encoder-decoder transformer in the DistilBART/BART family, adapted for news summarization. It generates new text rather than only selecting sentences from the article.

## Input and output
- Input: cleaned article text, or a chunk of a long article.
- Output: a generated summary string.
- The interface offers Short, Medium, and Long generation settings. These settings influence generation length; they do not guarantee an exact word count.

## Why use a pretrained transformer?
A pretrained model already learned language patterns and summarization behavior from large training data. This avoids the cost of training a transformer from scratch and is suitable for a student prototype.

## Processing of long articles
The application counts tokenizer tokens and creates chunks that fit the model's input budget. Each chunk is summarized. If the collection of chunk summaries is still too long, reduction passes summarize the combined summaries. The program raises an error rather than intentionally discarding remaining summaries if it cannot reduce them safely.

## Inference settings
The code uses beam search (`num_beams=4`), a no-repeat n-gram constraint, and length settings selected by the user. The model runs on CUDA if PyTorch detects a compatible GPU; otherwise it uses CPU.

## Training versus inference
This project performs inference with pretrained weights. It does not fine-tune the model on a project dataset. Any report should state this accurately.

## Risks and responsible use
- Generated text may omit details or introduce unsupported statements.
- Names, dates, numbers, and quotations should be checked against the original.
- Do not use the summary as the sole source for high-stakes decisions.
- Evaluation should use several articles and human-written references.
