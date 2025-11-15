# models/llm_helper.py
from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL
import json

class GeminiHelper:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set in config.")
        self.client = genai.Client(api_key=GEMINI_API_KEY)

    def analyze_response(self, prompt: str, user_response: str, context: str) -> str:
        """
        Asks Gemini to analyze the user's response against the prompt and context 
        for classification (CORRECT/INCORRECT/PARTIALLY_CORRECT).
        """
        system_prompt = (
            "You are an expert educational grader. Your task is to analyze a user's "
            "response to a prompt and classify it as 'CORRECT', 'INCORRECT', or 'PARTIALLY_CORRECT' "
            "based on the provided context. Then, provide a brief, supportive explanation for the classification. "
            "Do NOT answer the question. Only critique the provided response. "
            "Format your response as a JSON object: {'classification': '...', 'feedback': '...'}"
        )

        user_content = (
            f"--- CONTEXT FOR GRADING ---\n{context}\n"
            f"--- END CONTEXT ---\n\n"
            f"Prompt: {prompt}\n"
            f"User Response: {user_response}"
        )

        try:
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=user_content,
                config={
                    "system_instruction": system_prompt,
                    "response_mime_type": "application/json",
                    "response_schema": {
                        "type": "object",
                        "properties": {
                            "classification": {"type": "string"},
                            "feedback": {"type": "string"}
                        },
                        "required": ["classification", "feedback"]
                    }
                }
            )
            return response.text
        except Exception as e:
            return f"{{\"classification\": \"ERROR\", \"feedback\": \"LLM Call Failed: {e}\"}}"

    def analyze_long_response(self, prompt: str, user_response: str, context: str) -> str:
        """
        Analyzes a response to extract keywords, identify weak spots, 
        and create a cheat sheet using the provided context.
        """
        system_prompt = (
            "You are an expert educational reviewer specializing in identifying gaps in student knowledge. "
            "Your task is to analyze the student's response against the provided context. "
            "You must output a single JSON object containing three fields: 'keywords', 'weak_spots', and 'cheat_sheet'. "
            "Keywords should be 5-10 technical terms used or missed (comma-separated). "
            "Weak spots should be 2-3 brief sentences identifying where the student lacked detail or made errors. "
            "The cheat sheet must be 3-5 concise, bulleted facts to help the student review."
        )

        user_content = (
            f"--- CONTEXT FOR GRADING ---\n{context}\n"
            f"--- END CONTEXT ---\n\n"
            f"Prompt: {prompt}\n"
            f"Student's response for deep analysis: {user_response}"
        )

        try:
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=user_content,
                config={
                    "system_instruction": system_prompt,
                    "response_mime_type": "application/json",
                    "response_schema": {
                        "type": "object",
                        "properties": {
                            "keywords": {"type": "string"},
                            "weak_spots": {"type": "string"},
                            "cheat_sheet": {"type": "string"}
                        },
                        "required": ["keywords", "weak_spots", "cheat_sheet"]
                    }
                }
            )
            return response.text
        except Exception as e:
            return f"{{\"keywords\": \"ERROR\", \"weak_spots\": \"LLM Call Failed: {e}\", \"cheat_sheet\": \"\"}}"