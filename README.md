# Sistem Pendataan Pengunjung Perpustakaan Berbasis RFID

Aplikasi desktop untuk mendata pengunjung perpustakaan menggunakan kartu RFID.
Dibangun dengan Python dan CustomTkinter sebagai proyek akhir mata kuliah
Sistem Instrumentasi Elektronika di Politeknik Negeri Bandung.

## Fitur

- **Login Admin/Guest** — Admin (password: `admin`) memiliki akses penuh; Guest hanya dapat melakukan tap-in
- **Monitoring Real-time** — Menampilkan statistik kunjungan harian, mingguan, dan bulanan
- **Scan RFID** — Membaca kartu melalui Wemos D1 / Arduino Uno + RC522, pencatatan dilakukan secara otomatis
- **1 Hari 1 Scan** — Kartu yang telah melakukan scan pada hari yang sama akan ditolak dengan peringatan
- **Manajemen Kartu** — Mendaftarkan, mencari, dan menghapus data mahasiswa
- **Import/Export Excel** — Import data mahasiswa dan export data kunjungan ke file Excel
- **Mode Simulasi** — Pengujian tanpa hardware (dapat menggunakan tombol "Kartu Valid")
- **Dark Theme** — Tampilan modern dengan tema gelap

## Kebutuhan Sistem (di PC)

| Software | Keterangan |
|----------|------------|
| **Windows 10/11** | Aplikasi ini berjalan pada sistem operasi Windows |
| **Python 3.10 – 3.13** | Python 3.14 belum mendukung (disarankan menggunakan Python 3.11) |
| **pip** | Umumnya sudah tersedia bersamaan dengan instalasi Python |

## Cara Install (CLI)

Buka **PowerShell** atau **Command Prompt**, kemudian:

```powershell
# 1. Pastikan Python telah terinstall
python --version
# output yang diharapkan: Python 3.11.x

# 2. Masuk ke direktori aplikasi
cd E:\Aplikasi Perpustakaan POLBAN\rfid_perpustakaan

# 3. Install seluruh dependensi
pip install -r requirements.txt
```

## Cara Menjalankan

```powershell
cd E:\Aplikasi Perpustakaan POLBAN\rfid_perpustakaan
python main.py
```

## Login

| Role | Password | Akses |
|------|----------|-------|
| **Admin** | `admin` | Monitoring, Manajemen Kartu, Pengaturan |
| **Guest** | (langsung masuk) | Halaman tap-in, tombol Kartu Valid |

## Elektrikal

### Spesifikasi Modul RC522

| Parameter | Nilai |
|-----------|-------|
| Tegangan operasi | **3.3V DC** (⚠️ Jangan gunakan 5V! Dapat merusak komponen) |
| Arus operasi | ~13–26 mA (standby), ~80 mA (saat membaca kartu) |
| Frekuensi RF | 13.56 MHz (HF — High Frequency) |
| Protokol komunikasi | **SPI** (SCK, MOSI, MISO, SDA/SS) + RST |
| Jarak baca | ~2–5 cm (tergantung kartu dan antena) |
| Kartu compatible | MIFARE Classic 1K/4K, MIFARE Ultralight, NTAG |
| Chip | NXP MFRC522 |

### Logika Tegangan (3.3V vs 5V)

- **RC522** merupakan modul **3.3V**. Seluruh pin I/O (SDA, SCK, MOSI, MISO, RST) hanya
  boleh diberikan tegangan **maksimal 3.3V**. Jika diberikan tegangan 5V, chip MFRC522
  dapat mengalami kerusakan permanen.
- **Wemos D1 Mini (ESP8266)** sudah **3.3V native** — seluruh GPIO-nya menggunakan 3.3V.
  Cocok langsung dihubungkan ke RC522 tanpa level shifter.
- **Arduino Uno** memiliki logika **5V** pada pin I/O. Jika Arduino Uno digunakan secara
  langsung ke RC522 tanpa level shifter, tegangan 5V dari pin MOSI/MISO/SCK/SDA dapat
  merusak RC522 dalam jangka panjang.

### Level Shifter (wajib untuk Arduino Uno)

