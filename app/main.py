# app/main.py
import os
import logging
from datetime import datetime
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from schemas import PalmResponse
from hand_reader import process_hand_image
from ai_baba import generate_prediction  # your existing file

logger = logging.getLogger("uvicorn.error")

app = FastAPI(title="Palm Reader API")

# allow your frontend origin(s)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:3000"],  # change if needed
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# ensure directories exist
os.makedirs("images", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

# serve images (annotated) at /images/*
app.mount("/images", StaticFiles(directory="images"), name="images")


@app.post("/predict", response_model=PalmResponse)
async def predict(file: UploadFile = File(...)):
    """
    Expects a multipart/form-data upload (key: file).
    Frontend should send the captured image as FormData.append('file', blob, 'hand.jpg')
    """
    try:
        # save incoming upload
        contents = await file.read()
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        upload_filename = f"uploads/hand_upload_{ts}.jpg"
        with open(upload_filename, "wb") as f:
            f.write(contents)

        # process uploaded image (mediapipe + draw landmarks) -> returns summary, annotated_path
        summary, annotated_path = process_hand_image(upload_filename)

        if summary == "No hand detected":
            prediction_text = "Please show your hand clearly to the camera"
        elif summary in ("Invalid image", None):
            prediction_text = "Invalid image"
        else:
            # call your AI to generate the funny/savage prediction
            try:
                prediction_text = generate_prediction(summary)
            except Exception as e:
                logger.exception("AI generation failed")
                prediction_text = "⚠️ Could not generate prediction right now."

        return PalmResponse(summary=summary, prediction=prediction_text, image_path=annotated_path)
    except Exception as exc:
        logger.exception("Error in /predict")
        return PalmResponse(summary="Error", prediction=str(exc), image_path=None)
