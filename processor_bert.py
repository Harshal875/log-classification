# import joblib
# from sentence_transformers import SentenceTransformer

# model_embedding = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight embedding model
# model_classification = joblib.load("models/log_classifier.joblib")


# def classify_with_bert(log_message):
#     embeddings = model_embedding.encode([log_message])
#     probabilities = model_classification.predict_proba(embeddings)[0]
#     if max(probabilities) < 0.5:
#         return "Unclassified"
#     predicted_label = model_classification.predict(embeddings)[0]
    
#     return predicted_label


# if __name__ == "__main__":
#     logs = [
#         "alpha.osapi_compute.wsgi.server - 12.10.11.1 - API returned 404 not found error",
#         "GET /v2/3454/servers/detail HTTP/1.1 RCODE   404 len: 1583 time: 0.1878400",
#         "System crashed due to drivers errors when restarting the server",
#         "Hey bro, chill ya!",
#         "Multiple login failures occurred on user 6454 account",
#         "Server A790 was restarted unexpectedly during the process of data transfer"
#     ]
#     for log in logs:
#         label = classify_with_bert(log)
#         print(log, "->", label)



import joblib
import os
from sentence_transformers import SentenceTransformer
import numpy as np

# Load models with error handling
try:
    model_embedding = SentenceTransformer('all-MiniLM-L6-v2')
    model_path = os.path.join("models", "log_classifier.joblib")
    
    if os.path.exists(model_path):
        model_classification = joblib.load(model_path)
    else:
        raise FileNotFoundError(f"Model file not found at {model_path}")
        
except Exception as e:
    print(f"Error loading models: {e}")
    model_embedding = None
    model_classification = None


def classify_with_bert(log_message):
    """
    Classify log messages using BERT embeddings and logistic regression.
    Returns classification with confidence threshold.
    """
    if model_embedding is None or model_classification is None:
        print("Models not loaded properly")
        return "Unclassified"
    
    try:
        # Generate embeddings
        embeddings = model_embedding.encode([log_message])
        
        # Get predictions and probabilities
        probabilities = model_classification.predict_proba(embeddings)[0]
        max_probability = np.max(probabilities)
        
        # Apply confidence threshold
        if max_probability < 0.5:
            return "Unclassified"
            
        predicted_label = model_classification.predict(embeddings)[0]
        return predicted_label
        
    except Exception as e:
        print(f"Error in BERT classification: {e}")
        return "Unclassified"


def get_classification_confidence(log_message):
    """
    Get classification with confidence score.
    """
    if model_embedding is None or model_classification is None:
        return "Unclassified", 0.0
    
    try:
        embeddings = model_embedding.encode([log_message])
        probabilities = model_classification.predict_proba(embeddings)[0]
        max_probability = np.max(probabilities)
        
        if max_probability < 0.5:
            return "Unclassified", max_probability
            
        predicted_label = model_classification.predict(embeddings)[0]
        return predicted_label, max_probability
        
    except Exception as e:
        print(f"Error in classification: {e}")
        return "Unclassified", 0.0


if __name__ == "__main__":
    test_logs = [
        "alpha.osapi_compute.wsgi.server - 12.10.11.1 - API returned 404 not found error",
        "GET /v2/3454/servers/detail HTTP/1.1 RCODE   404 len: 1583 time: 0.1878400",
        "System crashed due to drivers errors when restarting the server",
        "Hey bro, chill ya!",
        "Multiple login failures occurred on user 6454 account",
        "Server A790 was restarted unexpectedly during the process of data transfer"
    ]
    
    for log in test_logs:
        label, confidence = get_classification_confidence(log)
        print(f"Log: {log}")
        print(f"Classification: {label} (Confidence: {confidence:.2f})")
        print("-" * 80)