from flask import Blueprint, request, jsonify
import os
import requests

ai_routes = Blueprint("ai_routes", __name__)

HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL_URL = "https://router.huggingface.co/v1/chat/completions"
MODEL_NAME = "moonshotai/Kimi-K2-Thinking:novita"


@ai_routes.route("/generate-questions", methods=["POST"])
def generate_questions():
    try:
        data = request.get_json()
        text = (data or {}).get("text", "").strip()

        if not text:
            return jsonify({"error": "No text provided"}), 400

        print("\n=== NOTES RECEIVED ===")
        print(text[:400])
        print("======================\n")

        headers = {
            "Authorization": f"Bearer {HF_API_KEY}",
            "Content-Type": "application/json",
        }

        # ----------------------------------------------------
        # NEW PROMPT — suppress chain-of-thought completely
        # ----------------------------------------------------
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
        hf_res = requests.post(HF_MODEL_URL, headers=headers, json=payload)
        print("HF status:", hf_res.status_code)

        if hf_res.status_code != 200:
            print("HF ERROR:", hf_res.text[:500])
            return jsonify({
                "error": "HF request failed",
                "status_code": hf_res.status_code,
                "details": hf_res.text,
            }), 500

        out = hf_res.json()
        msg = out["choices"][0]["message"]
        reply = msg.get("content") or msg.get("reasoning_content") or ""

        print("\n--- RAW MODEL OUTPUT ---")
        print(reply)
        print("-------------------------\n")

        # ----------------------------------------------------
        # Extract questions (ANY line ending with "?")
        # ----------------------------------------------------
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

    except Exception as e:
        print("\n!!! ERROR in /generate-questions !!!")
        print(e)
        print("======================================\n")
        return jsonify({"error": str(e)}), 500
