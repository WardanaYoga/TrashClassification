import serial
import time

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)

def kirim(kategori):
    ser.write((kategori + '\n').encode())

# Contoh
kirim("METAL")
time.sleep(2)
kirim("ANORG")
time.sleep(2)
kirim("ORG")
