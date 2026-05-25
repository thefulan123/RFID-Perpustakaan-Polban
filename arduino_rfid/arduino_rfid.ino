// =========================================================
// SISTEM PENDATAAN PENGUNJUNG PERPUSTAKAAN BERBASIS RFID
// Politeknik Negeri Bandung - D3 Teknik Elektronika
// =========================================================
// Sketch ini membaca UID kartu RFID via RC522 dan
// mengirimkannya ke komputer melalui serial USB.
//
// TIDAK menggunakan library MFRC522 eksternal.
// Semua komunikasi SPI dilakukan secara manual (bit-bang)
// via Software SPI, jadi semua pin BEBAS diatur.
// Cocok jika pin hardware SPI (10,11,12,13) rusak.
// =========================================================

#include <Arduino.h>

// ===================== KONFIGURASI PIN =====================
// Sesuaikan pin di bawah ini dengan wiring kamu.
#define SS_PIN    7   // SDA (Slave Select)  -> bebas
#define RST_PIN   9   // RST (Reset)         -> bebas
#define MOSI_PIN  6   // MOSI (Master Out)   -> bebas
#define MISO_PIN  5   // MISO (Master In)    -> bebas
#define SCK_PIN   4   // SCK (Clock)         -> bebas

// Pin output untuk indikator (opsional).
#define LED_HIJAU A0  // LED hijau (kartu valid)
#define LED_MERAH A1  // LED merah (kartu tidak terdaftar)
#define BUZZER    A2  // Buzzer (peringatan)


// ===================== REGISTER MFRC522 ====================
// Alamat register internal chip MFRC522 (liat datasheet).
// Register dikirim via SPI dengan format:
//   bit 7: 0=write, 1=read
//   bit 6-0: alamat register (digeser 1 bit ke kiri)
#define REG_COMMAND      0x01
#define REG_COM_I_EN     0x02
#define REG_DIV_I_EN     0x03
#define REG_COM_IRQ      0x04
#define REG_DIV_IRQ      0x05
#define REG_ERROR        0x06
#define REG_STATUS_1     0x07
#define REG_STATUS_2     0x08
#define REG_FIFO_DATA    0x09
#define REG_FIFO_LEVEL   0x0A
#define REG_WATER_LEVEL  0x0B
#define REG_CONTROL      0x0C
#define REG_BIT_FRAMING  0x0D
#define REG_COLL         0x0E
#define REG_MODE         0x11
#define REG_TX_MODE      0x12
#define REG_RX_MODE      0x13
#define REG_TX_CONTROL   0x14
#define REG_TX_AUTO      0x15
#define REG_TPRESCALER   0x2B
#define REG_TRELOAD_L    0x2C
#define REG_TRELOAD_H    0x2D
#define REG_VERSION      0x37

// Perintah untuk CommandReg.
#define CMD_IDLE        0x00
#define CMD_CALC_CRC    0x03
#define CMD_TRANSCEIVE  0x0C
#define CMD_MF_AUTHENT  0x0E
#define CMD_SOFT_POWER_DN 0x10

// Perintah untuk kartu RFID (PICC).
#define PICC_CMD_REQA   0x26  // Request Answer
#define PICC_CMD_ANTICOL_1 0x93  // Anti-collision CL1


// ===================== FUNGSI SOFTWARE SPI =================
// Fungsi bit-bang manual untuk komunikasi SPI.
// Tidak perlu pin hardware SPI (tidak pake library SPI.h).

void softSPI_init() {
  pinMode(SCK_PIN, OUTPUT);
  pinMode(MOSI_PIN, OUTPUT);
  pinMode(MISO_PIN, INPUT);
  pinMode(SS_PIN, OUTPUT);
  digitalWrite(SCK_PIN, LOW);
  digitalWrite(MOSI_PIN, LOW);
  digitalWrite(SS_PIN, HIGH);  // SS inactive (HIGH)
}

