"""
Contoh GUI Python (Tkinter) dengan kamera di kiri dan deskripsi di kanan.
Dependencies: opencv-python, pillow
Jalankan: python GUI_camera_example.py
"""

import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2

class CameraGUI:
    def __init__(self, root, cam_index=0):
        self.root = root
        self.root.title("Contoh GUI Kamera - Kiri: Kamera, Kanan: Deskripsi")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Layout: left = camera, right = deskripsi
        self.main_frame = ttk.Frame(self.root, padding=8)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_frame = ttk.Frame(self.main_frame, width=300)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Kamera: label untuk menampilkan frame
        self.video_label = ttk.Label(self.left_frame)
        self.video_label.pack(fill=tk.BOTH, expand=True)

        # Kontrol sederhana di bawah kamera
        controls = ttk.Frame(self.left_frame)
        controls.pack(fill=tk.X, pady=6)
        self.start_btn = ttk.Button(controls, text="Start", command=self.start_camera)
        self.start_btn.pack(side=tk.LEFT, padx=4)
        self.stop_btn = ttk.Button(controls, text="Stop", command=self.stop_camera, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=4)

        # Deskripsi di kanan: contoh judul + teks + tombol aksi
        title = ttk.Label(self.right_frame, text="Deskripsi Kamera", font=(None, 14, 'bold'))
        title.pack(anchor=tk.NW, pady=(6,4), padx=6)

        self.desc_text = tk.Text(self.right_frame, wrap=tk.WORD, height=15)
        self.desc_text.pack(fill=tk.BOTH, expand=True, padx=6)
        self.desc_text.insert(tk.END,
                              "Ini adalah area deskripsi.\n\nContoh penggunaan:\n- Menampilkan frame kamera di sisi kiri.\n- Menambahkan informasi hasil deteksi atau metadata di sini.\n\nAnda bisa mengganti teks ini dengan deskripsi apa pun yang diinginkan.")
        self.desc_text.config(state=tk.DISABLED)

        action_btn = ttk.Button(self.right_frame, text="Ambil Snapshot", command=self.take_snapshot)
        action_btn.pack(pady=6, padx=6, anchor=tk.S)

        # Kamera variables
        self.cam_index = cam_index
        self.cap = None
        self.running = False
        self._thread = None

    def start_camera(self):
        if self.running:
            return
        # Buka capture
        self.cap = cv2.VideoCapture(self.cam_index)
        if not self.cap.isOpened():
            tk.messagebox.showerror("Error", "Tidak dapat membuka kamera. Periksa indeks kamera atau koneksi.")
            return
        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self._thread = threading.Thread(target=self._update_loop, daemon=True)
        self._thread.start()

    def stop_camera(self):
        if not self.running:
            return
        self.running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        # Release handled in loop or on_close

    def _update_loop(self):
        while self.running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            # Resize frame agar muat di label
            h, w = frame.shape[:2]
            max_w = 640
            if w > max_w:
                scale = max_w / w
                frame = cv2.resize(frame, (int(w*scale), int(h*scale)))

            # Convert BGR -> RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            # Update label (harus di main thread) -> gunakan after
            self.video_label.after(0, self._set_image, imgtk)

            # sleep singkat untuk mengurangi beban CPU
            cv2.waitKey(10)

        # loop selesai: release
        if self.cap:
            self.cap.release()
            self.cap = None

    def _set_image(self, imgtk):
        # Simpan referensi agar tidak ter-GC
        self.video_label.imgtk = imgtk
        self.video_label.config(image=imgtk)

    def take_snapshot(self):
        # Ambil snapshot dari frame terakhir jika tersedia
        if not self.running or not self.video_label: 
            tk.messagebox.showinfo("Info", "Kamera belum dijalankan.")
            return
        imgtk = getattr(self.video_label, 'imgtk', None)
        if imgtk is None:
            tk.messagebox.showinfo("Info", "Belum ada frame untuk disimpan.")
            return
        # Convert back to PIL Image dan simpan
        pil_img = imgtk._PhotoImage__photo.convert('RGB') if hasattr(imgtk, '_PhotoImage__photo') else None
        # Cara aman: ambil dari cap sekali lagi
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                import time
                filename = f"snapshot_{int(time.time())}.png"
                cv2.imwrite(filename, frame)
                tk.messagebox.showinfo("Snapshot", f"Disimpan sebagai {filename}")
                return
        tk.messagebox.showinfo("Snapshot", "Gagal mengambil snapshot.")

    def on_close(self):
        self.running = False
        if self.cap and self.cap.isOpened():
            try:
                self.cap.release()
            except Exception:
                pass
        self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = CameraGUI(root, cam_index=0)
    root.mainloop()
