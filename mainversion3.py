import cv2
import numpy as np
import tensorflow as tf

# ===============================
# Load model CNN
# ===============================
model = tf.keras.models.load_model("model_cnn_6class.h5")

# ===============================
# Label kelas (sesuaikan!)
# ===============================
labels = ['plastic','organic', 'cardboard', 'paper', 'metal', 'glass']

# ===============================
# Kamera (0 = default webcam)
# ===============================
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Kamera tidak bisa dibuka")
    exit()

# ===============================
# Loop realtime
# ===============================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Resize sesuai input CNN
    img = cv2.resize(frame, (300, 300))

    # Normalisasi
    img = img.astype("float32") / 255.0

    # Tambah dimensi batch
    img = np.expand_dims(img, axis=0)  # (1,300,300,3)

    # ===============================
    # Prediksi CNN
    # ===============================
    preds = model.predict(img, verbose=0)
    class_id = np.argmax(preds)
    confidence = preds[0][class_id] * 100
    label = labels[class_id]

    # ===============================
    # Tampilkan hasil
    # ===============================
    text = f"{label} : {confidence:.2f}%"
    cv2.putText(frame, text, (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1,
                (0, 255, 0), 2)

    cv2.imshow("Realtime CNN Classification", frame)

    # Tekan q untuk keluar
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ===============================
# Cleanup
# ===============================
cap.release()
cv2.destroyAllWindows()
