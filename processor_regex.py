import re

def classify_with_regex(log_message):
    """Classify using simple regex patterns."""
    patterns = {
        r"User User\d+ logged (in|out)\.": "User Action",
        r"Backup (started|ended|completed successfully)": "System Notification",
        r"System updated to version": "System Notification",
        r"File .* uploaded successfully": "System Notification",
        r"Disk cleanup completed": "System Notification",
        r"System reboot initiated": "System Notification",
        r"Account with ID .* created": "User Action"
    }
    
    for pattern, label in patterns.items():
        if re.search(pattern, log_message):
            return label
    return None