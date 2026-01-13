#include <Servo.h>

// ===============================
// Servo
// ===============================
Servo servoMetal;
Servo servoAnorganik;
Servo servoOrganik;

// ===============================
// Pin Servo
// ===============================
const int PIN_METAL = 9;
const int PIN_ANORGANIK = 10;
const int PIN_ORGANIK = 5;

// ===============================
// Sudut Kalibrasi
// ===============================
const int METAL_BUKA = 120;
const int METAL_TUTUP = 0;

const int ANORGANIK_BUKA = 150;
const int ANORGANIK_TUTUP = 0;

const int ORGANIK_BUKA = 110;
const int ORGANIK_TUTUP = 0;

// ===============================
void setup() {
  Serial.begin(9600);

  servoMetal.attach(PIN_METAL);
  servoAnorganik.attach(PIN_ANORGANIK);
  servoOrganik.attach(PIN_ORGANIK);

  // Posisi awal
  servoMetal.write(METAL_TUTUP);
  servoAnorganik.write(ANORGANIK_TUTUP);
  servoOrganik.write(ORGANIK_TUTUP);
}

// ===============================
void loop() {
  if (Serial.available()) {
    char cmd = Serial.read();

    if (cmd == 'M') {
      servoMetal.write(METAL_BUKA);
      delay(5000);
      servoMetal.write(METAL_TUTUP);
    }

    else if (cmd == 'A') {
      servoAnorganik.write(ANORGANIK_BUKA);
      delay(5000);
      servoAnorganik.write(ANORGANIK_TUTUP);
    }

    else if (cmd == 'O') {
      servoOrganik.write(ORGANIK_BUKA);
      delay(5000);
      servoOrganik.write(ORGANIK_TUTUP);
    }
  }
}
