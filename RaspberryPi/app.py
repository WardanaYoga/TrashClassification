from flask import Flask, Response, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import tensorflow as tf
import threading
import time
import serial

# ===============================
# Flask
# ===============================
app = Flask(__name__)
CORS(app)

# ===============================
# Load CNN model
# ===============================
model = tf.keras.models.load_model("modelv5.h5")
labels = ['cardboard','glass','metal','organic','paper','plastic']

# ===============================
# Parameter Sistem
# ===============================
CONF_THRESHOLD = 0.80      # minimal confidence
VAR_THRESHOLD  = 20.0      # hindari background kosong
SERIAL_COOLDOWN = 2.0      # detik (anti spam servo)

# ===============================
# Mapping CNN ? Servo
# ===============================
SERIAL_MAP = {
    "metal": "M",
    "plastic": "A",
    "paper": "A",
    "cardboard": "A",
    "glass": "A",
    "organic": "O"
}

# ===============================
# Serial ke Arduino
# ===============================
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)

def kirim_serial(kode):
    ser.write((kode + '\n').encode())

# ===============================
# Kamera
# ===============================
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

latest_frame = None
latest_result = {"label": "Inisialisasi", "confidence": 0.0}

lock = threading.Lock()
last_cmd = None
last_time = 0
# ===============================
# Thread Kamera
# ===============================
def camera_loop():
    global latest_frame
    while True:
        ret, frame = cap.read()
        if ret:
            with lock:
                latest_frame = frame.copy()
        time.sleep(0.01)

# ===============================
# Thread CNN + Serial
# ===============================
def inference_loop():
    global latest_result, last_cmd, last_time

    while True:
        with lock:
            if latest_frame is None:
                continue
            frame = latest_frame.copy()

        # Preprocess
        img = cv2.resize(frame, (224, 224))
        img = img.astype("float32") / 255.0
        img = np.expand_dims(img, axis=0)

        preds = model.predict(img, verbose=0)
        idx = int(np.argmax(preds))
        conf = float(preds[0][idx])

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        variance = np.std(gray)
        
        

        # ===============================
        # Keputusan FINAL
        # ===============================
        if conf < CONF_THRESHOLD or variance < VAR_THRESHOLD:
            label = "Tidak terdeteksi"
            cmd = None
            conf = 0.0
            last_cmd = None
        else:
            label = labels[idx]
            cmd = SERIAL_MAP[label]

        # ===============================
        # Kirim ke Arduino (AMAN)
        # ===============================
        now = time.time()
        if cmd and (cmd != last_cmd) and (now - last_time > SERIAL_COOLDOWN):
            kirim_serial(cmd)
            last_cmd = cmd
            last_time = now

        with lock:
            latest_result = {"label": label, "confidence": conf}

        time.sleep(0.05)

# ===============================
# Video Streaming
# ===============================
def generate_frames():
    while True:
        with lock:
            if latest_frame is None:
                continue
            frame = latest_frame.copy()
            label = latest_result["label"]
            conf = latest_result["confidence"]

        text = label if label == "Tidak terdeteksi" else f"{label} {conf*100:.1f}%"
        cv2.putText(frame, text, (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 255, 0), 2)

        ret, buffer = cv2.imencode(".jpg", frame)
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" +
               buffer.tobytes() + b"\r\n")

# ===============================
# Flask Routes
# ===============================
@app.route("/video")
def video():
    return Response(generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/label")
def label():
    with lock:
        return jsonify(latest_result)

# ===============================
# Main
# ===============================
if __name__ == "__main__":
    threading.Thread(target=camera_loop, daemon=True).start()
    threading.Thread(target=inference_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
