from fastapi import FastAPI
from schemas import PalmRequest, PalmResponse
from hand_reader import summarize_hand
from ai_baba import generate_prediction

app = FastAPI(title="AI Baba Palm Reader")

@app.post("/predict", response_model=PalmResponse)
def predict(req: PalmRequest):
    # Step 1: read hand (or fake)
    summary = summarize_hand(fake=req.fake)

    # Step 2: generate AI baba prediction
    prediction = generate_prediction(summary)

    return PalmResponse(summary=summary, prediction=prediction)
