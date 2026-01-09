import cv2
import numpy as np
import tensorflow as tf
import tkinter as tk
from tkinter import Label, Button, Frame
from PIL import Image, ImageTk

# ========================
# KONFIGURASI
# ========================
MODEL_PATH = "model_cnn.tflite"  # Sesuaikan dengan path model Anda
IMG_SIZE = 300
LABELS = ["plastic","organic", "cardboard", "paper", "metal", "glass"]  # Diperbaiki: 5 label
CONF_THRESHOLD = 0.70

# ========================
# LOAD MODEL TFLITE
# ========================
try:
    interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    print("✅ Model berhasil dimuat")
    print(f"📊 Input shape: {input_details[0]['shape']}")
    print(f"📊 Output shape: {output_details[0]['shape']}")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    exit()

# ========================
# INISIALISASI KAMERA
# ========================
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Kamera tidak bisa dibuka")
    exit()

# Set resolusi kamera
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# ========================
# INISIALISASI GUI
# ========================
root = tk.Tk()
root.title("Image Classification System - TFLite")
root.geometry("950x550")
root.configure(bg="#1e1e1e")
root.resizable(False, False)

# ------------------------
# TITLE
# ------------------------
title = Label(root, text="SISTEM KLASIFIKASI SAMPAH",
              font=("Arial", 20, "bold"),
              fg="white", bg="#1e1e1e")
title.pack(pady=15)

# ------------------------
# MAIN FRAME
# ------------------------
main_frame = Frame(root, bg="#1e1e1e")
main_frame.pack()

# ------------------------
# FRAME KAMERA (KIRI)
# ------------------------
camera_frame = Frame(main_frame, bg="black", width=480, height=360, 
                     relief=tk.SUNKEN, borderwidth=3)
camera_frame.grid(row=0, column=0, padx=15, pady=10)
camera_frame.pack_propagate(False)

camera_label = Label(camera_frame, bg="black")
camera_label.pack(fill=tk.BOTH, expand=True)

# ------------------------
# FRAME INFO (KANAN)
# ------------------------
info_frame = Frame(main_frame, bg="#2b2b2b", width=380, height=360,
                   relief=tk.RAISED, borderwidth=3)
info_frame.grid(row=0, column=1, padx=15, pady=10)
info_frame.pack_propagate(False)

lbl_title = Label(info_frame, text="HASIL DETEKSI",
                  font=("Arial", 18, "bold"),
                  fg="white", bg="#2b2b2b")
lbl_title.pack(pady=25)

# Frame untuk hasil klasifikasi
result_frame = Frame(info_frame, bg="#363636", relief=tk.GROOVE, borderwidth=2)
result_frame.pack(pady=10, padx=20, fill=tk.BOTH)

lbl_class = Label(result_frame, text="---",
                  font=("Arial", 28, "bold"),
                  fg="cyan", bg="#363636",
                  height=2)
lbl_class.pack(pady=15)

lbl_conf = Label(info_frame, text="Confidence: 0.00%",
                 font=("Arial", 16),
                 fg="white", bg="#2b2b2b")
lbl_conf.pack(pady=15)

# Status label
lbl_status = Label(info_frame, text="🟢 Kamera Aktif",
                   font=("Arial", 12),
                   fg="lime", bg="#2b2b2b")
lbl_status.pack(pady=10)

# ------------------------
# FRAME TOMBOL
# ------------------------
button_frame = Frame(root, bg="#1e1e1e")
button_frame.pack(pady=15)

# Variabel untuk freeze detection
freeze_detection = False

def toggle_detection():
    global freeze_detection
    freeze_detection = not freeze_detection
    if freeze_detection:
        btn_freeze.config(text="LANJUTKAN", bg="orange")
        lbl_status.config(text="⏸️ Deteksi Dijeda", fg="orange")
    else:
        btn_freeze.config(text="JEDA", bg="blue")
        lbl_status.config(text="🟢 Kamera Aktif", fg="lime")

def exit_app():
    cap.release()
    cv2.destroyAllWindows()
    root.destroy()

btn_freeze = Button(button_frame, text="JEDA",
                    font=("Arial", 12, "bold"),
                    bg="blue", fg="white",
                    width=12, height=2,
                    command=toggle_detection)
btn_freeze.grid(row=0, column=0, padx=10)

btn_exit = Button(button_frame, text="KELUAR",
                  font=("Arial", 12, "bold"),
                  bg="red", fg="white",
                  width=12, height=2,
                  command=exit_app)
btn_exit.grid(row=0, column=1, padx=10)

# ========================
# FUNGSI PREPROCESSING
# ========================
def preprocess_image(frame):
    """
    Preprocessing gambar sesuai kebutuhan model
    """
    img = cv2.resize(frame, (IMG_SIZE, IMG_SIZE))
    img = img.astype(np.float32) / 255.0
    img = np.expand_dims(img, axis=0)
    return img

# ========================
# FUNGSI KLASIFIKASI
# ========================
def classify_image(frame):
    """
    Melakukan klasifikasi pada frame
    """
    try:
        img = preprocess_image(frame)
        
        # Set input tensor
        interpreter.set_tensor(input_details[0]['index'], img)
        
        # Run inference
        interpreter.invoke()
        
        # Get output
        output = interpreter.get_tensor(output_details[0]['index'])[0]
        
        # Validasi output
        if len(output) != len(LABELS):
            print(f"⚠️ Warning: Output size ({len(output)}) != Labels size ({len(LABELS)})")
            return "ERROR", 0.0
        
        class_id = np.argmax(output)
        confidence = float(output[class_id])
        label = LABELS[class_id]
        
        return label, confidence
    
    except Exception as e:
        print(f"❌ Error dalam klasifikasi: {e}")
        return "ERROR", 0.0

# ========================
# FUNGSI UPDATE FRAME
# ========================
def update_frame():
    ret, frame = cap.read()
    
    if not ret:
        lbl_status.config(text="❌ Kamera Error", fg="red")
        root.after(100, update_frame)
        return
    
    # Klasifikasi jika tidak dijeda
    if not freeze_detection:
        label, confidence = classify_image(frame)
        
        # Update label klasifikasi
        if label != "ERROR":
            if confidence >= CONF_THRESHOLD:
                text = label.upper()
                color = "lime"
            else:
                text = "TIDAK YAKIN"
                color = "yellow"
            
            lbl_class.config(text=text, fg=color)
            lbl_conf.config(text=f"Confidence: {confidence*100:.2f}%")
        else:
            lbl_class.config(text="ERROR", fg="red")
            lbl_conf.config(text="Confidence: 0.00%")
    
    # Convert frame untuk ditampilkan di Tkinter
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_resized = cv2.resize(frame_rgb, (480, 360))
    
    img_pil = Image.fromarray(frame_resized)
    img_tk = ImageTk.PhotoImage(image=img_pil)
    
    camera_label.imgtk = img_tk
    camera_label.configure(image=img_tk)
    
    # Update setiap 10ms
    root.after(10, update_frame)

# ========================
# JALANKAN APLIKASI
# ========================
print("🚀 Aplikasi dimulai...")
update_frame()
root.mainloop()

# Cleanup
cap.release()
cv2.destroyAllWindows()
print("✅ Aplikasi ditutup")
