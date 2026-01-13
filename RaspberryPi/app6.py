from flask import Flask, Response, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import tensorflow as tf
import threading
import time
from gpiozero import Servo

# ===============================
# Flask
# ===============================
app = Flask(__name__)
CORS(app)

# ===============================
# Load CNN model
# ===============================
model = tf.keras.models.load_model("modelv5.h5")
labels = ['cardboard','glass', 'metal', 'organic', 'paper', 'plastic']

# ===============================
# Parameter sistem
# ===============================
CONF_THRESHOLD = 0.75
VAR_THRESHOLD  = 15.0
SERVO_COOLDOWN = 2.0  # detik

# ===============================
# Mapping kelas ? kategori
# ===============================
SERVO_MAP = {
    "metal": "metal",
    "plastic": "anorganik",
    "paper": "anorganik",
    "cardboard": "anorganik",
    "glass": "anorganik",
    "organic": "organik"
}

# ===============================
# Servo
# ===============================
servo_metal = Servo(17)
servo_anorganik = Servo(27)
servo_organik = Servo(22)

# Posisi netral
servo_metal.mid()
servo_anorganik.mid()
servo_organik.mid()

# ===============================
# Kamera
# ===============================
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

latest_frame = None
latest_result = {
    "label": "Inisialisasi",
    "confidence": 0.0
}

lock = threading.Lock()
last_category = None
last_servo_time = 0

# ===============================
# Fungsi gerak servo
# ===============================
def gerak_servo(kategori):
    if kategori == "metal":
        servo_metal.min()
        time.sleep(0.8)
        servo_metal.mid()

    elif kategori == "anorganik":
        servo_anorganik.max()
        time.sleep(0.8)
        servo_anorganik.mid()

    elif kategori == "organik":
        servo_organik.max()
        time.sleep(0.8)
        servo_organik.mid()
# ===============================
# Thread kamera
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
# Thread CNN + Servo
# ===============================
def inference_loop():
    global latest_result, last_category, last_servo_time

    while True:
        with lock:
            if latest_frame is None:
                continue
            frame = latest_frame.copy()

        # Preprocessing
        img = cv2.resize(frame, (224, 224))
        img = img.astype("float32") / 255.0
        img = np.expand_dims(img, axis=0)

        preds = model.predict(img, verbose=0)
        idx = int(np.argmax(preds))
        conf = float(preds[0][idx])

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        variance = np.std(gray)

        # ===============================
        # Keputusan final
        # ===============================
        if conf < CONF_THRESHOLD or variance < VAR_THRESHOLD:
            label = "Tidak terdeteksi"
            conf = 0.0
            kategori = None
        else:
            label = labels[idx]
            kategori = SERVO_MAP[label]

        # ===============================
        # Kontrol servo (aman)
        # ===============================
        now = time.time()
        if kategori and kategori != last_category:
            if now - last_servo_time > SERVO_COOLDOWN:
                gerak_servo(kategori)
                last_servo_time = now
                last_category = kategori

        with lock:
            latest_result = {
                "label": label,
                "confidence": conf
            }

        time.sleep(0.05)

# ===============================
# Video streaming
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
                    (0,255,0), 2)

        ret, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()

        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

# ===============================
# Flask routes
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
