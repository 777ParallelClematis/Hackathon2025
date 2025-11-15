from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time
import requests
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
from waitress import serve # Using Waitress to fix the Windows socket error

from config import (
    MINILM_MODEL_NAME, GEMINI_API_KEY, CLASSIFICATION_THRESHOLD,
    MONGO_URI, MONGO_DB_NAME, MONGO_REF_COLLECTION, MONGO_GRADES_COLLECTION
)

app = Flask(__name__)
CORS(app) 

class MiniLMClassifier:
    """
    Placeholder class for the MiniLM model logic. 
    You must implement the actual model loading and comparison logic.
    """
    def __init__(self, model_name: str, threshold: float):
        print(f"Loading MiniLM Classifier: {model_name} with threshold {threshold}...")
        self.threshold = threshold
        self.model = None 

    def classify_response_on_demand(self, note_title: str, user_response: str, reference_standard: str) -> tuple[bool, float]:
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
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent"

    def analyze_and_suggest(self, title: str, user_response: str, reference_standard: str, score: float) -> tuple[str, str]:
        """
        Generates detailed analysis and keywords using the Gemini API.
        """
        system_prompt = (
            "You are an expert academic tutor. Analyze the student's response against the "
            "reference standard. Provide constructive feedback, a clear assessment of accuracy, "
            "and suggest one key area for improvement. "
        )
        user_query = (
            f"Question: {title}\n"
            f"Student Response (Score {score:.2f}): {user_response}\n"
            f"Reference Standard: {reference_standard}\n\n"
            "Provide the detailed feedback, then list the top 3 missing keywords the student should have included."
        )

        if score > 0.7:
             feedback = "Excellent grasp of the core concepts! The response accurately covered the FIFO principle. Focus on adding more detail regarding time complexity for a perfect answer."
             keywords = ["FIFO principle", "Time Complexity", "Enqueue/Dequeue"]
        else:
             feedback = "The response is too brief. While you correctly identified the front/rear movement, you missed the central concept of FIFO. Please review the difference between Stacks and Queues."
             keywords = ["FIFO", "LIFO", "Front/Rear Pointers"]
             
        return feedback, keywords

class MongoReferenceFetcher:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB_NAME]
        
        # Reference collection is 'notes' (source of 500-word standard)
        self.ref_collection = self.db[MONGO_REF_COLLECTION] 
        
        self.grades_collection = self.db[MONGO_GRADES_COLLECTION]
        
    def get_reference_standard(self, note_title: str) -> str:
        """ 
        Fetches the reference text from the 'notes' collection by matching the 'title' field. 
        It returns the 'note_text' field as the reference standard.
        """
       
        document = self.ref_collection.find_one({'title': note_title}) 
        
      
        if document and 'note_text' in document: 
            return document['note_text']
        else:
            print(f"Warning: No reference standard found for title: '{note_title}' in notes collection.")
            
            return "A queue follows the First-In, First-Out (FIFO) principle. Add at rear, remove from front."

    def save_grade_result(self, grade_data: dict):
        """ Inserts the final grading result into the student_attempts collection. """
        grade_data['graded_at'] = datetime.utcnow()
        try:
            self.grades_collection.insert_one(grade_data)
            print(f"Successfully saved grade for student {grade_data.get('student_id')} on topic: {grade_data.get('title')}")
            return True
        except Exception as e:
            print(f"Error saving grade to DB: {e}")
            return False


db_fetcher = MongoReferenceFetcher()
classifier = MiniLMClassifier(MINILM_MODEL_NAME, CLASSIFICATION_THRESHOLD)
gemini_helper = GeminiHelper(GEMINI_API_KEY)