uint8_t softSPI_transfer(uint8_t data) {
  // Kirim 8 bit data via MOSI, sambil baca 8 bit dari MISO.
  // Clock polarity: idle LOW, data sampled on rising edge (SPI mode 0).
  uint8_t result = 0;
  for (int i = 7; i >= 0; i--) {
    // Tiap bit: set MOSI, clock HIGH, baca MISO, clock LOW.
    digitalWrite(MOSI_PIN, (data >> i) & 1);
    digitalWrite(SCK_PIN, HIGH);
    result |= (digitalRead(MISO_PIN) << i);
    digitalWrite(SCK_PIN, LOW);
  }
  return result;
}


// ===================== FUNGSI BACA/TULIS REGISTER =========

void mfrc522_write(uint8_t reg, uint8_t data) {
  // Write mode: bit7 = 0, reg digeser 1 bit ke kiri.
  digitalWrite(SS_PIN, LOW);
  softSPI_transfer((reg << 1) & 0x7E);
  softSPI_transfer(data);
  digitalWrite(SS_PIN, HIGH);
}

uint8_t mfrc522_read(uint8_t reg) {
  // Read mode: bit7 = 1, reg digeser 1 bit ke kiri.
  digitalWrite(SS_PIN, LOW);
  softSPI_transfer(((reg << 1) & 0x7E) | 0x80);
  uint8_t data = softSPI_transfer(0x00);
  digitalWrite(SS_PIN, HIGH);
  return data;
}

void mfrc522_set_bitmask(uint8_t reg, uint8_t mask) {
  uint8_t tmp = mfrc522_read(reg);
  mfrc522_write(reg, tmp | mask);
}

void mfrc522_clear_bitmask(uint8_t reg, uint8_t mask) {
  uint8_t tmp = mfrc522_read(reg);
  mfrc522_write(reg, tmp & ~mask);
}


// ===================== INISIALISASI MFRC522 ================

