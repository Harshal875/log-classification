import pandas as pd
import os
from processor_regex import classify_with_regex
from processor_bert import classify_with_bert, get_classification_confidence
from processor_llm import classify_with_llm

def classify(logs):
    """Main classification function."""
    labels = []
    for source, log_msg in logs:
        label = classify_log(source, log_msg)
        labels.append(label)
    return labels

def classify_log(source, log_msg):
    """Classify single log using hybrid approach."""
    try:
        # LegacyCRM uses LLM directly
        if source == "LegacyCRM":
            return classify_with_llm(log_msg)
        
        # Try regex first
        regex_result = classify_with_regex(log_msg)
        if regex_result:
            return regex_result
        
        # Try BERT with confidence check
        bert_result, confidence = get_classification_confidence(log_msg)
        if bert_result != "Unclassified" and confidence > 0.7:
            return bert_result
        
        # Fallback to basic BERT
        bert_result = classify_with_bert(log_msg)
        if bert_result != "Unclassified":
            return bert_result
        
        return "Unclassified"
        
    except Exception as e:
        print(f"Classification error: {e}")
        return "Unclassified"

def classify_csv(input_file, output_file=None):
    """Process CSV file."""
    try:
        df = pd.read_csv(input_file)
        
        if "source" not in df.columns or "log_message" not in df.columns:
            raise ValueError("CSV must have 'source' and 'log_message' columns")
        
        logs_data = list(zip(df["source"], df["log_message"]))
        df["target_label"] = classify(logs_data)
        
        if output_file is None:
            output_file = "resources/output.csv"
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        df.to_csv(output_file, index=False)
        
        return output_file
        
    except Exception as e:
        print(f"CSV processing error: {e}")
        raise

# Test function
if __name__ == '__main__':
    # Create sample test data
    test_logs = [
        ("ModernCRM", "User User123 logged in."),
        ("BillingSystem", "Backup completed successfully."),
        ("LegacyCRM", "Feature deprecated in version 3.0"),
        ("AnalyticsEngine", "File uploaded successfully by user Admin")
    ]
    
    print("Testing classification...")
    for source, message in test_logs:
        result = classify_log(source, message)
        print(f"{source}: {message[:30]}... → {result}")