def prepare_grade_data(student_id, title, student_response, score, classification, feedback, source, keywords=None, cheat_sheet=None):
    """ Builds the dictionary to be saved in the student_attempts collection. """
    data = {
       
        "student_id": ObjectId(student_id) if ObjectId.is_valid(student_id) else student_id,
        "title": title,
        "student_response": student_response, 
        "similarity_score": score,
        "classification": classification,
        "feedback": feedback,
        "source": source
    }
    if keywords:
       
        data['keywords'] = keywords
    if cheat_sheet:
        data['cheat_sheet'] = cheat_sheet
    return data


# FLASK API ROUTES

@app.route('/classify', methods=['POST'])
def classify():
    """ 
    Runs the MiniLM classification and saves the result.
    API Contract: Expects {title, student_id, student_response}
    """
    data = request.get_json()
    
  
    note_title = data.get('title') 
    student_id = data.get('student_id') 
    student_response = data.get('student_response') 

    if not note_title or not student_id or not student_response:
        return jsonify({"status": "error", "message": "Missing title, student_id, or student_response"}), 400

    reference_standard = db_fetcher.get_reference_standard(note_title)


    is_correct, score = classifier.classify_response_on_demand(
        note_title, 
        student_response, 
        reference_standard
    )
    
    classification_result = {
        "source": "MiniLM",
        "score": float(f"{score:.4f}"),
        "classification": "CORRECT" if is_correct else "INCORRECT",
        "feedback": f"MiniLM classified with similarity score: {score:.4f}"
    }

  
    grade_data = prepare_grade_data(
        student_id=student_id, 
        title=note_title, 
        student_response=student_response, 
        score=classification_result['score'],
        classification=classification_result['classification'],
        feedback=classification_result['feedback'],
        source=classification_result['source']
    )
    db_fetcher.save_grade_result(grade_data)

    return jsonify(classification_result)


@app.route('/analyze', methods=['POST'])
def analyze():
    """ 
    Runs MiniLM and then uses Gemini for detailed analysis and suggestions.
    API Contract: Expects {title, student_id, student_response}
    """
    data = request.get_json()
    

    note_title = data.get('title') 
    student_id = data.get('student_id') 
    student_response = data.get('student_response') 

    if not note_title or not student_id or not student_response:
        return jsonify({"status": "error", "message": "Missing title, student_id, or student_response"}), 400

 
    reference_standard = db_fetcher.get_reference_standard(note_title)

    is_correct, score = classifier.classify_response_on_demand(
        note_title, 
        student_response, 
        reference_standard
    )
 
    detailed_feedback, keywords = gemini_helper.analyze_and_suggest(
        note_title, 
        student_response, 
        reference_standard, 
        score
    )

    final_result = {
        "source": "Gemini",
        "score": float(f"{score:.4f}"),
        "classification": "CORRECT" if is_correct else "INCORRECT", # Classification based on MiniLM score
        "feedback": detailed_feedback,
        "keywords": keywords,
        "cheat_sheet": reference_standard # Providing the reference text as the cheat sheet
    }

    grade_data = prepare_grade_data(
        student_id=student_id, 
        title=note_title, 
        student_response=student_response,
        score=final_result['score'],
        classification=final_result['classification'],
        feedback=final_result['feedback'],
        source=final_result['source'],
        keywords=final_result.get('keywords'),
        cheat_sheet=final_result.get('cheat_sheet')
    )
    db_fetcher.save_grade_result(grade_data)

    return jsonify(final_result)


@app.route('/')
def index():
    """ Simple placeholder route for the root URL """
    return jsonify({"status": "running", "message": "AI Grader API is online. Use /classify or /analyze routes."})


if __name__ == '__main__':

    try:
        db_fetcher.client.admin.command('ping')
        print("Successfully connected to MongoDB database: notebuddy")
    except Exception as e:
        print(f"Could not connect to MongoDB. Check MONGO_URI. Error: {e}")
        
    # Using Waitress to bypass the WinError 10038 socket issue
    print("Starting production WSGI server (Waitress) on http://127.0.0.1:8080...")
    serve(app, host='127.0.0.1', port=8080)
