import os
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

KB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "kb.json"))

class KBSearchEngine:
    def __init__(self):
        self.kb_data = []
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = None
        self.load_kb()

    def load_kb(self):
        """Loads and indexes the knowledge base from kb.json."""
        if not os.path.exists(KB_PATH):
            print(f"Warning: Knowledge base file not found at {KB_PATH}")
            return
        
        try:
            with open(KB_PATH, "r", encoding="utf-8") as f:
                self.kb_data = json.load(f)
            
            # Extract questions to fit TF-IDF
            questions = [item["question"] for item in self.kb_data]
            if questions:
                self.tfidf_matrix = self.vectorizer.fit_transform(questions)
        except Exception as e:
            print(f"Error loading or parsing kb.json: {e}")

    def query(self, user_query, threshold=0.15):
        """
        Queries the knowledge base for the closest matching question.
        Parameters:
            user_query (str): The search query from the user.
            threshold (float): Minimum cosine similarity to match a Q&A.
            
        Returns:
            dict: The matching Q&A block + matching similarity score, or a fallback suggestion.
        """
        if not self.kb_data or self.tfidf_matrix is None:
            return {
                "found": False,
                "answer": "Sorry, the knowledge base is currently empty or has not been initialized.",
                "confidence": 0.0
            }
        
        # Transform the user query
        query_vector = self.vectorizer.transform([user_query])
        
        # Compute cosine similarities
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        # Get the index of the highest similarity score
        best_match_idx = int(np.argmax(similarities))
        best_score = float(similarities[best_match_idx])
        
        if best_score >= threshold:
            match = self.kb_data[best_match_idx]
            return {
                "found": True,
                "question": match["question"],
                "answer": match["answer"],
                "tags": match["tags"],
                "confidence": round(best_score * 100, 1)
            }
        
        # Fallback recommendations if no good match is found
        all_topics = [item["question"] for item in self.kb_data]
        return {
            "found": False,
            "answer": "I couldn't find a direct answer to your question in my database. Try asking about topics like:\n\n" + 
                      "\n".join([f"- {q}" for q in all_topics[:5]]) + "\n- Or check your spelling and try again!",
            "confidence": round(best_score * 100, 1)
        }

# Instantiate a single engine instance to be imported elsewhere
kb_engine = KBSearchEngine()

if __name__ == "__main__":
    # Test query
    print("Testing KBSearchEngine...")
    test_queries = ["What is phishing?", "tell me about fake websites", "how to secure my password?"]
    for q in test_queries:
        res = kb_engine.query(q)
        print(f"\nQuery: '{q}' (Confidence: {res['confidence']}%)\nAnswer: {res['answer'][:150]}...")
