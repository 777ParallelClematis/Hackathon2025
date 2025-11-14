import json
from textwrap import dedent

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

MODEL_NAME = "google/gemma-2b-it"
print(f"Loading Gemma model: {MODEL_NAME}")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
gen_pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=512,
    do_sample=False,
)


def build_prompt(notes: str, explanation: str, analysis: dict) -> str:
    global_label = analysis.get("global_label")
    global_score = analysis.get("global_score")

    suspicious_sentences = []
    for s in analysis.get("sentences", []):
        if s["label"] == "not_correct" or s.get("negation_flag"):
            suspicious_sentences.append(
                {
                    "sentence": s["sentence"],
                    "score": s["adjusted_score"],
                    "negation_flag": s.get("negation_flag", False),
                }
            )

    prompt = dedent(f"""
    You are a helpful teaching assistant.
    You will receive:
    1) A student's notes.
    2) The student's explanation.
    3) A heuristic analysis that guesses which sentences might be weak.

    The heuristic gives:
    - global_label: "{global_label}"
    - global_score: {global_score:.3f}  (0 to 1, higher means more correct)
    - suspicious_sentences: a list of sentences that may be wrong, unclear, or contradictory.

    Tasks:
    1. Briefly summarize what the student did WELL based on the notes and explanation.
    2. For each suspicious sentence, explain in simple language:
       - what is wrong or confusing
       - how to fix it,
       and give a corrected version of the sentence.
    3. Provide a short cheat sheet of the key ideas the student should remember:
       - use bullet points
       - keep it under 200 words
    4. Be kind and encouraging.

    Return ONLY valid JSON with this structure:
    {{
      "overall_comment": "short paragraph praising and orienting the student",
      "sentence_feedback": [
        {{
          "original": "the original suspicious sentence",
          "issue": "what is wrong / missing / unclear",
          "correction": "a clearer, correct version"
        }}
      ],
      "cheat_sheet": "bullet point list as a single string"
    }}

    --- STUDENT NOTES ---
    {notes}

    --- STUDENT EXPLANATION ---
    {explanation}

    --- HEURISTIC SUSPICIOUS SENTENCES (JSON) ---
    {json.dumps(suspicious_sentences, indent=2)}
    """).strip()

    return prompt


def generate_feedback_with_gemma(notes: str, explanation: str, analysis: dict) -> dict:
    prompt = build_prompt(notes, explanation, analysis)

    out = gen_pipe(prompt, num_return_sequences=1)[0]["generated_text"]

    # try to extract JSON from the output
    first = out.find("{")
    last = out.rfind("}")
    if first != -1 and last != -1 and last > first:
        json_str = out[first:last + 1]
    else:
        json_str = out

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        data = {
            "overall_comment": "I had trouble parsing my own output, but please compare your explanation carefully with your notes.",
            "sentence_feedback": [],
            "cheat_sheet": "- Review your notes.\n- Focus on correcting contradictory statements.\n- Practice explaining the concept in your own words.",
        }

    data.setdefault("overall_comment", "")
    data.setdefault("sentence_feedback", [])
    data.setdefault("cheat_sheet", "")

    return data
