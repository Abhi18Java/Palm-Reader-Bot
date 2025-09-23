from fastapi import FastAPI
from schemas import PalmRequest, PalmResponse
from hand_reader import summarize_hand
from ai_baba import generate_prediction

app = FastAPI(title="AI Baba Palm Reader")

@app.post("/predict", response_model=PalmResponse)
def predict(req: PalmRequest):
    summary, image_path = summarize_hand()
    
    if summary == "No hand detected":
        prediction = "Please show your hand clearly to the camera"
    else:
        prediction = generate_prediction(summary)
    
    return PalmResponse(summary=summary, prediction=prediction, image_path=image_path)
