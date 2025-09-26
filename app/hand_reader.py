# app/hand_reader.py
import cv2
import mediapipe as mp
import numpy as np
import os
from datetime import datetime

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# keep your helpers (count_extended_fingers, palm_openness, approx_life_line_length)
def count_extended_fingers(landmarks, img_h, img_w):
    tips = [4, 8, 12, 16, 20]
    pips = [3, 6, 10, 14, 18]
    count = 0
    for tip, pip in zip(tips, pips):
        # thumb logic uses x-coordinates (depends on image flip/orientation)
        if tip == 4:
            if landmarks[tip].x < landmarks[pip].x:
                count += 1
        else:
            if landmarks[tip].y < landmarks[pip].y:
                count += 1
    return count

def palm_openness(landmarks):
    wrist = [landmarks[0].x, landmarks[0].y]
    mcp_idxs = [5, 9, 13, 17]
    dists = [np.linalg.norm(np.array(wrist) - np.array([landmarks[i].x, landmarks[i].y])) for i in mcp_idxs]
    return float(np.mean(dists))

def approx_life_line_length(landmarks):
    a = [landmarks[0].x, landmarks[0].y]
    b = [landmarks[9].x, landmarks[9].y]
    return float(np.linalg.norm(np.array(a) - np.array(b)))

def process_hand_image(input_image_path: str):
    """
    Read an image from disk, process with MediaPipe hands,
    save an annotated image in images/ and return (summary, image_path).
    If no hand detected -> ("No hand detected", None)
    """
    os.makedirs("images", exist_ok=True)

    img = cv2.imread(input_image_path)
    if img is None:
        return "Invalid image", None

    with mp_hands.Hands(static_image_mode=True, max_num_hands=1) as hands:
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if not results.multi_hand_landmarks:
            return "No hand detected", None

        # We have landmarks for the first hand
        landmarks = results.multi_hand_landmarks[0].landmark
        img_h, img_w, _ = img.shape
        fingers = count_extended_fingers(landmarks, img_h, img_w)
        openness = palm_openness(landmarks)
        life_len = approx_life_line_length(landmarks)

        summary = f"{fingers} fingers, openness={openness:.3f}, life_line={life_len:.3f}"

        # draw landmarks on copy
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        annotated_filename = f"hand_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        annotated_path = os.path.join("images", annotated_filename)
        cv2.imwrite(annotated_path, img)

        # return summary and relative path (frontend will do http://HOST/{image_path})
        return summary, annotated_path
