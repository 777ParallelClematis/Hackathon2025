from flask import Blueprint, request, jsonify
import os
import requests
import re

from middleware.auth import require_auth
from middleware.rate_limit import limiter

# Validation
from validation.ai_schemas import AIQuestionSchema
from validation import validate_json

ai_routes = Blueprint("ai_routes", __name__)

HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL_URL = "https://router.huggingface.co/v1/chat/completions"
MODEL_NAME = "google/gemma-2-2b-it"




@ai_routes.route("/generate-questions", methods=["POST"])
@limiter.limit("10 per minute")
@require_auth
def generate_questions():
    try:
        data = request.get_json() or {}

        # -------------------------
        # Validate input
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
        print("=====================================\n")

        headers = {
            "Authorization": f"Bearer {HF_API_KEY}",
            "Content-Type": "application/json",
        }

        # -------------------------
        # Prompt – keep it simple, but we will
        # strip any reasoning on our side anyway.
        # -------------------------
        prompt = (
            "Read the following notes and produce exactly three specific learning questions.\n"
            "Each question MUST end with a question mark.\n"
            "Write only the three questions, one per line.\n\n"
            f"NOTES:\n{text}\n\n"
            "First question:"
        )

        payload = {
            "model": MODEL_NAME,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 200,
            "temperature": 0.2,
        }

        print("--- Sending request to HuggingFace Router ---")
        hf_res = requests.post(HF_MODEL_URL, headers=headers, json=payload, timeout=30)
        print("HF status:", hf_res.status_code)

        if hf_res.status_code != 200:
            try:
                err = hf_res.json()
            except Exception:
                err = hf_res.text

            print("\n--- HF ERROR FULL ---")
            print(err)
            print("---------------------\n")

            return jsonify({
                "error": "HF request failed",
                "status_code": hf_res.status_code,
                "details": err,
            }), 500

        out = hf_res.json()

        print("\n--- HF RAW JSON ---")
        print(out)
        print("--------------------\n")

        choice = out.get("choices", [{}])[0]
        msg = choice.get("message", {})

        # ==========================================================
        # "Reasoning disabled":
        # - Ignore reasoning_content entirely.
        # - Only trust message["content"] and then strip reasoning-like text.
        # ==========================================================
        raw_content = (msg.get("content") or "").strip()

        print("\n--- RAW MODEL OUTPUT (content only) ---")
        print(raw_content)
        print("---------------------------------------\n")

        blob = raw_content.replace("\n", " ")

        # ----------------------------------------------------------
        # Sentence-level split: split at '?', then re-attach '?'
        # This avoids gluing long meta text + first question together.
        # ----------------------------------------------------------
        segments = [seg.strip() for seg in re.split(r"\?", blob) if seg.strip()]

        candidates = []
        for seg in segments:
            sentence = (seg + "?").strip()

            # Drop obvious chain-of-thought / meta sentences
            lowered = sentence.lower()
            if any(
                phrase in lowered
                for phrase in [
                    "the user wants me",
                    "i should",
                    "i need to",
                    "constraints are",
                    "possible questions",
                    "let me",
                    "i will now",
                    "step by step",
                ]
            ):
                continue

            cleaned = sentence.lstrip("-•–*1234567890.)(").strip()
            candidates.append(cleaned)

        questions = candidates[:3]

        # ----------------------------------------------------------
        # Fallback – generic, domain-neutral
        # ----------------------------------------------------------
        if len(questions) != 3:
            print("!!! FALLBACK TRIGGERED !!! (Model returned < 3 clean questions)")
            questions = [
                "What are the main ideas presented in these notes?",
                "Which concepts in these notes are still unclear or need further explanation?",
                "How do the ideas in these notes connect to other topics you have studied?"
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
