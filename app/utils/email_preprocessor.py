import re
import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

# Standard list of English stopwords to avoid NLTK download dependency issues in runtime
STOPWORDS = {
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", 
    "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", 
    "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", 
    "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", 
    "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", 
    "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", 
    "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", 
    "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", 
    "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", 
    "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", 
    "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", 
    "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"
}

def clean_text(text):
    """
    Cleans raw email text: lowercasing, removing special characters/numbers,
    tokenizing, and removing stop words.
    """
    if not isinstance(text, str):
        text = ""
    # Lowercase
    text = text.lower()
    # Remove HTML tags if any
    text = re.sub(r"<[^>]*>", " ", text)
    # Keep only letters
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    # Tokenize by whitespace
    tokens = text.split()
    # Filter stopwords and short tokens
    cleaned = [t for t in tokens if t not in STOPWORDS and len(t) > 1]
    return " ".join(cleaned)

class EmailPreprocessor:
    def __init__(self, max_features=3000, vectorizer_path=None):
        self.max_features = max_features
        self.vectorizer_path = vectorizer_path
        if vectorizer_path and os.path.exists(vectorizer_path):
            self.vectorizer = joblib.load(vectorizer_path)
        else:
            self.vectorizer = TfidfVectorizer(max_features=self.max_features)

    def fit_transform(self, texts):
        """
        Fits the vectorizer on the input texts after cleaning, and returns the TF-IDF matrix.
        """
        cleaned_texts = [clean_text(t) for t in texts]
        return self.vectorizer.fit_transform(cleaned_texts)

    def transform(self, texts):
        """
        Transforms texts using the fitted vectorizer.
        """
        cleaned_texts = [clean_text(t) for t in texts]
        return self.vectorizer.transform(cleaned_texts)

    def save_vectorizer(self, path):
        """
        Saves the fitted vectorizer to the specified path.
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self.vectorizer, path)
        print(f"Saved TF-IDF vectorizer to {path}")

# Run simple test when executed directly
if __name__ == "__main__":
    test_texts = [
        "Free entry in 2 a wkly comp to win FA Cup final tkts! Text FA to 87121",
        "Hello, how are you? Are we still meeting for lunch today?"
    ]
    preprocessor = EmailPreprocessor(max_features=100)
    features = preprocessor.fit_transform(test_texts)
    print("Features matrix shape:", features.shape)
    print("Cleaned text 1:", clean_text(test_texts[0]))
