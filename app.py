import streamlit as st
import cv2
import numpy as np
import easyocr
from datetime import datetime

st.set_page_config(page_title="Expiry Detector", layout="wide")

# EasyOCR reader
reader = easyocr.Reader(['en'])

def extract_date(text):
    import re
    patterns = [
        r"\b\d{2}/\d{2}/\d{4}\b",
        r"\b\d{2}-\d{2}-\d{4}\b",
        r"\b\d{2}/\d{2}/\d{2}\b",
        r"\b\d{2}-\d{2}-\d{2}\b"
    ]
    for p in patterns:
        match = re.search(p, text)
        if match:
            return match.group()
    return None

def check_expiry(date_str):
    try:
        if len(date_str.split("/")[-1]) == 2:
            date_str = date_str[:6] + "20" + date_str[-2:]

        exp = datetime.strptime(date_str, "%d/%m/%Y")
        today = datetime.now()

        if exp >= today:
            return "✔ SAFE TO CONSUME", "green"
        else:
            return "❌ EXPIRED", "red"

    except:
        return None, None


st.title("📅 Real-Time Expiry Date Detector")

st.write("Use your **mobile camera** or **laptop webcam** to scan expiry date.")


run_cam = st.checkbox("Start Camera")

if run_cam:
    FRAME_WINDOW = st.image([])
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            st.write("Camera not working.")
            break

        # Resize for better speed
        small = cv2.resize(frame, (640, 480))

        # OCR detect
        results = reader.readtext(small)

        detected_date = None

        for (bbox, text, prob) in results:
            date_found = extract_date(text)
            if date_found:
                detected_date = date_found
                # Draw rectangle
                pts = np.array(bbox).astype(int)
                cv2.polylines(small, [pts], True, (0,255,0), 2)
                cv2.putText(
                    small,
                    date_found,
                    (pts[0][0], pts[0][1]-10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0,255,0),
                    2
                )

        if detected_date:
            status, color = check_expiry(detected_date)
            if status:
                cv2.putText(small, status, (20, 450),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                            (0,255,0) if color=="green" else (0,0,255),
                            3)

        FRAME_WINDOW.image(small, channels="BGR")

    cap.release()
