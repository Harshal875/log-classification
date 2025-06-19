import os
import re
from dotenv import load_dotenv

load_dotenv()
groq_client = None

def init_groq():
    """Initialize Groq client."""
    global groq_client
    try:
        from groq import Groq
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            groq_client = Groq(api_key=api_key)
            return True
    except Exception as e:
        print(f"Groq initialization failed: {e}")
    return False

def classify_with_llm(log_msg):
    """Classify using LLM."""
    global groq_client
    
    if groq_client is None:
        if not init_groq():
            return "Unclassified"
    
    try:
        prompt = f'''Classify this log message into one category: 
        (1) Workflow Error, (2) Deprecation Warning, or (3) Unclassified.
        Put answer in <category></category> tags.
        
        Log: {log_msg}'''

        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            max_tokens=50
        )

        content = response.choices[0].message.content
        match = re.search(r'<category>(.*?)</category>', content)
        
        if match:
            category = match.group(1).strip()
            if category in ["Workflow Error", "Deprecation Warning"]:
                return category
                
        return "Unclassified"
    except:
        return "Unclassified"