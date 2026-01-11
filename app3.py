from flask import Flask, Response, jsonify
from flask_cors import CORS
import cv2
import time
from threading import Thread, Lock

app = Flask(__name__)
CORS(app)

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
if not cap.isOpened():
    raise RuntimeError("Kamera tidak bisa dibuka")

latest_frame = None
latest_label = "Menunggu"
latest_confidence = 0.0
lock = Lock()

def klasifikasi_dummy(frame):
    t = int(time.time()) % 3
    if t == 0:
        return "Organik", 0.92
    elif t == 1:
        return "Anorganik", 0.88
    else:
        return "B3", 0.85
def camera_loop():
    global latest_frame, latest_label, latest_confidence
    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.1)
            continue

        label, conf = klasifikasi_dummy(frame)
        with lock:
            latest_frame = frame.copy()
            latest_label = label
            latest_confidence = conf

Thread(target=camera_loop, daemon=True).start()
def generate_frames():
    while True:
        with lock:
            if latest_frame is None:
                continue
            frame = latest_frame.copy()

        _, buffer = cv2.imencode(".jpg", frame)
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
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False
    )
