import re
import numpy as np
from sentence_transformers import SentenceTransformer

# Load SBERT model once
MODEL_NAME = "all-MiniLM-L6-v2"
print(f"🧠 Loading SentenceTransformer model: {MODEL_NAME}")
embedder = SentenceTransformer(MODEL_NAME)


def has_negation(text: str) -> bool:
    return re.search(r"\b(not|never|no|none|n't)\b", text.lower()) is not None


def embed(text: str) -> np.ndarray:
    return embedder.encode([text], convert_to_numpy=True)[0]


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)  # [-1, 1]


def similarity_score(a: str, b: str) -> float:
    """
    Returns similarity in [0,1]
    """
    ea = embed(a)
    eb = embed(b)
    sim = cosine_sim(ea, eb)           # [-1, 1]
    return (sim + 1) / 2               # [0, 1]


def split_sentences(text: str):
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [p for p in parts if p]


def sentence_score(
    notes: str,
    sentence: str,
    base_threshold: float = 0.6,
    negation_penalty: float = 0.25
):
    """
    Score a single sentence.
    If sentence has negation but notes don't, penalize it.
    """
    base = similarity_score(notes, sentence)

    notes_neg = has_negation(notes)
    sent_neg = has_negation(sentence)

    adjusted = base
    neg_flag = False
    if sent_neg and not notes_neg:
        adjusted = max(0.0, base - negation_penalty)
        neg_flag = True

    label = "correct" if adjusted >= base_threshold else "not_correct"

    return {
        "sentence": sentence,
        "base_score": base,
        "adjusted_score": adjusted,
        "label": label,
        "negation_flag": neg_flag,
    }


def analyze_explanation(
    notes: str,
    explanation: str,
    global_threshold: float = 0.6,
    sentence_threshold: float = 0.6
):
    """
    Main entrypoint:
    - scores whole explanation
    - scores each sentence
    """
    # global score: similarity between notes and full explanation
    global_score = similarity_score(notes, explanation)
    global_label = "correct" if global_score >= global_threshold else "not_correct"

    sentences = split_sentences(explanation)
    sentence_results = [
        sentence_score(notes, s, base_threshold=sentence_threshold)
        for s in sentences
    ]

    return {
        "global_label": global_label,
        "global_score": global_score,
        "sentences": sentence_results,
    }


def level_from_score(score: float) -> str:
    """
    Coarse correctness level for UI / LLM.
    """
    if score >= 0.8:
        return "high"
    elif score >= 0.6:
        return "medium"
    elif score >= 0.4:
        return "low"
    else:
        return "very_low"


if __name__ == "__main__":
    # quick sanity test
    notes = "A queue uses FIFO: first-in, first-out. Elements are removed in the same order they are inserted."
    explanation = (
        "A queue is like a line at a store: whoever comes first is not served first. "
        "Queues are used in breadth-first search to visit nodes layer by layer. "
        "If it removed the newest item first, it would act like a stack not a queue."
    )

    result = analyze_explanation(notes, explanation)
    print("Global label:", result["global_label"])
    print("Global score:", result["global_score"], f"({result['global_score']*100:.1f}% similarity)")
    print("Level:", level_from_score(result["global_score"]))

    print("\nSentence breakdown:")
    for s in result["sentences"]:
        print("-")
        print("Sentence:", s["sentence"])
        print("Base score:", f"{s['base_score']:.3f}")
        print("Adjusted score:", f"{s['adjusted_score']:.3f}")
        print("Negation_flag:", s["negation_flag"])
        print("Label:", s["label"])
