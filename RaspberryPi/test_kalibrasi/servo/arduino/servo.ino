#include <Servo.h>

// ===============================
// Servo objects
// ===============================
Servo servoMetal;
Servo servoAnorganik;
Servo servoOrganik;

// ===============================
// Pin mapping
// ===============================
#define PIN_METAL 9
#define PIN_ANORG 10
#define PIN_ORG   5

// ===============================
// Sudut kalibrasi
// ===============================
#define METAL_BUKA   120
#define METAL_TUTUP  0

#define ANORG_BUKA   150
#define ANORG_TUTUP  0

#define ORG_BUKA     110
#define ORG_TUTUP    0

// ===============================
void setup() {
  Serial.begin(9600);

  servoMetal.attach(PIN_METAL);
  servoAnorganik.attach(PIN_ANORG);
  servoOrganik.attach(PIN_ORG);

  // Posisi awal
  servoMetal.write(METAL_TUTUP);
  servoAnorganik.write(ANORG_TUTUP);
  servoOrganik.write(ORG_TUTUP);

  Serial.println("READY");
}

// ===============================
void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd == "METAL") {
      gerakMetal();
    }
    else if (cmd == "ANORG") {
      gerakAnorganik();
    }
    else if (cmd == "ORG") {
      gerakOrganik();
    }
  }
}

// ===============================
void gerakMetal() {
  Serial.println("METAL OPEN");
  servoMetal.write(METAL_BUKA);
  delay(2000);
  servoMetal.write(METAL_TUTUP);
}

// ===============================
void gerakAnorganik() {
  Serial.println("ANORGANIK OPEN");
  servoAnorganik.write(ANORG_BUKA);
  delay(2000);
  servoAnorganik.write(ANORG_TUTUP);
}

// ===============================
void gerakOrganik() {
  Serial.println("ORGANIK OPEN");
  servoOrganik.write(ORG_BUKA);
  delay(2000);
  servoOrganik.write(ORG_TUTUP);
}