Karena Arduino Uno menghasilkan output 5V, diperlukan **level shifter** (konverter tegangan)
antara Uno dan RC522. Terdapat beberapa opsi:

1. **Modul level shifter 4-channel** (direkomendasikan) — tersedia di toko elektronik
   dengan harga terjangkau. Wiring: HV (5V) ke Uno, LV (3.3V) ke RC522.
2. **Pembagi tegangan resistor** — menggunakan 2 resistor (1kΩ + 2.2kΩ) pada setiap jalur
   SPI. Berfungsi menurunkan tegangan dari 5V menjadi ~3.3V, namun arah MISO perlu diatur
   secara berbeda.
3. **Modul RC522 khusus 5V** — beberapa versi modul RC522 telah dilengkapi regulator 3.3V
   dan level shifter bawaan.

⚠️ **Peringatan**: Meskipun terdapat referensi yang menyatakan bahwa Uno dapat langsung
dihubungkan ke RC522 tanpa level shifter, hal ini **tidak disarankan** untuk proyek
permanen. Tegangan 5V secara perlahan dapat merusak input 3.3V chip MFRC522.

### Konsumsi Daya

| Komponen | Tegangan | Arus |
|----------|----------|------|
| Wemos D1 Mini (aktif + WiFi) | 3.3V | ~80–200 mA |
| Arduino Uno (aktif) | 5V (via USB/Vin) | ~50–100 mA |
| Modul RC522 (baca kartu) | 3.3V | ~80 mA |
| **Total (Wemos + RC522)** | **3.3V** | **~160–280 mA** |
| **Total (Uno + RC522)** | **5V + 3.3V** | **~130–180 mA** |

Keduanya dapat dihubungkan langsung ke USB komputer (500 mA max) tanpa memerlukan
adaptor tambahan.

### Jarak dan Antena

- Jarak baca maksimal RC522 ~2–5 cm tergantung bentuk kartu/tag
- Untuk jarak optimal, tempelkan kartu sejajar dengan modul (parallel), bukan dalam
  posisi tegak lurus
- Antena RC522 terdapat di dalam PCB modul (coil printed circuit board)

---

## Koneksi Hardware RFID

### Opsi 1: Wemos D1 Mini (DIREKOMENDASIKAN)

Wemos D1 Mini berbasis ESP8266 dengan logika **3.3V**, sehingga cocok langsung
dihubungkan dengan RC522 tanpa level shifter. Komunikasi SPI menggunakan hardware SPI.

Wiring:

```
RC522      →  Wemos D1 Mini   →  GPIO
SDA (SS)   →  D2              →  GPIO4
SCK        →  D5              →  GPIO14
MOSI       →  D7              →  GPIO13
MISO       →  D6              →  GPIO12
RST        →  D1              →  GPIO5
3.3V       →  3.3V
GND        →  GND
```

Cara upload:

1. Buka `wemos_rfid/wemos_rfid.ino` di Arduino IDE
2. Pilih Board: **LOLIN(WEMOS) D1 R2 & mini**
3. Pilih port COM yang sesuai
4. Klik Upload
5. Aplikasi akan mendeteksi Wemos secara otomatis di COM3

### Opsi 2: Arduino Uno (baremetal, without library)

⚠️ **PENTING**: Arduino Uno menggunakan logika **5V**, sedangkan RC522 menggunakan **3.3V**.
**Wajib menggunakan level shifter** antara Uno dan RC522 (kecuali Uno diganti
dengan board 3.3V seperti Arduino Pro Mini 3.3V).

Sketch ini menggunakan **Software SPI (bitbang)** — seluruh pin SPI diimplementasikan
secara manual melalui kode, bukan hardware SPI. Metode ini berguna jika pin hardware SPI
Uno (10=D10/SS, 11=D11/MOSI, 12=D12/MISO, 13=D13/SCK) mengalami kerusakan.

Wiring dengan level shifter:

```
RC522      →  Level Shifter  →  Arduino Uno
SDA (SS)   →  LV1 (HV1)      →  Pin 7
RST        →  LV2 (HV2)      →  Pin 9
MOSI       →  LV3 (HV3)      →  Pin 6
MISO       →  LV4 (HV4)      →  Pin 5
SCK        →  LV5 (HV5)      →  Pin 4
3.3V       →  LV             →  (GND via shifter)
GND        →  GND            →  GND
             HV              →  5V
```

