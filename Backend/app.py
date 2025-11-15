from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import re
import time
import requests
import json
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
from difflib import SequenceMatcher
from waitress import serve  # Using Waitress to fix the Windows socket error

from config import (
    MINILM_MODEL_NAME,
    GEMINI_API_KEY,
    CLASSIFICATION_THRESHOLD,
    MONGO_URI,
    MONGO_DB_NAME,
    MONGO_REF_COLLECTION,
    MONGO_GRADES_COLLECTION,
)

from routes.user_routes import user_routes
from db import get_db

load_dotenv()

app = Flask(__name__)
CORS(app)

# ----------------------------
# BLUEPRINTS
# ----------------------------
app.register_blueprint(user_routes, url_prefix="/api/users")


# ----------------------------
# MODEL / HELPER CLASSES
# ----------------------------

class MiniLMClassifier:
    """
    Placeholder class for the MiniLM model logic.
    You must implement the actual model loading and comparison logic.
    """
    def __init__(self, model_name: str, threshold: float):
        print(f"Loading MiniLM Classifier: {model_name} with threshold {threshold}...")
        self.threshold = threshold
        self.model = None

    def classify_response_on_demand(
        self, note_title: str, user_response: str, reference_standard: str
    ) -> tuple[bool, float]:
        """
        Calculates the similarity score between the user response and the reference standard.
        """
        if len(user_response) > 50 and len(reference_standard) > 50:
            score = 0.85
        else:
            score = 0.45

        is_correct = score >= self.threshold
        return is_correct, score

class GeminiHelper:
    """
    Uses Gemini (gemini-2.5-flash) to:
    1) Analyze the student's answer vs reference notes.
    2) Produce structured feedback (overall / strengths / improvements).
    3) Identify missing_keywords (key concepts not well covered by the student).
    4) Build a cheat sheet: each missing keyword + a short explanation.

    Returns (feedback_text, keywords, cheat_sheet_text).
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model_name = "gemini-2.5-flash"
        self.api_url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model_name}:generateContent"
        )

    # ----------------- low-level helper -----------------

    def _call_gemini(self, prompt: str) -> str:
        """Call Gemini and return the concatenated text of the first candidate."""
        payload = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }

        resp = requests.post(
            self.api_url,
            params={"key": self.api_key},
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        candidates = data.get("candidates", [])
        if not candidates:
            raise ValueError("No candidates returned from Gemini")

        parts = candidates[0].get("content", {}).get("parts", [])
        texts = [
            p.get("text", "")
            for p in parts
            if isinstance(p, dict) and p.get("text")
        ]
        full_text = " ".join(texts).strip()
        if not full_text:
            raise ValueError("Empty text in Gemini response")

        return full_text

    # ----------------- main public method -----------------

    def analyze_and_suggest(
        self,
        title: str,
        user_response: str,
        reference_standard: str,
        score: float,
    ) -> tuple[str, list[str], str]:
        """
        Returns:
            feedback_text (str)  → multi-section feedback
            keywords (list[str]) → missing concepts (for chips + cheat sheet)
            cheat_sheet (str)    → bullet list: '- keyword: explanation'
        """

        # ---------- 1) Ask Gemini for analysis + missing keywords ----------
        analysis_prompt = f"""
You are an academic grading assistant.

Compare the student's response to the reference standard and produce:

1. "overall": A brief overall assessment (1–3 sentences).
2. "strengths": A list of 2–4 specific strengths.
3. "improvements": A list of 2–4 specific, actionable improvements.
4. "missing_keywords": A list of 3–5 key concepts that appear in the reference
   but are missing or poorly explained in the student's response.

IMPORTANT:
- "missing_keywords" MUST focus on gaps in the student's answer.
- Be kind, specific, and helpful.
- Do NOT mention the similarity score directly, but you may implicitly
  use it to judge how complete the answer is.

Title: {title}
Approximate similarity score from another model: {score:.2f}

Student Response:
{user_response}

Reference Standard:
{reference_standard}

Return ONLY valid JSON, with no extra commentary, in exactly this format:

