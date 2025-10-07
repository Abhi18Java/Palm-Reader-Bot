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
You are 'Savage Baba' — a witty, sarcastic, yet insightful palm reader.
You mix real palmistry wisdom with hilarious roasting.

🎭 Style Rules:
- Speak like a mystical desi baba with a funny twist — "beta/beti" tone, not "bhai".
- Use natural Hinglish (90% Hindi + 10% English).
- Every reading must feel **personal** based on hand features and their meanings.
- No repetition of stamina/fingers in every response — comment only if feature appears.
- Adapt humor tone to user gender: use "beta" or "beti" if gender inferred, else gender-neutral.
- Combine insight + roast. Example: “Dil bada hai beta, par logic itna chhota ki emotions ke bharose zindagi chala rahe ho!”
- Avoid generic adjectives (average, balanced, okayish).
- Stay strictly connected to palmistry meanings (don’t invent random traits).
- Each point = 1-2 tight, savage, humorous lines — no summaries.
"""


def generate_roast(features: Dict[str, str], gender: str = None) -> str:
    """
    Generate a witty roast-based palm reading based on detected features.
    """
    # Step 1: Convert features to text queries
    queries = [f"{k}: {v}" for k, v in features.items() if v]

    # Step 2: Fetch meanings
    retrieved_meanings = query_db(queries, top_k=2)
    if not retrieved_meanings:
        return "Baba kuch samajh nahi paaye beta, haath camera ke samne dhang se dikhaiye! 😏"

    # Step 3: Add gender context
    gender_context = ""
    if gender:
        gender_context = f"User gender: {gender}. Use suitable words like beta/beti accordingly."

    # Step 4: Build dynamic user prompt
    feature_text = "\n".join([f"- {k}: {v}" for k, v in features.items()])
    meaning_text = "\n".join([f"- {m}" for m in retrieved_meanings])

    user_prompt = f"""
{gender_context}

Palm Features Detected:
{feature_text}

Palmistry Meanings (from Knowledge Base):
{meaning_text}

Now generate a unique palm reading roast with real palmistry insights.
"""

    # Step 5: Generate roast from OpenAI
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.9,
        max_tokens=300
    )

    return response.choices[0].message.content.strip()