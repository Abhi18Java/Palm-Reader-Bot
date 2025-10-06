# D:\AI_Project\hand_reader_ai_baba\app\llm_roaster.py
import os
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv
from vector_db import query_db

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- System Prompt (role definition) ---
SYSTEM_PROMPT = """
You are 'Savage Baba', ek witty aur sarcastic palm reader jo palmistry ke gyaan ko 
roast-style me sunata hai. 

🎭 Style Rules:
- Hinglish me likho (desi mix of Hindi + English).
- Har feature/meaning ke liye ek savage line do.
- Har line = ulta tareef + turant roast, jo crowd ko hasaye.
- Lines logically connected rahe, random topics jump mat karo.
- Sirf palmistry ke meanings use karo (vector DB se aaye). Apna khud ka meaning kabhi mat banana, jo bhi meaning banao vo savage or sarcastic hona chahiye.
- No labels like "Summary:" or "Roast:" – bas straight savage output.
- Max 2 lines, tightly roastfull aur insightful.
- Boring words jaise "balanced", "average", "confused" avoid karo.
"""



def generate_roast(features: Dict[str, str]) -> str:
    """
    Given palm features and their labels, fetch meanings from DB
    and create a roast-style prediction.
    """
    # Step 1: Convert features into text queries
    queries = [f"{k}: {v}" for k, v in features.items() if v]

    # Step 2: Fetch relevant palmistry meanings
    retrieved_meanings = query_db(queries, top_k=2)

    if not retrieved_meanings:
        return "Baba kuch samajh nahi paaye, haath dhang se dikhaiye! 😏"

    # Step 3: Construct prompt
    feature_text = "\n".join([f"- {k}: {v}" for k, v in features.items()])
    meaning_text = "\n".join([f"- {m}" for m in retrieved_meanings])

    user_prompt = f"""
Palm Features Detected:
{feature_text}

Palmistry Meanings from Knowledge Base:
{meaning_text}

Now, roast the person in witty Hinglish style while keeping meaning intact.
"""

    # Step 4: Call OpenAI
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.8,
    )

    return response.choices[0].message.content.strip()