Atau jika menggunakan pembagi tegangan resistor pada setiap jalur SPI:

```
RC522 SDA ← 3.3V ← [1kΩ] ── [2.2kΩ] → GND
                         ↑
                  Pin 7 Uno (5V)
```

(Langkah yang sama berlaku untuk SCK, MOSI, RST. Khusus MISO arahnya berkebalikan,
dari RC522 ke Uno — tegangan 3.3V masuk ke Uno dan tetap dianggap sebagai logic HIGH.)

Upload `arduino_rfid/arduino_rfid.ino` ke Arduino Uno melalui Arduino IDE.

### Opsi 3: Mode Simulasi (tanpa hardware)

Tidak perlu menggunakan Arduino/Wemos. Buka menu **Pengaturan** → aktifkan **Mode Simulasi**,
atau klik tombol **"Kartu Valid"** / **"Kartu Tidak Valid"** pada tampilan Guest.

### Perbandingan Opsi Hardware

| Aspek | Wemos D1 Mini | Arduino Uno |
|-------|---------------|-------------|
| Tegangan logika | 3.3V ✅ sesuai | 5V ❌ perlu level shifter |
| Library RFID | MFRC522 (oleh Miguel Balboa) | Software SPI bitbang (buatan sendiri) |
| Komunikasi SPI | Hardware SPI (built-in) | Software SPI (bitbang) |
| Pin SPI | Fixed (D5-D7) | Bebas (dapat dipilih sendiri) |
| Harga board | ~Rp50.000 | ~Rp70.000 |
| Ukuran | Sangat kecil | Besar |
| Memerlukan level shifter? | Tidak | Ya |

## Struktur File

```
rfid_perpustakaan/
├── main.py                    # Entry point aplikasi
├── app.py                     # GUI utama (CustomTkinter)
├── database.py                # Operasi database SQLite
├── serial_reader.py           # Komunikasi serial + mode simulasi
├── db_viewer.py               # GUI untuk melihat database
├── requirements.txt           # Dependencies Python
├── README.md                  # Dokumentasi
│
├── wemos_rfid/
│   └── wemos_rfid.ino         # Sketch Wemos D1 (library MFRC522)
│
├── wemos_test/
│   └── wemos_test.ino         # Testing sketch Wemos (verbose output)
│
├── arduino_rfid/
│   └── arduino_rfid.ino       # Sketch Arduino Uno (baremetal SPI)
│
└── arduino_test/
    └── arduino_test.ino       # Testing sketch Arduino (blink + serial)
```

## Database

Database SQLite (`perpustakaan.db`) dibuat secara otomatis saat pertama kali
aplikasi dijalankan.

Terdiri dari 2 tabel:

- **mahasiswa** — menyimpan UID, NIM, Nama, Prodi
- **kunjungan** — mencatat UID, NIM, Nama, waktu_masuk, tanggal

## Troubleshooting

**Error `pip install` / module not found:**
```powershell
pip install customtkinter pyserial pandas openpyxl
```

**"Kartu tidak terdeteksi" padahal Wemos menyala:**
- Periksa baudrate pada sketch: harus **115200**
- Periksa wiring, pastikan pin SDA dan RST sesuai
- Output serial aplikasi hanya format `A3:4F:2B:11` (tanpa teks tambahan)
- Coba klik **Refresh** port pada tab Pengaturan

**Error "invalid command name" di terminal:**
Dapat diabaikan, merupakan sisa callback dari proses logout. Sudah diamankan
menggunakan try/except.

**Port COM tidak muncul:**
- Periksa Device Manager → Ports (COM & LPT)
- Cabut dan pasang kembali USB Arduino/Wemos
- Klik **Refresh** pada tab Pengaturan

**Mengganti password admin:**
Buka file `app.py`, cari `password == "admin"`, ganti "admin" dengan password
yang baru.

## Untuk Developer / Kontributor

```powershell
git clone https://github.com/thefulan123/RFID-Perpustakaan-Polban.git
cd RFID-Perpustakaan-Polban
pip install -r requirements.txt
python main.py
```
