import requests

BASE_URL = "http://127.0.0.1:8080"  # or 5000, whatever your app is using


def test_analyze():
    payload = {
        "title": "Photosynthesis",
        "student_id": "6917bd98cebcd5150c57529d",
        "student_response": "Photosynthesis is how plants make their food using sunlight. They take in carbon dioxide and water and turn it into sugar. The sunlight provides the energy to make this happen. Oxygen is produced during this process and released into the air. Plants do this mainly in their leaves where chlorophyll absorbs the light. The process is important because it gives us oxygen and helps plants grow.",
        # extra fields if your /analyze route uses them:
        #"notes": "The Queue is a fundamental, linear Abstract Data Type (ADT) that adheres to FIFO.",
        #"reference_text": "Example teacher explanation or lecture text if your backend uses it.",
    }
    r = requests.post(f"{BASE_URL}/analyze", json=payload)
    print("ANALYZE Status:", r.status_code)
    print("ANALYZE Response:", r.json())


def test_classify():
    payload = {
        "title": "Photosynthesis",
        "student_id": "6917bd98cebcd5150c57529d",
        "student_response": "Photosynthesis is how plants make their food using sunlight. They take in carbon dioxide and water and turn it into sugar. The sunlight provides the energy to make this happen. Oxygen is produced during this process and released into the air. Plants do this mainly in their leaves where chlorophyll absorbs the light. The process is important because it gives us oxygen and helps plants grow.",
    }
    r = requests.post(f"{BASE_URL}/classify", json=payload)
    print("CLASSIFY Status:", r.status_code)
    print("CLASSIFY Response:", r.json())


if __name__ == "__main__":
    test_analyze()
    test_classify()
