import cv2
import mediapipe as mp
import numpy as np
import os
from datetime import datetime
from typing import List, Optional, Tuple

# Initialize mediapipe solutions
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def extract_landmarks(input_image_path: str) -> Tuple[Optional[List], Optional[str]]:
    """
    Process an image, detect hand landmarks, and return:
    - landmarks: list of 21 hand landmark points (x, y, z)
    - annotated_path: path to saved image with landmarks drawn

    Returns (None, None) if no hand detected or invalid image.
    """
    os.makedirs("images", exist_ok=True)

    img = cv2.imread(input_image_path)
    if img is None:
        return None, None

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    with mp_hands.Hands(
        static_image_mode=True,
        max_num_hands=1,
        min_detection_confidence=0.6
    ) as hands:

        results = hands.process(img_rgb)

        if not results.multi_hand_landmarks:
            return None, None

        # Only first detected hand
        landmarks = results.multi_hand_landmarks[0].landmark

        # Draw landmarks for visualization
        annotated_img = img.copy()
        mp_drawing.draw_landmarks(
            annotated_img,
            results.multi_hand_landmarks[0],
            mp_hands.HAND_CONNECTIONS
        )

        annotated_filename = f"hand_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        annotated_path = os.path.join("images", annotated_filename)
        cv2.imwrite(annotated_path, annotated_img)

        return landmarks, annotated_path
