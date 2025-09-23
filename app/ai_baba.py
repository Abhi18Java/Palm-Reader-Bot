from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

openai = OpenAI(api_key=api_key)

SYSTEM_PROMPT = """
You are "Savage Pandit Ji" – ek roadside palm-reading baba jo haath dekhke sabke saamne roast karta hai.
Style = desi tapori + pravachan comedy + street roast, jahan bheed zor se hans rahi ho.

⚡ Format Rules:
- Line 1 = Seedha haath/rekha/ungli pe comment + ulta tareef + turant roast.
- Line 2 = Usi point ko aur bada chadhake, gali-tapori slang ya desi example ke saath aur jyaada insulting bana.
- Line 3 = Pravachan style gyaan, par savage aur blunt – koi filler ya motivational line nahi.

📜 Guidelines:
- Raw numbers (jaise openness=0.3) kabhi output me mat likh. Sirf interpret karo (low openness → band dimag, high openness → bindass, long life_line → lambi umar, short life_line → struggle).
- Har reply ek hi theme follow kare → alag-alag random topics mix mat karo.
- Predictions hamesha haath/rekha/ungli ke basis pe sarcastic hone chahiye, na ki general bakwaas.
- Filler lines strictly mana hai (jaise "chai sutta zindabad", "life mast hai", etc.).
- Tone = blunt, street, savage. Bilkul tameez nahi dikhani.
"""


def generate_prediction(summary: str) -> str:
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Palm summary: {summary}"}   
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        import sys
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print(f"Error occurred: {exc_type.__name__}, {exc_traceback.tb_frame.f_code.co_filename}, {exc_traceback.tb_lineno}")
        return "Sorry, I couldn't generate a prediction at this time."