{{
  "overall": "overall feedback here",
  "strengths": ["strength 1", "strength 2"],
  "improvements": ["improvement 1", "improvement 2"],
  "missing_keywords": ["keyword1", "keyword2", "keyword3"]
}}
"""

        # ---- Fallback defaults ----
        fallback_overall = (
            f"Your answer on '{title}' shows some understanding, but you should "
            "add more detail and connect more closely to the key ideas in your notes."
        )
        fallback_strengths = ["You attempted to describe the main concept."]
        fallback_improvements = [
            "Add more precise definitions and key terms from your notes.",
            "Include at least one clear example or important detail.",
        ]

        # naive missing-word guess if Gemini fails entirely
        ref_words = [
            re.sub(r"[^\w]", "", w.lower())
            for w in reference_standard.split()
        ]
        student_words = {
            re.sub(r"[^\w]", "", w.lower())
            for w in user_response.split()
        }
        missing_guess = [
            w for w in ref_words
            if len(w) > 5 and w not in student_words
        ]
        seen = {}
        for w in missing_guess:
            if w and w not in seen:
                seen[w] = True
        fallback_keywords = list(seen.keys())[:3] or ["concepts", "details", "examples"]

        # Try the analysis call
        try:
            raw_text = self._call_gemini(analysis_prompt)

            # Strip ```json fences if present
            cleaned = raw_text.strip()
            if cleaned.startswith("```"):
                cleaned = re.sub(r"^```[a-zA-Z0-9]*\s*", "", cleaned)
                cleaned = re.sub(r"\s*```$", "", cleaned).strip()

            # If there's narration around JSON, grab the first {...}
            if not cleaned.startswith("{"):
                m = re.search(r"\{.*\}", cleaned, re.DOTALL)
                if m:
                    cleaned = m.group(0)

            parsed = json.loads(cleaned)

            overall = parsed.get("overall", fallback_overall)
            strengths = parsed.get("strengths", fallback_strengths)
            improvements = parsed.get("improvements", fallback_improvements)
            missing_keywords = parsed.get("missing_keywords", fallback_keywords)

            # Normalize lists
            if not isinstance(strengths, list):
                strengths = fallback_strengths
            else:
                strengths = [str(s).strip() for s in strengths if str(s).strip()]

            if not isinstance(improvements, list):
                improvements = fallback_improvements
            else:
                improvements = [str(i).strip() for i in improvements if str(i).strip()]

            if not isinstance(missing_keywords, list):
                keywords = fallback_keywords
            else:
                keywords = [
                    str(k).strip()
                    for k in missing_keywords
                    if str(k).strip()
                ][:5]

        except Exception as e:
            print(f"[WARN] Gemini analysis failed, using fallback. Error: {e}")
            overall = fallback_overall
            strengths = fallback_strengths
            improvements = fallback_improvements
            keywords = fallback_keywords

        # ---------- 2) Build cheat sheet: keyword → short explanation ----------

        cheat_sheet_text = self._build_cheat_sheet_from_keywords(
            title=title,
            reference_standard=reference_standard,
            keywords=keywords,
        )

        # ---------- 3) Build structured feedback text ----------

        strengths_block = "\n".join(f"- {s}" for s in strengths)
        improvements_block = "\n".join(f"- {i}" for i in improvements)

        feedback_text = (
            f"Overall:\n{overall}\n\n"
            f"Strengths:\n{strengths_block}\n\n"
            f"Areas for improvement:\n{improvements_block}"
        )

        return feedback_text, keywords, cheat_sheet_text

    # ----------------- cheat sheet helper -----------------

    def _build_cheat_sheet_from_keywords(
        self,
        title: str,
        reference_standard: str,
        keywords: list[str],
    ) -> str:
        """
        Ask Gemini to generate a short explanation for each keyword.
        Format: '- keyword: explanation'.
        If it fails, fall back to a simple template list.
        """
        if not keywords:
            return "No specific missing concepts identified."

        prompt = f"""
You are helping a student revise the topic "{title}".

For each of the following key concepts:

{keywords}

Write a VERY short cheat sheet as bullet points.
Each bullet MUST be in this format:

- keyword: one simple sentence explaining it

