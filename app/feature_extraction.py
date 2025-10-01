import math
from typing import List, Dict
from mediapipe.framework.formats import landmark_pb2


def distance(a, b):
    """Euclidean distance between 2 normalized points."""
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)


def is_finger_extended(tip, pip, wrist):
    """
    Check if a finger is extended:
    - If fingertip is farther from wrist than its middle joint.
    """
    return distance(tip, wrist) > distance(pip, wrist)


def count_extended_fingers(landmarks: List[landmark_pb2.NormalizedLandmark]) -> int:
    """Count how many fingers are extended (ignoring thumb for now)."""
    finger_tips = [8, 12, 16, 20]  # Index, Middle, Ring, Pinky
    finger_pips = [6, 10, 14, 18]
    
    if len(landmarks) != 21:
        print("Insufficient landmarks to count fingers.")
        return 0

    try:
        wrist = landmarks[0]
        extended = 0

        for tip, pip in zip(finger_tips, finger_pips):
            if is_finger_extended(landmarks[tip], landmarks[pip], wrist):
                extended += 1

        # Thumb: check horizontally (simplified rule)
        if landmarks[4].x < landmarks[3].x:  # right hand assumption
            extended += 1

        return extended
    except Exception as e:
        import sys
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(f"Error counting fingers: {e}")
        return 0

def palm_openness(landmarks: List[landmark_pb2.NormalizedLandmark]) -> float:
    """
    Approx openness of palm: distance between index base (5) and pinky base (17).
    """
    return distance(landmarks[5], landmarks[17])


def life_line_length(landmarks: List[landmark_pb2.NormalizedLandmark]) -> float:
    """
    Approx "life line" length (wrist → index base).
    Palmistry approximation (not exact).
    """
    wrist = landmarks[0]
    index_base = landmarks[5]
    return distance(wrist, index_base)


def extract_features(landmarks: List[landmark_pb2.NormalizedLandmark]) -> Dict:
    """
    Convert 21 landmarks into meaningful palm features.
    Returns dict with numeric + categorical descriptors.
    """
    features = {}

    # 1. Finger count
    fingers = count_extended_fingers(landmarks)
    features["fingers"] = fingers

    # 2. Palm openness
    openness = palm_openness(landmarks)
    features["openness"] = round(openness, 3)

    # 3. Life line
    ll = life_line_length(landmarks)
    features["life_line"] = round(ll, 3)

    # 4. Interpretive labels (for knowledge base retrieval)
    if fingers <= 2:
        features["fingers_label"] = "kam fingers, secretive"
    elif fingers <= 4:
        features["fingers_label"] = "average fingers, balanced"
    else:
        features["fingers_label"] = "full open hand, open-minded"

    features["openness_label"] = "high openness" if openness > 0.2 else "low openness"
    features["life_line_label"] = (
        "long life line" if ll > 0.1 else "short life line"
    )

    return features
