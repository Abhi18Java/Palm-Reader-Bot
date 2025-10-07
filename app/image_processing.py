import cv2
import mediapipe as mp
import numpy as np
import os
from datetime import datetime
from typing import List, Optional, Tuple

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def extract_landmarks(input_image_path: str) -> Tuple[Optional[List], Optional[str]]:
    """
    Detect hand landmarks and draw custom glowing effect on palm.
    Returns:
        - landmarks: list of 21 points (x, y, z)
        - annotated_path: path to saved stylized image
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

        landmarks = results.multi_hand_landmarks[0].landmark
        annotated_img = img.copy()

        # ==== ✨ Custom Visualization ====
        h, w, _ = annotated_img.shape
        pts = []

        for lm in landmarks:
            x, y = int(lm.x * w), int(lm.y * h)
            pts.append((x, y))

        # Draw connecting lines (golden)
        for connection in mp_hands.HAND_CONNECTIONS:
            start, end = connection
            x1, y1 = pts[start]
            x2, y2 = pts[end]
            cv2.line(annotated_img, (x1, y1), (x2, y2), (0, 215, 255), 2, cv2.LINE_AA)
            # Soft glow line
            cv2.line(annotated_img, (x1, y1), (x2, y2), (0, 255, 255), 1, cv2.LINE_AA)

        # Draw glowing landmark dots
        for (x, y) in pts:
            cv2.circle(annotated_img, (x, y), 5, (0, 255, 255), -1)
            cv2.circle(annotated_img, (x, y), 9, (0, 255, 255), 2)
            cv2.circle(annotated_img, (x, y), 12, (0, 180, 255), 1)



        annotated_filename = f"hand_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        annotated_path = os.path.join("images", annotated_filename)
        cv2.imwrite(annotated_path, annotated_img)

        return landmarks, annotated_path
