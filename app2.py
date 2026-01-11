from flask import Flask, Response, jsonify
from flask_cors import CORS
import cv2
import time
from threading import Thread
import sys
print("PYTHON USED:", sys.executable)


app = Flask(__name__)
CORS(app, resources={r"/label": {"origins": "*"}})
cap = cv2.VideoCapture(0)
latest_frame = None
latest_label = "Menunggu"
latest_confidence = 0.0

def camera_loop():
    global latest_frame, latest_label, latest_confidence

    while True:
        success, frame = cap.read()
        if not success:
            time.sleep(0.1)
            continue

        latest_frame = frame
        latest_label, latest_confidence = klasifikasi_dummy(frame)

Thread(target=camera_loop, daemon=True).start()

def generate_frames():
    global latest_frame

    while True:
        if latest_frame is None:
            time.sleep(0.05)
            continue

        _, buffer = cv2.imencode(".jpg", latest_frame)
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" +
               buffer.tobytes() + b"\r\n")

@app.route("/video")
def video():
    return Response(generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/label")
def label():
    return jsonify({
        "label": latest_label,
        "confidence": latest_confidence
    })
