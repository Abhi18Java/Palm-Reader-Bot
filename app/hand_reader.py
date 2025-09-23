import cv2
import mediapipe as mp
import numpy as np
import random

mp_hands = mp.solutions.hands

def count_extended_fingers(landmarks, img_h, img_w):
    tips = [4, 8, 12, 16, 20]
    pips = [3, 6, 10, 14, 18]
    count = 0
    for tip, pip in zip(tips, pips):
        if tip == 4:  # thumb
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

def summarize_hand(fake=False):
    if fake:
        fingers = random.randint(0, 5)
        openness = random.uniform(0.05, 0.18)
        life_len = random.uniform(0.1, 0.22)
        return f"Fake hand: {fingers} fingers, openness={openness:.3f}, life_line={life_len:.3f}"

    cap = cv2.VideoCapture(0)  # Access webcam to capture hand images
    with mp_hands.Hands(max_num_hands=1) as hands:
        ret, frame = cap.read()
        if not ret:
            cap.release()
            return "Fake hand: 3 fingers, openness=0.111, life_line=0.200"  # fallback

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)
        cap.release()

        if not results.multi_hand_landmarks:
            fingers = random.randint(1, 5)
            openness = random.uniform(0.1, 0.9)
            life_len = random.uniform(0.2, 0.8)
            return f"Fake hand (no detection): {fingers} fingers, openness={openness:.3f}, life_line={life_len:.3f}"

        landmarks = results.multi_hand_landmarks[0].landmark
        img_h, img_w, _ = frame.shape
        fingers = count_extended_fingers(landmarks, img_h, img_w)
        openness = palm_openness(landmarks)
        life_len = approx_life_line_length(landmarks)

        return f"{fingers} fingers, openness={openness:.3f}, life_line={life_len:.3f}"
