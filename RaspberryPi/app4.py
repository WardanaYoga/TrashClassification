from flask import Flask, Response, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import tensorflow as tf
import threading

app = Flask(__name__)
CORS(app)

# ===============================
# Load CNN model
# ===============================
model = tf.keras.models.load_model("modelv5.h5")
labels = ['cardboard','glass', 'metal', 'organic', 'paper', 'plastic']

# ===============================
# Kamera
# ===============================
cap = cv2.VideoCapture(0)

latest_result = {
    "label": "Inisialisasi",
    "confidence": 0.0
}

lock = threading.Lock()

def inference_loop():
    global latest_result
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        img = cv2.resize(frame, (224, 224))
        img = img.astype("float32") / 255.0
        img = np.expand_dims(img, axis=0)

        preds = model.predict(img, verbose=0)
        idx = int(np.argmax(preds))
        conf = float(preds[0][idx])

        with lock:
            latest_result = {
                "label": labels[idx],
                "confidence": conf
            }

def generate_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        with lock:
            label = latest_result["label"]
            conf = latest_result["confidence"]

        cv2.putText(frame,
            f"{label} {conf*100:.1f}%",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,255,0), 2)

        ret, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()

        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

@app.route("/video")
def video():
    return Response(generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/label")
def label():
    with lock:
        return jsonify(latest_result)

if __name__ == "__main__":
    t = threading.Thread(target=inference_loop, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=5000)
