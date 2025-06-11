# from dotenv import load_dotenv
# from groq import Groq
# import json
# import re


# load_dotenv()

# groq = Groq()

# def classify_with_llm(log_msg):
#     """
#     Generate a variant of the input sentence. For example,
#     If input sentence is "User session timed out unexpectedly, user ID: 9250.",
#     variant would be "Session timed out for user 9251"
#     """
#     prompt = f'''Classify the log message into one of these categories: 
#     (1) Workflow Error, (2) Deprecation Warning.
#     If you can't figure out a category, use "Unclassified".
#     Put the category inside <category> </category> tags. 
#     Log message: {log_msg}'''

#     chat_completion = groq.chat.completions.create(
#         messages=[{"role": "user", "content": prompt}],
#         # model="llama-3.3-70b-versatile",
#         model="llama-3.3-70b-versatile",
#         temperature=0.5
#     )

#     content = chat_completion.choices[0].message.content
#     match = re.search(r'<category>(.*)<\/category>', content, flags=re.DOTALL)
#     category = "Unclassified"
#     if match:
#         category = match.group(1)

#     return category


# if __name__ == "__main__":
#     print(classify_with_llm(
#         "Case escalation for ticket ID 7324 failed because the assigned support agent is no longer active."))
#     print(classify_with_llm(
#         "The 'ReportGenerator' module will be retired in version 4.0. Please migrate to the 'AdvancedAnalyticsSuite' by Dec 2025"))
#     print(classify_with_llm("System reboot initiated by user 12345."))

from dotenv import load_dotenv
from groq import Groq
import json
import re
import os

load_dotenv()

# Initialize Groq client with explicit API key
groq = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def classify_with_llm(log_msg):
    """
    Classify the log message into predefined categories for LegacyCRM logs.
    Uses LLM for complex pattern recognition when regex and BERT are insufficient.
    """
    try:
        prompt = f'''Classify the log message into one of these categories: 
        (1) Workflow Error, (2) Deprecation Warning.
        If you can't figure out a category, use "Unclassified".
        Put the category inside <category> </category> tags. 
        Log message: {log_msg}'''

        chat_completion = groq.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.1,  # Lower temperature for more consistent results
            max_tokens=100    # Limit tokens for efficiency
        )

        content = chat_completion.choices[0].message.content
        match = re.search(r'<category>(.*?)<\/category>', content, flags=re.DOTALL)
        category = "Unclassified"
        if match:
            category = match.group(1).strip()

        return category

    except Exception as e:
        print(f"Error in LLM classification: {e}")
        return "Unclassified"


if __name__ == "__main__":
    # Test cases
    test_messages = [
        "Case escalation for ticket ID 7324 failed because the assigned support agent is no longer active.",
        "The 'ReportGenerator' module will be retired in version 4.0. Please migrate to the 'AdvancedAnalyticsSuite' by Dec 2025",
        "System reboot initiated by user 12345."
    ]
    
    for msg in test_messages:
        result = classify_with_llm(msg)
        print(f"Message: {msg}")
        print(f"Classification: {result}")
        print("-" * 50)