import os
import uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path

from image_processing import extract_landmarks
from feature_extraction import extract_features
from llm_roaster import generate_roast

# --- Config ---
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)

# --- FastAPI app ---
app = FastAPI(title="Savage Baba Palm Reader")

# Allow frontend (React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:3000"],  # set specific domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        # Save uploaded image
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as f:
            f.write(await file.read())

        print("Processing image for landmarks...")
        # FIX: Unpack the tuple returned by extract_landmarks
        landmarks, annotated_path = extract_landmarks(str(file_path))
        print(f"Landmarks detected: {len(landmarks) if landmarks else 0}")
        print(f"Annotated image saved at: {annotated_path}")

        if not landmarks:
            return JSONResponse(
                {"error": "No valid hand landmarks detected."}, status_code=400
            )

        print("Extracting features...")
        features = extract_features(landmarks)
        print("Features:", features)

        print("Generating roast...")
        prediction = generate_roast(features)
        print("Prediction:", prediction)

        return {
            "prediction": prediction,
            "features": features,
            "image_path": str(file_path),
            "annotated_image_path": annotated_path,  # Include annotated image path
        }

    except Exception as e:
        import sys
        import traceback
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(f"Error processing image: {e}")
        print(f"Exception type: {exc_type}")
        print(f"Full traceback:")
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