void mfrc522_init() {
  // --- Reset hardware ---
  pinMode(RST_PIN, OUTPUT);
  digitalWrite(RST_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(RST_PIN, HIGH);
  delay(50);  // Tunggu chip stabil

  // Cek koneksi dengan membaca firmware version register.
  // Version 0x92 atau 0x12 = MFRC522 original.
  uint8_t version = mfrc522_read(REG_VERSION);
  // Kalo 0x00 atau 0xFF -> komunikasi gagal.
  if (version == 0x00 || version == 0xFF) {
    // Abaikan, error akan terlihat saat tidak bisa baca kartu.
  }

  // --- Konfigurasi timer ---
  // Timer = TPrescaler * Treload / 6.78MHz = ~25ms timeout.
  mfrc522_write(REG_MODE, 0x3D);     // CRC initial value 0x6363
  mfrc522_write(REG_TX_MODE, 0x00);  // Bit framing: normal
  mfrc522_write(REG_RX_MODE, 0x00);  // Bit framing: normal

  // Set timer autoload
  mfrc522_write(REG_TPRESCALER, 0x3E);
  mfrc522_write(REG_TRELOAD_L, 30);
  mfrc522_write(REG_TRELOAD_H, 0);

  // 100% ASK modulation
  mfrc522_write(REG_TX_AUTO, 0x40);
  // Set bit framing: 1 byte (8 bits) per transfer
  mfrc522_write(REG_BIT_FRAMING, 0x00);

  // --- Nyalakan antenna ---
  mfrc522_set_bitmask(REG_TX_CONTROL, 0x03);
}


// ===================== KOMUNIKASI DENGAN KARTU ============

void mfrc522_transceive(uint8_t *send_data, uint8_t send_len,
                         uint8_t *recv_data, uint8_t *recv_len) {
  // 1. Flush FIFO (hapus data lama).
  mfrc522_set_bitmask(REG_FIFO_LEVEL, 0x80);

  // 2. Tulis data ke FIFO.
  for (uint8_t i = 0; i < send_len; i++) {
    mfrc522_write(REG_FIFO_DATA, send_data[i]);
  }

  // 3. Set command ke TRANSCEIVE.
  mfrc522_write(REG_COMMAND, CMD_TRANSCEIVE);

  // 4. Mulai transmisi (StartSend = 1).
  mfrc522_set_bitmask(REG_BIT_FRAMING, 0x80);

  // 5. Tunggu hingga selesai.
  uint16_t timeout = 2000;
  while (timeout--) {
    uint8_t irq = mfrc522_read(REG_COM_IRQ);
    if (irq & 0x30) {  // Bit4 (TxIRq) atau bit5 (RxIRq) = selesai
      break;
    }
    delayMicroseconds(10);
  }

  // 6. Hentikan command.
  mfrc522_clear_bitmask(REG_BIT_FRAMING, 0x80);
  mfrc522_write(REG_COMMAND, CMD_IDLE);

  // 7. Baca jumlah byte yang diterima dari FIFO.
  uint8_t count = mfrc522_read(REG_FIFO_LEVEL);

  // 8. Baca data dari FIFO.
  *recv_len = count;
  for (uint8_t i = 0; i < count; i++) {
    recv_data[i] = mfrc522_read(REG_FIFO_DATA);
  }
}


// ===================== BACA UID KARTU =====================

bool baca_uid_rfid(String &uid_str) {
  // --- Langkah 1: Request REQA ---
  // Kirim perintah REQA (0x26) untuk mendeteksi kartu.
  uint8_t req_data[] = {PICC_CMD_REQA};
  uint8_t req_resp[2];
  uint8_t req_len = 0;

  mfrc522_transceive(req_data, 1, req_resp, &req_len);

  // Kalo tidak ada respon (length = 0), tidak ada kartu.
  if (req_len == 0) {
    return false;
  }

  // --- Langkah 2: Anti-collision ---
  // Kirim perintah anti-collision CL1 (0x93) + 0x20 (NVB=40 bit)
  // untuk mendapatkan UID kartu.
  uint8_t anticol_data[] = {PICC_CMD_ANTICOL_1, 0x20};
  uint8_t uid_bytes[10];  // Buffer untuk UID + checksum.
  uint8_t uid_len = 0;

  mfrc522_transceive(anticol_data, 2, uid_bytes, &uid_len);

  // Hasil anti-collision: 5 byte (4 byte UID + 1 byte checksum).
  // Kalo kurang dari 5, gagal.
  if (uid_len < 5) {
    return false;
  }

  // --- Susun UID jadi format "XX:XX:XX:XX" ---
  uid_str = "";
  for (uint8_t i = 0; i < 4; i++) {
    if (i > 0) uid_str += ":";
    if (uid_bytes[i] < 0x10) uid_str += "0";
    uid_str += String(uid_bytes[i], HEX);
  }
  uid_str.toUpperCase();

  // --- Hentikan kartu (HALT) agar tidak terbaca terus ---
  uint8_t halt_data[] = {0x50, 0x00};
  uint8_t halt_resp[2];
  uint8_t halt_len = 0;
  mfrc522_transceive(halt_data, 2, halt_resp, &halt_len);

  return true;
}


// ===================== SETUP ==============================

void setup() {
  // Inisialisasi serial ke komputer (baudrate harus sama dengan Python app).
  Serial.begin(115200);
  while (!Serial) { ; }  // Tunggu serial siap (khusus Arduino Leonardo).

  // Setup pin indikator.
  pinMode(LED_HIJAU, OUTPUT);
  pinMode(LED_MERAH, OUTPUT);
  pinMode(BUZZER, OUTPUT);
  digitalWrite(LED_HIJAU, LOW);
  digitalWrite(LED_MERAH, LOW);
  digitalWrite(BUZZER, LOW);

  // Inisialisasi software SPI dan MFRC522.
  softSPI_init();
  mfrc522_init();

  // Kirim sinyal siap ke komputer.
  Serial.println("READY");

  // Blip hijau sebagai tanda ok.
  digitalWrite(LED_HIJAU, HIGH);
  delay(200);
  digitalWrite(LED_HIJAU, LOW);
}


// ===================== LOOP UTAMA =========================

void loop() {
  String uid = "";

  // Coba baca UID dari kartu yang didekatkan.
  if (baca_uid_rfid(uid)) {
    // Kartu terbaca -> kirim UID via serial.
    Serial.println(uid);
  }

  // Delay kecil agar tidak overload.
  delay(200);
}
