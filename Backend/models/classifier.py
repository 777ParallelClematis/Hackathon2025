# models/classifier.py (Only the class structure is needed, logic is the same)
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from config import MINILM_MODEL_NAME, SIMILARITY_THRESHOLD
import numpy as np
import torch 

class MiniLMClassifier:
    
    def __init__(self, reference_answers: dict):
        self.model = SentenceTransformer(MINILM_MODEL_NAME)

    def classify_response_on_demand(self, prompt: str, user_response: str, reference_standard: str) -> tuple[bool, float]:
        """
        Calculates the similarity between the user's response and the 
        dynamically provided reference standard.
        """
        device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
        
        # ... (Embedding and similarity calculation logic remains the same) ...
        response_embedding = self.model.encode(user_response, convert_to_tensor=True, device=device)
        ref_embedding = self.model.encode(reference_standard, convert_to_tensor=True, device=device)
        
        similarity_score = cosine_similarity(
            response_embedding.cpu().numpy().reshape(1, -1),
            ref_embedding.cpu().numpy().reshape(1, -1)
        )[0][0]
        
        is_correct = similarity_score >= SIMILARITY_THRESHOLD
        
        return is_correct, float(similarity_score)

    def needs_llm_help(self, similarity_score: float) -> bool:
        confusion_band = 0.05
        return abs(similarity_score - SIMILARITY_THRESHOLD) < confusion_band