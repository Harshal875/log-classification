# from processor_regex import classify_with_regex
# from processor_bert import classify_with_bert
# from processor_llm import classify_with_llm

# def classify(logs):
#     labels = []
#     for source, log_msg in logs:
#         label = classify_log(source, log_msg)
#         labels.append(label)
#     return labels


# def classify_log(source, log_msg):
#     if source == "LegacyCRM":
#         label = classify_with_llm(log_msg)
#     else:
#         label = classify_with_regex(log_msg)
#         if not label:
#             label = classify_with_bert(log_msg)
#     return label

# def classify_csv(input_file):
#     import pandas as pd
#     df = pd.read_csv(input_file)

#     # Perform classification
#     df["target_label"] = classify(list(zip(df["source"], df["log_message"])))

#     # Save the modified file
#     output_file = "output.csv"
#     df.to_csv(output_file, index=False)

#     return output_file

# if __name__ == '__main__':
#     classify_csv("test.csv")
#     # logs = [
#     #     ("ModernCRM", "IP 192.168.133.114 blocked due to potential attack"),
#     #     ("BillingSystem", "User 12345 logged in."),
#     #     ("AnalyticsEngine", "File data_6957.csv uploaded successfully by user User265."),
#     #     ("AnalyticsEngine", "Backup completed successfully."),
#     #     ("ModernHR", "GET /v2/54fadb412c4e40cdbaed9335e4c35a9e/servers/detail HTTP/1.1 RCODE  200 len: 1583 time: 0.1878400"),
#     #     ("ModernHR", "Admin access escalation detected for user 9429"),
#     #     ("LegacyCRM", "Case escalation for ticket ID 7324 failed because the assigned support agent is no longer active."),
#     #     ("LegacyCRM", "Invoice generation process aborted for order ID 8910 due to invalid tax calculation module."),
#     #     ("LegacyCRM", "The 'BulkEmailSender' feature is no longer supported. Use 'EmailCampaignManager' for improved functionality."),
#     #     ("LegacyCRM", " The 'ReportGenerator' module will be retired in version 4.0. Please migrate to the 'AdvancedAnalyticsSuite' by Dec 2025")
#     # ]
#     # labels = classify(logs)
#     #
#     # for log, label in zip(logs, labels):
#     #     print(log[0], "->", label)


from processor_regex import classify_with_regex
from processor_bert import classify_with_bert, get_classification_confidence
from processor_llm import classify_with_llm
import pandas as pd
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def classify(logs):
    """
    Classify a list of logs using the hybrid approach.
    
    Args:
        logs: List of tuples (source, log_message)
    
    Returns:
        List of classified labels
    """
    labels = []
    stats = {
        'regex': 0,
        'bert': 0, 
        'llm': 0,
        'unclassified': 0
    }
    
    for source, log_msg in logs:
        label, method = classify_log_with_method(source, log_msg)
        labels.append(label)
        stats[method] += 1
    
    logger.info(f"Classification stats: {stats}")
    return labels


def classify_log_with_method(source, log_msg):
    """
    Classify a single log message and return both label and method used.
    
    Args:
        source: Source system of the log
        log_msg: Log message content
    
    Returns:
        Tuple of (label, method_used)
    """
    try:
        if source == "LegacyCRM":
            # For LegacyCRM, use LLM directly
            label = classify_with_llm(log_msg)
            return label, 'llm'
        else:
            # First try regex classification
            label = classify_with_regex(log_msg)
            if label:
                return label, 'regex'
            
            # If regex fails, try BERT with confidence
            bert_label, confidence = get_classification_confidence(log_msg)
            if bert_label != "Unclassified" and confidence > 0.7:
                return bert_label, 'bert'
            
            # Fallback to basic BERT classification
            label = classify_with_bert(log_msg)
            if label != "Unclassified":
                return label, 'bert'
            
            return "Unclassified", 'unclassified'
            
    except Exception as e:
        logger.error(f"Error classifying log: {e}")
        return "Unclassified", 'unclassified'


def classify_log(source, log_msg):
    """
    Original classify_log function for backward compatibility.
    """
    label, _ = classify_log_with_method(source, log_msg)
    return label


