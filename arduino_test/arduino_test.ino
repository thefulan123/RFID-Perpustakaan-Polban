// =========================================================
// TES ARDUINO - BLINK + SERIAL
// =========================================================
// Sketch sederhana buat ngetes:
// 1. LED pin 13 kedip-kedip
// 2. Serial mengirim "HELLO" tiap 1 detik
//
// Kalo ini berhasil upload, berarti Arduino dan kabel USB
// berfungsi normal. Masalah ada di wiring RFID atau setting.
// =========================================================

void setup() {
  // Inisialisasi serial (baudrate 115200, sama kayak RFID app).
  Serial.begin(115200);

  // Pin 13 sebagai output buat LED bawaan Arduino.
  pinMode(13, OUTPUT);

  // Kirim tanda hidup.
  Serial.println("ARDUINO OK");
}

void loop() {
  // Nyalakan LED pin 13.
  digitalWrite(13, HIGH);
  Serial.println("LED ON");
  delay(1000);

  // Matikan LED pin 13.
  digitalWrite(13, LOW);
  Serial.println("LED OFF");
  delay(1000);
}
