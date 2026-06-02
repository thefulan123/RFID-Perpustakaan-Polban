// =========================================================
// SISTEM PENDATAAN PENGUNJUNG PERPUSTAKAAN BERBASIS RFID
// Board: LOLIN(WEMOS) D1 R2 & mini + Modul MFRC522
// =========================================================

#include <SPI.h>
#include <MFRC522.h>

// Konfigurasi pin untuk Wemos D1
#define SS_PIN  D2   // SDA (GPIO4)
#define RST_PIN D1   // RST (GPIO5)

MFRC522 mfrc522(SS_PIN, RST_PIN); // Inisialisasi MFRC522

void setup() {
  Serial.begin(115200); 
  SPI.begin();          
  mfrc522.PCD_Init();   
  
  Serial.println("READY");
}

void loop() {
  // Tunggu sampai ada kartu yang terdeteksi sensor
  if (!mfrc522.PICC_IsNewCardPresent()) {
    return;
  }

  // Baca data serial dari kartu
  if (!mfrc522.PICC_ReadCardSerial()) {
    return;
  }

  // Menggabungkan byte UID menjadi string XX:XX:XX:XX
  String uid = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    if (i > 0) uid += ":";
    if (mfrc522.uid.uidByte[i] < 0x10) uid += "0";
    uid += String(mfrc522.uid.uidByte[i], HEX);
  }
  uid.toUpperCase();

  // Kirim UID via serial
  Serial.println(uid);

  // Hentikan pembacaan kartu saat ini
  mfrc522.PICC_HaltA();
  
  // Jeda 1 detik sebelum percobaan selanjutnya
  delay(1000); 
}