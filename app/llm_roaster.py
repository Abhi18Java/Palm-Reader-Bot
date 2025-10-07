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
- Write in flowing paragraphs, NOT bullet points or markup formatting.
- NO asterisks, dashes, colons, or special formatting - just natural sentences.
- Create 2-3 small paragraphs with smooth transitions between thoughts.
- Infuse humor, sarcasm, and playful teasing in conversational style.
- Every reading must feel personal based on hand features and their meanings.
- Adapt humor tone to user gender: use "baccha" if gender inferred, else gender-neutral.
- Combine insight + roast naturally in paragraph form.
- Avoid generic adjectives and stay connected to palmistry meanings.
- Write like you're talking face-to-face, not making a list or report.
- ALWAYS end with complete sentences and proper closure - never leave responses hanging mid-sentence or incomplete thoughts.
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

Generate a complete palm reading roast with real palmistry insights. Make sure to end with a proper conclusion and complete thought.
"""

    # Step 5: Generate roast from OpenAI
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=500
    )

    result = response.choices[0].message.content.strip()
    
    # Ensure complete sentence ending
    if not result.endswith(('.', '!', '?', '😏', '😂', '🤣')):
        # Find last complete sentence
        sentences = result.split('.')
        if len(sentences) > 1:
            result = '.'.join(sentences[:-1]) + '.'
        else:
            result += ' Bas itna hi samjh gaye Baba! 😏'
    
    return result