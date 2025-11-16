from flask import Blueprint, request, jsonify
import os
import requests
import json # Import json for cleaner logging of dicts/JSON
import traceback # Import traceback for better error logging

from middleware.auth import require_auth
from middleware.rate_limit import limiter

# Validation
from validation.ai_schemas import AIQuestionSchema
from validation import validate_json

ai_routes = Blueprint("ai_routes", __name__)

HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL_URL = "https://router.huggingface.co/v1/chat/completions"
MODEL_NAME = os.getenv("MODEL_NAME")


@ai_routes.route("/api/ai/generate-questions", methods=["POST", "OPTIONS"])
@limiter.limit("10 per minute") 	 # <--- Rate limiting added
@require_auth 	                     # <--- Must remain AFTER limiter
def generate_questions():
    try:
        data = request.get_json() or {}

        # -------------------------
        # DEBUG STEP 1: Log incoming request data
        # -------------------------
        print("\n--- INCOMING REQUEST DATA ---")
        # Use json.dumps for clean printing of Python dictionary
        print(json.dumps(data, indent=2))
        print("---------------------------\n")

        # -------------------------
        # Server-side validation
        # -------------------------
        schema = AIQuestionSchema()
        error = validate_json(schema, data)
        if error:
            print(f"VALIDATION ERROR: {error.json}")
            return error

        text = data["text"].strip()

        if not text:
            return jsonify({"error": "Text must not be empty"}), 400

        # -------------------------
        # DEBUG STEP 2: Log received notes
        # -------------------------
        print("\n=== NOTES RECEIVED ===")
        print(text[:400]) # Print first 400 characters for brevity
        print(f"Text length: {len(text)}")
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

        # -------------------------
        # DEBUG STEP 3: Log the full request payload sent to HuggingFace
        # -------------------------
        print("\n--- HUGGINGFACE REQUEST PAYLOAD ---")
        print(json.dumps(payload, indent=2))
        print("-----------------------------------\n")

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
        
        # -------------------------
        # DEBUG STEP 4: Log the full raw response JSON
        # -------------------------
        print("\n--- RAW HUGGINGFACE RESPONSE (JSON) ---")
        print(json.dumps(out, indent=2))
        print("---------------------------------------\n")
        
        msg = out.get("choices", [{}])[0].get("message", {})
        reply = msg.get("content") or msg.get("reasoning_content") or ""

        # -------------------------
        # DEBUG STEP 5: Log the extracted text (the AI's reply)
        # -------------------------
        print("\n--- RAW MODEL OUTPUT (Content) ---")
        print(reply)
        print(f"Reply length: {len(reply)}")
        print("---------------------------------\n")

        questions = []
        
        # -------------------------
        # DEBUG STEP 6: Log question parsing details
        # -------------------------
        print("--- STARTING QUESTION PARSING ---")
        for i, line in enumerate(reply.split("\n")):
            clean = line.strip()
            print(f"Line {i+1}: Raw: '{line}' -> Stripped: '{clean}'")
            if clean.endswith("?"):
                # Clean prefix numbers/bullets and whitespace
                # This ensures we get the question text without leading bullets/numbers
                clean = clean.lstrip("-•–1234567890. ").strip()
                print(f"  -> VALIDATED & CLEANED: '{clean}'")
                questions.append(clean)
            else:
                print("  -> SKIPPED (Line does not end with '?')")

        questions = questions[:3]

        if len(questions) < 3:
            # -------------------------
            # DEBUG STEP 7: Log fallback usage
            # -------------------------
            print(f"!!! FALLBACK USED !!! Only {len(questions)} questions extracted. Defaulting to safe questions.")
            questions = [
                "What deeper relationships exist between supply, demand, and price changes?",
                "How do market shifts influence the stability of equilibrium?",
                "What factors determine how consumers and producers respond to price changes?"
            ]
        
        # -------------------------
        # DEBUG STEP 8: Log final output
        # -------------------------
        print("\n--- FINAL QUESTIONS SENT TO CLIENT ---")
        print(questions)
        print("--------------------------------------\n")

        return jsonify({"questions": questions}), 200

    except requests.exceptions.Timeout:
        # Log Timeout error
        print("\n!!! ERROR: AI Request Timed Out !!!\n")
        return jsonify({"error": "AI request timed out"}), 504

    except Exception as e:
        # Log comprehensive internal server error trace
        print("\n!!! INTERNAL SERVER ERROR in /generate-questions !!!")
        print(traceback.format_exc())
        print("==================================================\n")
        return jsonify({"error": "Internal server error"}), 500