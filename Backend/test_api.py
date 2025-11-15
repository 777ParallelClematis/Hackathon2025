import requests

BASE_URL = "http://127.0.0.1:8080"  # or 5000, whatever your app is using


def test_analyze():
    payload = {
        "title": "Queues short answer",
        "student_id": "student_123",
        "student_response": "A queue is a linear data structure that follows FIFO.",
        # extra fields if your /analyze route uses them:
        "notes": "The Queue is a fundamental, linear Abstract Data Type (ADT) that adheres to FIFO.",
        "reference_text": "Example teacher explanation or lecture text if your backend uses it.",
    }
    r = requests.post(f"{BASE_URL}/analyze", json=payload)
    print("ANALYZE Status:", r.status_code)
    print("ANALYZE Response:", r.json())


def test_classify():
    payload = {
        "title": "Queues",
        "student_id": "student_123",
        "student_response": "A queue is a linear data structure that follows FIFO.",
    }
    r = requests.post(f"{BASE_URL}/classify", json=payload)
    print("CLASSIFY Status:", r.status_code)
    print("CLASSIFY Response:", r.json())


if __name__ == "__main__":
    test_analyze()
    test_classify()
