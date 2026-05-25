// =========================================================
// SISTEM PENDATAAN PENGUNJUNG PERPUSTAKAAN BERBASIS RFID
// Politeknik Negeri Bandung - D3 Teknik Elektronika
// =========================================================
// Wemos D1 (ESP8266) + MFRC522 library.
//
// RC522       Wemos D1
// SDA (SS) -> D2  (GPIO4)
// SCK      -> D5  (GPIO14)
// MOSI     -> D7  (GPIO13)
// MISO     -> D6  (GPIO12)
// RST      -> D1  (GPIO5)
// 3.3V     -> 3.3V
// GND      -> GND
// =========================================================

#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN  4   // D2
#define RST_PIN 5   // D1

MFRC522 mfrc522(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(115200);
  SPI.begin();
  mfrc522.PCD_Init();
  Serial.println("READY");
}

void loop() {
  if (!mfrc522.PICC_IsNewCardPresent()) return;
  if (!mfrc522.PICC_ReadCardSerial()) return;

  String uid = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    if (i > 0) uid += ":";
    if (mfrc522.uid.uidByte[i] < 0x10) uid += "0";
    uid += String(mfrc522.uid.uidByte[i], HEX);
  }
  uid.toUpperCase();

  Serial.println(uid);
  mfrc522.PICC_HaltA();
  delay(300);
}
