from classifier.semantic import analyze_explanation, level_from_score
from llm_gemma import generate_feedback_with_gemma


if __name__ == "__main__":
    notes = (
        "A queue uses FIFO: first-in, first-out. "
        "Elements are removed in the same order they are inserted."
    )

    explanation = (
        "A queue is like a line at a store: whoever comes first is not served first. "
        "Queues are used in breadth-first search to visit nodes layer by layer. "
        "If it removed the newest item first, it would act like a stack not a queue."
    )

    # 1) heuristic analysis
    analysis = analyze_explanation(notes, explanation)
    print("Heuristic global_label:", analysis["global_label"])
    print("Heuristic global_score:", analysis["global_score"],
          f"({analysis['global_score']*100:.1f}% similarity)")
    print("Heuristic level:", level_from_score(analysis["global_score"]))

    # 2) LLM feedback: Gemma-2B
    feedback = generate_feedback_with_gemma(notes, explanation, analysis)

    print("\n=== LLM FEEDBACK (Gemma) ===")
    print("\nOverall comment:\n", feedback["overall_comment"])
    print("\nSentence feedback:")
    for sf in feedback["sentence_feedback"]:
        print("- Original:", sf.get("original"))
        print("  Issue:", sf.get("issue"))
        print("  Correction:", sf.get("correction"))
    print("\nCheat sheet:\n", feedback["cheat_sheet"])
