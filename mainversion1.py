import cv2
import numpy as np
import tensorflow as tf
import time

# ========================
# KONFIGURASI
# ========================
MODEL_PATH = "trash_classifier_4class.tflite"
IMG_SIZE = 224
LABELS = ["glass", "metal", "paper", "plastic"]

CONF_THRESHOLD = 0.70   # minimal confidence agar dianggap valid

# ========================
# LOAD MODEL TFLITE
# ========================
interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# ========================
# INISIALISASI KAMERA
# ========================
cap = cv2.VideoCapture(0)  # 0 = webcam utama

if not cap.isOpened():
    print("❌ Kamera tidak bisa dibuka")
    exit()

print("✅ Webcam aktif, tekan Q untuk keluar")

# ========================
# LOOP UTAMA
# ========================
while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Gagal mengambil frame")
        break

    img = cv2.resize(frame, (IMG_SIZE, IMG_SIZE))
    img = img.astype(np.float32) / 255.0
    img = np.expand_dims(img, axis=0)

    interpreter.set_tensor(input_details[0]['index'], img)
    interpreter.invoke()

    output = interpreter.get_tensor(output_details[0]['index'])[0]
    class_id = np.argmax(output)
    confidence = float(output[class_id])
    label = LABELS[class_id]

    if confidence >= CONF_THRESHOLD:
        text = f"{label} ({confidence:.2f})"
    else:
        text = "Tidak yakin"

    # ========================
    # TAMPILKAN KE LAYAR
    # ========================
    cv2.putText(frame, text,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 255, 0), 2)

    cv2.imshow("Trash Classification - PC Test", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