Rules:
- Use the student's level (high school / intro university).
- Max 1 sentence per keyword.
- No extra commentary before or after the list.
"""

        try:
            raw_text = self._call_gemini(prompt).strip()

            # If Gemini is chatty, we still only want lines starting with '-'
            lines = [ln for ln in raw_text.splitlines() if ln.strip().startswith("-")]
            if not lines:
                raise ValueError("No bullet lines found in cheat sheet response")

            cheat_sheet = "\n".join(lines)
            return cheat_sheet

        except Exception as e:
            print(f"[WARN] Gemini cheat sheet generation failed, using fallback. Error: {e}")
            # Simple fallback: one generic sentence per keyword
            fallback_lines = [
                f"- {k}: important concept you should review for this topic."
                for k in keywords
            ]
            return "\n".join(fallback_lines)     
    
class MongoReferenceFetcher:
    FALLBACK_REFERENCE_TEXT = (
        "A queue follows the First-In, First-Out (FIFO) principle. "
        "Add at rear, remove from front."
    )

    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB_NAME]

        # Reference collection is 'notes' (source of 500-word standard)
        self.ref_collection = self.db[MONGO_REF_COLLECTION]

        # Grades collection is 'student_attempts' (destination for results)
        self.grades_collection = self.db[MONGO_GRADES_COLLECTION]

    # ---------- PUBLIC API ----------

    def get_reference_standard(self, note_title: str) -> str:
        """
        Returns the reference 'note_text' for a given title.

        Strategy:
        1. Try exact match on 'title'
        2. Try case-insensitive exact match
        3. Try fuzzy best-match across all titles
        4. If still nothing, return a safe fallback reference text
        """
        if not note_title:
            print("[WARN] get_reference_standard called with empty note_title.")
            return self.FALLBACK_REFERENCE_TEXT

        # 1. Exact match (case-sensitive)
        document = self.ref_collection.find_one({"title": note_title})

        # 2. Case-insensitive exact match (e.g., 'Queues' vs 'queues')
        if not document:
            ci_query = {
                "title": {
                    "$regex": f"^{re.escape(note_title)}$",
                    "$options": "i",  # case-insensitive
                }
            }
            document = self.ref_collection.find_one(ci_query)

        # 3. Fuzzy best-match
        if not document:
            matched_title = self.find_best_matching_title(note_title)
            if matched_title:
                document = self.ref_collection.find_one({"title": matched_title})
                print(
                    f"[INFO] Fuzzy matched '{note_title}' → "
                    f"'{matched_title}' for reference standard."
                )

        # 4. Still nothing → fallback
        if not document or "note_text" not in document:
            print(
                f"[WARN] No reference standard found in '{MONGO_REF_COLLECTION}' "
                f"for requested title '{note_title}'. Using fallback text."
            )
            return self.FALLBACK_REFERENCE_TEXT

        print(
            f"[INFO] Using reference standard with stored title "
            f"'{document.get('title')}' for requested '{note_title}'."
        )
        return document["note_text"]

    # ---------- INTERNAL HELPERS ----------

    def find_best_matching_title(self, note_title: str) -> str | None:
        """
        Return the title from DB that best matches the provided title
        using normalized string similarity.
        """
        user_norm = self._normalize_title(note_title)

        titles_cursor = self.ref_collection.find({}, {"title": 1})
        best_match: str | None = None
        best_score: float = 0.0

        for doc in titles_cursor:
            t = doc.get("title")
            if not t:
                continue

            t_norm = self._normalize_title(t)
            score = SequenceMatcher(None, user_norm, t_norm).ratio()

            if score > best_score:
                best_score = score
                best_match = t

        # Require a minimum similarity to avoid random garbage matches
        if best_match and best_score >= 0.7:
            print(
                f"[DEBUG] Best fuzzy match for '{note_title}' → "
                f"'{best_match}' (score={best_score:.3f})"
            )
            return best_match

        print(
            f"[DEBUG] No acceptable fuzzy match found for '{note_title}'. "
            f"Best score was {best_score:.3f} (below threshold)."
        )
        return None

    def _normalize_title(self, title: str) -> str:
        """
        Lowercase, trim, and collapse whitespace so small differences
        don't ruin similarity scores.
        """
        title = title.strip().lower()
        title = re.sub(r"\s+", " ", title)  # collapse multiple spaces
        return title

    # ---------- SAVE GRADES ----------

    def save_grade_result(self, grade_data: dict) -> bool:
        """Inserts the final grading result into the student_attempts collection."""
        grade_data["graded_at"] = datetime.utcnow()
        try:
            self.grades_collection.insert_one(grade_data)
            print(
                f"Successfully saved grade for student {grade_data.get('student_id')} "
                f"on topic: {grade_data.get('title')}"
            )
            return True
        except Exception as e:
            print(f"Error saving grade to DB: {e}")
            return False


db_fetcher = MongoReferenceFetcher()
classifier = MiniLMClassifier(MINILM_MODEL_NAME, CLASSIFICATION_THRESHOLD)
gemini_helper = GeminiHelper(GEMINI_API_KEY)


def prepare_grade_data(
    student_id,
    title,
    student_response,
    score,
    classification,
    feedback,
    source,
    keywords=None,
    cheat_sheet=None,
):
    """Builds the dictionary to be saved in the student_attempts collection."""
    data = {
        "student_id": ObjectId(student_id)
        if ObjectId.is_valid(student_id)
        else student_id,
        "title": title,
        "student_response": student_response,
        "similarity_score": score,
        "classification": classification,
        "feedback": feedback,
        "source": source,
    }
    if keywords:
        data["keywords"] = keywords
    if cheat_sheet:
        data["cheat_sheet"] = cheat_sheet
    return data


# ----------------------------
# AI GRADER ROUTES
# ----------------------------

@app.route('/classify', methods=['POST'])
def classify():
    """
    Runs the MiniLM classification and saves the result.
    API Contract: Expects JSON body:
      {
        "title": "Some note title",
        "student_id": "some_student_id",
        "student_response": "Their answer..."
      }
    """
    try:
        data = request.get_json(force=True) or {}
    except Exception:
        return jsonify({
            "status": "error",
            "message": "Invalid JSON body"
        }), 400

    note_title = data.get("title")
    student_id = data.get("student_id")
    student_response = data.get("student_response")

    # Basic validation
    if not note_title or not student_id or not student_response:
        return jsonify({
            "status": "error",
            "message": "Missing title, student_id, or student_response"
        }), 400

    # 1. FETCH REFERENCE STANDARD FROM MONGO
    try:
        reference_standard = db_fetcher.get_reference_standard(note_title)
    except Exception as e:
        print(f"[ERROR] Failed to fetch reference for '{note_title}': {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to fetch reference standard from database."
        }), 500

    # 2. RUN MINI-LM CLASSIFICATION (placeholder)
    try:
        is_correct, score = classifier.classify_response_on_demand(
            note_title,
            student_response,
            reference_standard,
        )
    except Exception as e:
        print(f"[ERROR] MiniLM classification failed: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal error during classification."
        }), 500

    classification_result = {
        "source": "MiniLM",
        "score": float(f"{score:.4f}"),
        "classification": "CORRECT" if is_correct else "INCORRECT",
        "feedback": f"MiniLM classified with similarity score: {score:.4f}",
    }

    # 3. SAVE RESULT TO MONGO
    try:
        grade_data = prepare_grade_data(
            student_id=student_id,
            title=note_title,
            student_response=student_response,
            score=classification_result["score"],
            classification=classification_result["classification"],
            feedback=classification_result["feedback"],
            source=classification_result["source"],
        )
        db_fetcher.save_grade_result(grade_data)
    except Exception as e:
        print(f"[WARN] Failed to save grade result: {e}")
        # Don't block the response just because saving failed

    return jsonify(classification_result), 200



@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Runs MiniLM and then uses Gemini for detailed analysis and suggestions.
    API Contract: Expects {title, student_id, student_response}
    """
    data = request.get_json()

    note_title = data.get("title")
    student_id = data.get("student_id")
    student_response = data.get("student_response")

    if not note_title or not student_id or not student_response:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Missing title, student_id, or student_response",
                }
            ),
            400,
        )

    reference_standard = db_fetcher.get_reference_standard(note_title)

    is_correct, score = classifier.classify_response_on_demand(
        note_title,
        student_response,
        reference_standard,
    )
    detailed_feedback, keywords, cheat_sheet = gemini_helper.analyze_and_suggest(
    note_title,
    student_response,
    reference_standard,
    score,
)

    final_result = {
    "source": "Gemini",
    "score": float(f"{score:.4f}"),
    "classification": "CORRECT" if is_correct else "INCORRECT",
    "feedback": detailed_feedback,
    "keywords": keywords,       # now: missing concepts
    "cheat_sheet": cheat_sheet  # generated by Gemini
}

    grade_data = prepare_grade_data(
        student_id=student_id,
        title=note_title,
        student_response=student_response,
        score=final_result["score"],
        classification=final_result["classification"],
        feedback=final_result["feedback"],
        source=final_result["source"],
        keywords=final_result.get("keywords"),
        cheat_sheet=final_result.get("cheat_sheet"),
    )
    db_fetcher.save_grade_result(grade_data)

    return jsonify(final_result)


@app.route("/")
def index():
    """Simple placeholder route for the root URL."""
    return jsonify(
        {
            "status": "running",
            "message": "AI Grader API is online. Use /classify or /analyze routes.",
        }
    )


# ----------------------------
# TEST DB ROUTE
# ----------------------------
@app.route("/api/test-db", methods=["GET"])
def test_db():
    try:
        db = get_db()
        collections = db.list_collection_names()
        return {"status": "ok", "collections": collections}, 200
    except Exception as e:
        print("TEST-DB ERROR:", e)
        return {"status": "error", "message": str(e)}, 500


if __name__ == "__main__":
    # Optional: quick DB ping
    try:
        db_fetcher.client.admin.command("ping")
        print(f"Successfully connected to MongoDB database: {MONGO_DB_NAME}")
    except Exception as e:
        print(f"Could not connect to MongoDB. Check MONGO_URI. Error: {e}")

    # Use Waitress in production, binding to Render's PORT on 0.0.0.0
    from waitress import serve
    port = int(os.getenv("PORT", 8080))  # Render sets PORT automatically
    print(f"Starting production WSGI server (Waitress) on http://0.0.0.0:{port}...")
    serve(app, host="0.0.0.0", port=port)


