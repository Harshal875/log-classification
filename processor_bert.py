import joblib
import os
import numpy as np

model_embedding = None
model_classification = None

def load_models():
    """Load BERT models."""
    global model_embedding, model_classification
    try:
        from sentence_transformers import SentenceTransformer
        model_embedding = SentenceTransformer('all-MiniLM-L6-v2')
        
        model_path = "models/log_classifier.joblib"
        if os.path.exists(model_path):
            model_classification = joblib.load(model_path)
        else:
            print("BERT model not found. Training required.")
    except Exception as e:
        print(f"Error loading BERT models: {e}")

def classify_with_bert(log_message):
    """Classify using BERT."""
    global model_embedding, model_classification
    
    if model_embedding is None:
        load_models()
    
    if model_embedding is None or model_classification is None:
        return "Unclassified"
    
    try:
        embeddings = model_embedding.encode([log_message])
        probabilities = model_classification.predict_proba(embeddings)[0]
        
        if np.max(probabilities) < 0.5:
            return "Unclassified"
            
        return model_classification.predict(embeddings)[0]
    except:
        return "Unclassified"

def get_classification_confidence(log_message):
    """Get classification with confidence."""
    global model_embedding, model_classification
    
    if model_embedding is None:
        load_models()
    
    if model_embedding is None or model_classification is None:
        return "Unclassified", 0.0
    
    try:
        embeddings = model_embedding.encode([log_message])
        probabilities = model_classification.predict_proba(embeddings)[0]
        confidence = np.max(probabilities)
        
        if confidence < 0.5:
            return "Unclassified", confidence
            
        label = model_classification.predict(embeddings)[0]
        return label, confidence
    except:
        return "Unclassified", 0.0