def classify_csv(input_file, output_file=None):
    """
    Classify logs from a CSV file and save results.
    
    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file (optional)
    
    Returns:
        Path to output file
    """
    try:
        # Read CSV
        df = pd.read_csv(input_file)
        
        # Validate required columns
        if "source" not in df.columns or "log_message" not in df.columns:
            raise ValueError("CSV must contain 'source' and 'log_message' columns")
        
        logger.info(f"Processing {len(df)} log entries from {input_file}")
        
        # Perform classification
        logs_data = list(zip(df["source"], df["log_message"]))
        df["target_label"] = classify(logs_data)
        
        # Set output file path
        if output_file is None:
            output_file = "output.csv"
        
        # Save results
        df.to_csv(output_file, index=False)
        logger.info(f"Results saved to {output_file}")
        
        return output_file
        
    except Exception as e:
        logger.error(f"Error processing CSV: {e}")
        raise


def get_classification_stats(logs):
    """
    Get detailed statistics about classification methods used.
    
    Args:
        logs: List of tuples (source, log_message)
    
    Returns:
        Dictionary with classification statistics
    """
    stats = {
        'total': len(logs),
        'regex': 0,
        'bert': 0,
        'llm': 0,
        'unclassified': 0,
        'by_source': {}
    }
    
    for source, log_msg in logs:
        label, method = classify_log_with_method(source, log_msg)
        stats[method] += 1
        
        if source not in stats['by_source']:
            stats['by_source'][source] = {'regex': 0, 'bert': 0, 'llm': 0, 'unclassified': 0}
        stats['by_source'][source][method] += 1
    
    return stats


if __name__ == '__main__':
    # Test with sample data
    test_logs = [
        ("ModernCRM", "IP 192.168.133.114 blocked due to potential attack"),
        ("BillingSystem", "User User12345 logged in."),
        ("AnalyticsEngine", "File data_6957.csv uploaded successfully by user User265."),
        ("AnalyticsEngine", "Backup completed successfully."),
        ("ModernHR", "GET /v2/54fadb412c4e40cdbaed9335e4c35a9e/servers/detail HTTP/1.1 RCODE  200 len: 1583 time: 0.1878400"),
        ("ModernHR", "Admin access escalation detected for user 9429"),
        ("LegacyCRM", "Case escalation for ticket ID 7324 failed because the assigned support agent is no longer active."),
        ("LegacyCRM", "Invoice generation process aborted for order ID 8910 due to invalid tax calculation module."),
        ("LegacyCRM", "The 'BulkEmailSender' feature is no longer supported. Use 'EmailCampaignManager' for improved functionality."),
        ("LegacyCRM", "The 'ReportGenerator' module will be retired in version 4.0. Please migrate to the 'AdvancedAnalyticsSuite' by Dec 2025")
    ]
    
    print("Testing hybrid classification system...")
    print("=" * 80)
    
    # Get detailed stats
    stats = get_classification_stats(test_logs)
    print(f"Classification Statistics:")
    print(f"Total logs: {stats['total']}")
    print(f"Regex: {stats['regex']}")
    print(f"BERT: {stats['bert']}")
    print(f"LLM: {stats['llm']}")
    print(f"Unclassified: {stats['unclassified']}")
    print("\nBy Source:")
    for source, source_stats in stats['by_source'].items():
        print(f"  {source}: {source_stats}")
    
    print("\n" + "=" * 80)
    print("Individual Classifications:")
    
    # Classify each log
    for source, log_msg in test_logs:
        label, method = classify_log_with_method(source, log_msg)
        print(f"Source: {source}")
        print(f"Message: {log_msg[:60]}{'...' if len(log_msg) > 60 else ''}")
        print(f"Label: {label} (Method: {method})")
        print("-" * 80)
    
    # Test CSV processing if test.csv exists
    try:
        output_file = classify_csv("test.csv")
        print(f"\nCSV processing completed. Output saved to: {output_file}")
    except FileNotFoundError:
        print("\ntest.csv not found, skipping CSV test")
    except Exception as e:
        print(f"\nError processing CSV: {e}")