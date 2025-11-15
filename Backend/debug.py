import requests
from config import GEMINI_API_KEY

URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

prompt = "Say 'hello from Gemini' and give 2 bullet points about queues in data structures."

payload = {
    "contents": [
        {"parts": [{"text": prompt}]}
    ]
}

resp = requests.post(f"{URL}?key={GEMINI_API_KEY}", json=payload, timeout=30)

print("HTTP status:", resp.status_code)
print("Body:\n", resp.text[:2000])
