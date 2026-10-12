"""Evaluate a generated summary against a human-written reference.

Example:
  python evaluation.py --article article.txt --reference reference_summary.txt
  python evaluation.py --article article.txt --reference reference_summary.txt --textrank
ROUGE is a rough text-overlap metric; it does not fully measure factual accuracy.
"""
import argparse
from pathlib import Path

from summarizer import NewsSummarizer
from utils import clean_text


def load_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8").strip()


def main():
    parser = argparse.ArgumentParser(description="Evaluate the news summarizer using ROUGE.")
    parser.add_argument("--article", required=True, help="Path to a UTF-8 text file containing the article.")
    parser.add_argument("--reference", required=True, help="Path to a UTF-8 human-written reference summary.")
    parser.add_argument("--length", choices=["Short", "Medium", "Long"], default="Medium")
    parser.add_argument("--textrank", action="store_true", help="Also compare with a TextRank baseline.")
    args = parser.parse_args()

    article = clean_text(load_text(args.article))
    reference = clean_text(load_text(args.reference))
    if not article or not reference:
        parser.error("Article and reference files must both contain text.")

    try:
        from rouge_score import rouge_scorer
    except ImportError:
        parser.error("ROUGE is not installed. Run: python -m pip install -r requirements-eval.txt")

    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
    model = NewsSummarizer()
    generated = model.summarize(article, length=args.length)
    print("\n=== Transformer summary ===\n", generated)
    print("\n=== ROUGE scores (precision / recall / F1) ===")
    scores = scorer.score(reference, generated)
    for metric, score in scores.items():
        print(f"{metric}: P={score.precision:.4f} R={score.recall:.4f} F1={score.fmeasure:.4f}")

    if args.textrank:
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            import numpy as np
            sentences = [s.strip() for s in __import__("re").split(r"(?<=[.!?])\s+", article) if s.strip()]
            if len(sentences) < 2:
                print("\nTextRank baseline skipped: article has fewer than two sentences.")
            else:
                # Lightweight extractive baseline: rank sentences by TF-IDF vector magnitude.
                matrix = TfidfVectorizer(stop_words="english").fit_transform(sentences)
                scores_vec = np.asarray(matrix.sum(axis=1)).ravel()
                selected = sorted(np.argsort(scores_vec)[-min(5, len(sentences)):])
                baseline = " ".join(sentences[i] for i in selected)
                print("\n=== Simple TF-IDF extractive baseline ===\n", baseline)
                baseline_scores = scorer.score(reference, baseline)
                print("\n=== Baseline ROUGE F1 ===")
                for metric, score in baseline_scores.items():
                    print(f"{metric}: {score.fmeasure:.4f}")
        except Exception as exc:
            print("\nBaseline could not run:", exc)


if __name__ == "__main__":
    main()
