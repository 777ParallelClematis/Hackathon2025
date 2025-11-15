from flask import Blueprint, request, jsonify
import os
import requests

from middleware.auth import require_auth
from middleware.rate_limit import limiter

# Validation
from validation.ai_schemas import AIQuestionSchema
from validation import validate_json

ai_routes = Blueprint("ai_routes", __name__)

HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL_URL = "https://router.huggingface.co/v1/chat/completions"
MODEL_NAME = "moonshotai/Kimi-K2-Thinking:novita"


@ai_routes.route("/generate-questions", methods=["POST"])
@limiter.limit("10 per minute")     # <--- Rate limiting added
@require_auth                       # <--- Must remain AFTER limiter
def generate_questions():
    try:
        data = request.get_json() or {}

        # -------------------------
        # Server-side validation
        # -------------------------
        schema = AIQuestionSchema()
        error = validate_json(schema, data)
        if error:
            return error

        text = data["text"].strip()

        if not text:
            return jsonify({"error": "Text must not be empty"}), 400

        print("\n=== NOTES RECEIVED ===")
        print(text[:400])
        print("======================\n")

        headers = {
            "Authorization": f"Bearer {HF_API_KEY}",
            "Content-Type": "application/json",
        }

        # -------------------------
        # Construct safe prompt
        # -------------------------
        prompt = (
            "Read the following notes and immediately produce three specific learning questions.\n"
            "DO NOT think step by step. DO NOT analyze the notes. DO NOT explain your reasoning.\n"
            "Begin your reply with the first question. Each question must end with a question mark.\n"
            "Write only the three questions, each on its own line.\n\n"
            f"NOTES:\n{text}\n\n"
            "First question:"
        )

        payload = {
            "model": MODEL_NAME,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 150,
            "temperature": 0.7,
        }

        print("--- Sending request to HuggingFace Router ---")
        hf_res = requests.post(HF_MODEL_URL, headers=headers, json=payload, timeout=30)
        print("HF status:", hf_res.status_code)

        if hf_res.status_code != 200:
            try:
                err = hf_res.json()
            except Exception:
                err = hf_res.text

            print("HF ERROR:", str(err)[:500])
            return jsonify({
                "error": "HF request failed",
                "status_code": hf_res.status_code,
                "details": err,
            }), 500

        out = hf_res.json()
        msg = out.get("choices", [{}])[0].get("message", {})
        reply = msg.get("content") or msg.get("reasoning_content") or ""

        print("\n--- RAW MODEL OUTPUT ---")
        print(reply)
        print("-------------------------\n")

        questions = []
        for line in reply.split("\n"):
            clean = line.strip()
            if clean.endswith("?"):
                clean = clean.lstrip("-•–1234567890. ").strip()
                questions.append(clean)

        questions = questions[:3]

        if len(questions) < 3:
            print("!!! FALLBACK USED !!!")
            questions = [
                "What deeper relationships exist between supply, demand, and price changes?",
                "How do market shifts influence the stability of equilibrium?",
                "What factors determine how consumers and producers respond to price changes?"
            ]

        print("Final questions:", questions)

        return jsonify({"questions": questions}), 200

    except requests.exceptions.Timeout:
        return jsonify({"error": "AI request timed out"}), 504

    except Exception as e:
        print("\n!!! ERROR in /generate-questions !!!")
        print(e)
        print("======================================\n")
        return jsonify({"error": "Internal server error"}), 500
