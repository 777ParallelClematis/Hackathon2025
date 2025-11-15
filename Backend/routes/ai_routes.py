from flask import Blueprint, request, jsonify
import os
import requests

ai_routes = Blueprint("ai_routes", __name__)

HF_API_KEY = os.getenv("HF_API_KEY")

print("\n=== HF TOKEN LOADED ===")
print("HF_API_KEY:", repr(HF_API_KEY))
print("=======================\n")

# HF Router (OpenAI-style)
HF_MODEL_URL = "https://router.huggingface.co/v1/chat/completions"

# Working router-compatible model
MODEL_NAME = "moonshotai/Kimi-K2-Thinking:novita"

print("=== HF ROUTER CONFIG ===")
print("Endpoint:", HF_MODEL_URL)
print("Model:", MODEL_NAME)
print("========================\n")


@ai_routes.route("/generate-questions", methods=["POST"])
def generate_questions():
    print("\n========== /generate-questions CALLED ==========")

    try:
        # STEP 1 — Read body
        print("--- STEP 1: Read request body ---")
        data = request.get_json()
        print("Incoming JSON:", data)

        text = (data or {}).get("text", "").strip()
        print("Extracted text length:", len(text))

        if not text:
            return jsonify({"error": "No text provided"}), 400

        # STEP 2 — Headers
        print("\n--- STEP 2: Build headers ---")
        headers = {
            "Authorization": f"Bearer {HF_API_KEY}",
            "Content-Type": "application/json",
        }

        # STEP 3 — Payload
        print("\n--- STEP 3: Build payload ---")
        prompt = (
    "Read the following notes and generate two sets of questions:\n"
    "1. **Questions for the lecturer** – clarifications the student should ask in class.\n"
    "2. **Questions for future learning** – deeper follow-up questions for revision.\n\n"
    "Requirements:\n"
    "- Base the questions ONLY on the provided notes.\n"
    "- Provide EXACTLY 3 questions in each category.\n"
    "- Do NOT explain your reasoning.\n"
    "- Do NOT include chain-of-thought.\n"
    "- Output ONLY the final questions in the correct format.\n"
    "- Format EXACTLY as written below:\n"
    "Questions for the lecturer:\n"
    "- Q1\n- Q2\n- Q3\n\n"
    "Questions for future learning:\n"
    "- Q1\n- Q2\n- Q3\n\n"
    f"NOTES:\n{text}"
)


        payload = {
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 350,
            "temperature": 0.3
        }

        print("Payload OK:", str(payload)[:200], "...")

        # STEP 4 — Send request
        print("\n--- STEP 4: Send request ---")
        print("POST", HF_MODEL_URL)

        hf_res = requests.post(HF_MODEL_URL, headers=headers, json=payload)

        # STEP 5 — Log response
        print("\n--- HF RESPONSE ---")
        print("Status:", hf_res.status_code)
        print("Body:", hf_res.text[:400])
        print("----------------------------")

        if hf_res.status_code != 200:
            return jsonify({
                "error": "HF request failed",
                "status_code": hf_res.status_code,
                "details": hf_res.text
            }), 500

        # STEP 6 — Parse JSON
        print("\n--- STEP 6: Parse JSON ---")
        out = hf_res.json()

        msg = out["choices"][0]["message"]

        # Use content OR reasoning_content (Kimi outputs reasoning_content)
        reply = (
            msg.get("content")
            or msg.get("reasoning_content")
            or ""
        )

        print("Extracted reply:", reply[:200], "...")

        # STEP 7 — Extract questions (line by line)
        print("\n--- STEP 7: Split questions ---")
        questions = [
            q.strip().lstrip("-•0123456789. ").strip()
            for q in reply.split("\n")
            if q.strip()
        ]

        print("Parsed questions:", questions)

        print("\n========== COMPLETE ==========\n")
        return jsonify({"questions": questions}), 200

    except Exception as e:
        print("\n!!! FATAL ERROR IN AI ROUTE !!!")
        print("Exception:", e)
        print("=================================\n")
        return jsonify({"error": str(e)}), 500
