"""Pretrained transformer summarizer with token-aware chunking."""
from __future__ import annotations

import re
from typing import List


class SummarizationError(RuntimeError):
    """Raised when summarization cannot be completed safely."""


class NewsSummarizer:
    """Use Hugging Face's pretrained DistilBART CNN summarization model."""

    LENGTH_SETTINGS = {
        "Short": (35, 75),
        "Medium": (70, 130),
        "Long": (110, 190),
    }

    def __init__(self, model_name: str = "sshleifer/distilbart-cnn-12-6"):
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        except ImportError as exc:
            raise SummarizationError(
                "Required packages are missing. Run: python -m pip install -r requirements.txt"
            ) from exc

        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        self.model.eval()
        self.max_input_tokens = min(
            int(getattr(self.model.config, "max_position_embeddings", 1024)), 900
        )

    def _sentences(self, text: str) -> List[str]:
        # Lightweight sentence splitting; avoids adding another dependency.
        pieces = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"“'])", text.strip())
        return [piece.strip() for piece in pieces if piece.strip()] or [text.strip()]

    def _token_length(self, text: str) -> int:
        return len(self.tokenizer.encode(text, add_special_tokens=False))

    def _make_chunks(self, text: str) -> List[str]:
        chunks, current = [], []
        current_tokens = 0
        for sentence in self._sentences(text):
            sentence_tokens = self._token_length(sentence)
            # A very long sentence is split by tokenizer tokens rather than truncated.
            if sentence_tokens > self.max_input_tokens:
                if current:
                    chunks.append(" ".join(current))
                    current, current_tokens = [], 0
                ids = self.tokenizer.encode(sentence, add_special_tokens=False)
                for start in range(0, len(ids), self.max_input_tokens):
                    piece_ids = ids[start:start + self.max_input_tokens]
                    piece = self.tokenizer.decode(piece_ids, skip_special_tokens=True)
                    if piece.strip():
                        chunks.append(piece.strip())
                continue
            if current and current_tokens + sentence_tokens > self.max_input_tokens:
                chunks.append(" ".join(current))
                current, current_tokens = [], 0
            current.append(sentence)
            current_tokens += sentence_tokens
        if current:
            chunks.append(" ".join(current))
        return chunks

    def _generate(self, text: str, min_new_tokens: int, max_new_tokens: int) -> str:
        import torch
        inputs = self.tokenizer(
            text, return_tensors="pt", truncation=True,
            max_length=self.max_input_tokens,
        )
        inputs = {key: value.to(self.device) for key, value in inputs.items()}
        with torch.inference_mode():
            output_ids = self.model.generate(
                **inputs,
                min_new_tokens=min(min_new_tokens, max(5, self._token_length(text) // 4)),
                max_new_tokens=max_new_tokens,
                num_beams=4,
                length_penalty=1.0,
                no_repeat_ngram_size=3,
                early_stopping=True,
            )
        return self.tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()

    def summarize(self, text: str, length: str = "Medium") -> str:
        if not isinstance(text, str) or len(text.strip()) < 80:
            raise SummarizationError("Please provide at least 80 characters of article text.")
        if length not in self.LENGTH_SETTINGS:
            length = "Medium"
        min_new, max_new = self.LENGTH_SETTINGS[length]
        chunks = self._make_chunks(text)
        if not chunks:
            raise SummarizationError("No readable text was found.")

        try:
            summaries = [self._generate(chunk, min_new, max_new) for chunk in chunks]
            # Hierarchical reduction: summarize groups until the combined text fits.
            rounds = 0
            while self._token_length(" ".join(summaries)) > self.max_input_tokens:
                rounds += 1
                if rounds > 4:
                    raise SummarizationError(
                        "The article summaries could not be combined safely within the processing limit. "
                        "Try a smaller article or split it into sections."
                    )
                combined = " ".join(summaries)
                reduce_chunks = self._make_chunks(combined)
                if len(reduce_chunks) >= len(summaries):
                    # Use smaller groups to guarantee progress, never silently discard summaries.
                    reduce_chunks = []
                    group = []
                    group_tokens = 0
                    for summary in summaries:
                        n_tokens = self._token_length(summary)
                        if group and group_tokens + n_tokens > self.max_input_tokens:
                            reduce_chunks.append(" ".join(group))
                            group, group_tokens = [], 0
                        group.append(summary)
                        group_tokens += n_tokens
                    if group:
                        reduce_chunks.append(" ".join(group))
                    if len(reduce_chunks) >= len(summaries):
                        raise SummarizationError(
                            "Could not safely combine all article sections. Try a shorter article."
                        )
                summaries = [self._generate(chunk, min_new, max_new) for chunk in reduce_chunks]
            if len(summaries) == 1:
                return summaries[0]
            return self._generate(" ".join(summaries), min_new, max_new)
        except SummarizationError:
            raise
        except Exception as exc:
            raise SummarizationError(
                f"Model processing failed ({exc.__class__.__name__}). Check your internet connection "
                "for the first model download, available memory, and installed package versions."
            ) from exc
