// =========================================================
// PENGUJIAN WEMOS D1 MINI + RFID RC522
// Politeknik Negeri Bandung - D3 Teknik Elektronika
// Mata Kuliah: Sistem Instrumentasi Elektronika
// =========================================================
// Pengujian ini bertujuan untuk memverifikasi:
//   1. Komunikasi serial Wemos D1 Mini dengan komputer
//   2. Pembacaan UID kartu RFID menggunakan modul RC522
//   3. Indikator LED sebagai output visual
//
// Alat dan Bahan:
//   - Wemos D1 Mini (ESP8266)
//   - Modul RFID RC522
//   - Kartu RFID/Tag
//   - Kabel jumper
//
// Wiring:
//   RC522       Wemos D1 Mini    GPIO
//   SDA (SS) -> D2              = GPIO4
//   SCK      -> D5              = GPIO14
//   MOSI     -> D7              = GPIO13
//   MISO     -> D6              = GPIO12
//   RST      -> D1              = GPIO5
//   3.3V     -> 3.3V
//   GND      -> GND
//
// Prosedur Pengujian:
//   1. Upload program ke Wemos D1 Mini
//   2. Buka Serial Monitor (baudrate 115200)
//   3. Amati output "READY" sebagai tanda inisialisasi berhasil
//   4. Tempelkan kartu RFID ke modul RC522
//   5. Amati UID kartu yang muncul di Serial Monitor
//   6. Ulangi langkah 4-5 untuk beberapa kartu berbeda
// =========================================================

#include <SPI.h>
#include <MFRC522.h>

// --- Konfigurasi Pin ---
#define SS_PIN_RFID  4   // SDA  -> D2 (GPIO4)
#define RST_PIN_RFID 5   // RST  -> D1 (GPIO5)
#define LED_TEST     2   // LED  -> D4 (GPIO2) - LED bawaan Wemos

MFRC522 mfrc522(SS_PIN_RFID, RST_PIN_RFID);

// ===================== SETUP ==============================
void setup() {
  // Inisialisasi komunikasi serial dengan komputer.
  Serial.begin(115200);
  while (!Serial) { ; }

  // Inisialisasi LED indikator.
  pinMode(LED_TEST, OUTPUT);
  digitalWrite(LED_TEST, LOW);

  // Inisialisasi komunikasi SPI dan modul RFID RC522.
  SPI.begin();
  mfrc522.PCD_Init();

  // Kirim header pengujian ke serial.
  Serial.println("");
  Serial.println("==========================================");
  Serial.println("PENGUJIAN WEMOS D1 MINI + RFID RC522");
  Serial.println("Politeknik Negeri Bandung");
  Serial.println("==========================================");
  Serial.println("");

  // Tampilkan versi firmware modul RC522.
  byte version = mfrc522.PCD_ReadRegister(MFRC522::VersionReg);
  Serial.print("Firmware Version: 0x");
  Serial.print(version, HEX);
  Serial.println(" (0x92/0x12 = OK)");

  // Uji LED: berkedip 3 kali sebagai indikasi siap.
  Serial.println("Uji LED: OK (3x kedip)");
  for (int i = 0; i < 3; i++) {
    digitalWrite(LED_TEST, HIGH);
    delay(200);
    digitalWrite(LED_TEST, LOW);
    delay(200);
  }

  Serial.println("");
  Serial.println("Siap membaca kartu RFID. Tempelkan kartu...");
  Serial.println("------------------------------------------");
}


// ===================== LOOP UTAMA =========================
void loop() {
  // Cek apakah ada kartu di dekat reader.
  if (!mfrc522.PICC_IsNewCardPresent()) {
    return;
  }

  // Baca UID dari kartu.
  if (!mfrc522.PICC_ReadCardSerial()) {
    Serial.println("Gagal membaca kartu");
    return;
  }

  // LED menyala saat kartu terbaca.
  digitalWrite(LED_TEST, HIGH);

  // Ambil informasi tipe kartu.
  MFRC522::PICC_Type piccType = mfrc522.PICC_GetType(mfrc522.uid.sak);
  String tipeKartu = mfrc522.PICC_GetTypeName(piccType);

  // Susun UID dalam format XX:XX:XX:XX.
  String uid = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    if (i > 0) uid += ":";
    if (mfrc522.uid.uidByte[i] < 0x10) uid += "0";
    uid += String(mfrc522.uid.uidByte[i], HEX);
  }
  uid.toUpperCase();

  // Tampilkan hasil pembacaan ke Serial Monitor.
  Serial.println("");
  Serial.println("------------------------------------------");
  Serial.println("KARTU TERDETEKSI!");
  Serial.print  ("UID          : ");
  Serial.println(uid);
  Serial.print  ("Tipe Kartu   : ");
  Serial.println(tipeKartu);
  Serial.print  ("Jumlah Byte  : ");
  Serial.print(mfrc522.uid.size);
  Serial.println(" byte");
  Serial.println("------------------------------------------");

  // Hentikan komunikasi dengan kartu.
  mfrc522.PICC_HaltA();

  delay(500);
  digitalWrite(LED_TEST, LOW);
}
