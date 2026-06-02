# Sistem Pendataan Pengunjung Perpustakaan Berbasis RFID

Aplikasi desktop untuk mendata pengunjung perpustakaan menggunakan kartu RFID.
Dibangun dengan Python dan CustomTkinter sebagai proyek akhir mata kuliah
Sistem Instrumentasi Elektronika di Politeknik Negeri Bandung.

## Fitur

- **Login Admin/Guest** — Admin (password: `admin`) bisa full akses; Guest cuma tap-in
- **Monitoring Real-time** — Statistik kunjungan harian, mingguan, bulanan
- **Scan RFID** — Baca kartu via Wemos D1 / Arduino Uno + RC522, catat otomatis
- **1 Hari 1 Scan** — Kartu yang udah scan hari ini ditolak dengan peringatan
- **Manajemen Kartu** — Daftar, cari, hapus data mahasiswa
- **Import/Export Excel** — Import mahasiswa, export data kunjungan
- **Mode Simulasi** — Testing tanpa hardware (bisa pake tombol "Kartu Valid")
- **Dark Theme** — Tampilan modern tema gelap

## Requirements (di PC)

| Software | Keterangan |
|----------|------------|
| **Windows 10/11** | Aplikasi ini untuk Windows |
| **Python 3.10 – 3.13** | Python 3.14 **BELUM support** (pake 3.11 aja) |
| **pip** | Biasanya udah include sama Python |

## Cara Install (CLI)

Buka **PowerShell** atau **Command Prompt**, lalu:

```powershell
# 1. Pastikan Python udah keinstall
python --version
# output: Python 3.11.x

# 2. Masuk ke folder aplikasi
cd E:\Aplikasi Perpustakaan POLBAN\rfid_perpustakaan

# 3. Install semua dependencies
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
| **Guest** | (langsung masuk) | Tap-in aja, tombol Kartu Valid |

## Elektrikal

### Spesifikasi Modul RC522

| Parameter | Nilai |
|-----------|-------|
| Tegangan operasi | **3.3V DC** (⚠️ JANGAN pake 5V! Bisa rusak) |
| Arus operasi | ~13–26 mA (standby), ~80 mA (baca kartu) |
| Frekuensi RF | 13.56 MHz (HF — High Frequency) |
| Protokol komunikasi | **SPI** (SCK, MOSI, MISO, SDA/SS) + RST |
| Jarak baca | ~2–5 cm (tergantung kartu dan antena) |
| Kartu compatible | MIFARE Classic 1K/4K, MIFARE Ultralight, NTAG |
| Chip | NXP MFRC522 |

### Logika Tegangan (3.3V vs 5V)

- **RC522** adalah modul **3.3V**. Semua pin I/O (SDA, SCK, MOSI, MISO, RST) HANYA
  boleh diberi tegangan **maks 3.3V**. Kalo dipaksa 5V, chip MFRC522 bisa rusak
  permanen.
- **Wemos D1 Mini (ESP8266)** sudah **3.3V native** — semua GPIO-nya 3.3V. Cocok
  langsung disambung ke RC522 tanpa level shifter.
- **Arduino Uno** punya logika **5V** di pin I/O. Kalo Arduino Uno dipake langsung
  ke RC522 tanpa level shifter, tegangan 5V dari pin MOSI/MISO/SCK/SDA bisa
  ngerusak RC522 dalam jangka panjang.

### Level Shifter (wajib untuk Arduino Uno)

Karena Arduino Uno output-nya 5V, perlu **level shifter** (konverter tegangan)
antara Uno dan RC522. Ada beberapa opsi:

1. **Modul level shifter 4-channel** (recommended) — $1-2 di toko elektronik.
   Wiring: HV (5V) ke Uno, LV (3.3V) ke RC522.
2. **Pembagi tegangan resistor** — pake 2 resistor (1kΩ + 2.2kΩ) tiap jalur SPI.
   Cuma nurunin tegangan dari 5V ke ~3.3V, tapi arah MISO perlu diatur beda.
3. **Modul RC522 khusus 5V** — beberapa versi modul RC522 udah include regulator
   3.3V dan level shifter bawaan.

⚠️ **Peringatan**: Walaupun beberapa orang bilang "langsung colok aja" Uno ke
RC522 tanpa level shifter, ini **tidak disarankan** untuk proyek permanen.
Tegangan 5V perlahan ngerusak input 3.3V chip MFRC522.

### Konsumsi Daya

| Komponen | Tegangan | Arus |
|----------|----------|------|
| Wemos D1 Mini (aktif + WiFi) | 3.3V | ~80–200 mA |
| Arduino Uno (aktif) | 5V (via USB/Vin) | ~50–100 mA |
| Modul RC522 (baca kartu) | 3.3V | ~80 mA |
| **Total (Wemos + RC522)** | **3.3V** | **~160–280 mA** |
| **Total (Uno + RC522)** | **5V + 3.3V** | **~130–180 mA** |

Keduanya bisa dicolok langsung ke USB komputer (500 mA max), tanpa adaptor
tambahan.

### Jarak dan Antena

- Jarak baca maksimal RC522 ~2–5 cm tergantung bentuk kartu/tag
- Untuk jarak optimal, tempelkan kartu sejajar dengan modul (parallel), bukan
  tegak lurus
- Antena RC522 ada di dalam PCB modul (coil printed circuit board)

---

## Koneksi Hardware RFID

### Opsi 1: Wemos D1 Mini (RECOMMENDED)

Wemos D1 Mini berbasis ESP8266 dengan logika **3.3V**, jadi cocok langsung
dengan RC522 tanpa level shifter. Komunikasi SPI via hardware SPI.

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
5. Aplikasi otomatis detek Wemos di COM3

### Opsi 2: Arduino Uno (baremetal, no library)

⚠️ **PENTING**: Arduino Uno pake logika **5V**, RC522 pake **3.3V**.
**Wajib pake level shifter** antara Uno dan RC522 (kecuali Uno diganti
dengan yang 3.3V kayak Arduino Pro Mini 3.3V).

Sketch ini pake **Software SPI (bitbang)** — semua pin SPI diimplementasikan
manual lewat kode, bukan hardware SPI. Ini berguna kalo pin hardware SPI
Uno (10=D10/SS, 11=D11/MOSI, 12=D12/MISO, 13=D13/SCK) ada yang rusak.

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

Atau kalo pake pembagi tegangan resistor tiap jalur SPI:

```
RC522 SDA ← 3.3V ← [1kΩ] ── [2.2kΩ] → GND
                         ↑
                  Pin 7 Uno (5V)
```

(Sama untuk SCK, MOSI, RST. Khusus MISO arahnya sebaliknya dari RC522 ke Uno,
jadi aman — 3.3V masuk ke Uno dianggap sebagai logic HIGH.)

Upload `arduino_rfid/arduino_rfid.ino` ke Arduino Uno lewat Arduino IDE.

### Opsi 3: Mode Simulasi (tanpa hardware)

Gasah pake Arduino/Wemos. Buka **Pengaturan** → nyalakan **Mode Simulasi**,
atau tinggal klik **"Kartu Valid"** / **"Kartu Tidak Valid"** di layar Guest.

### Perbandingan Opsi Hardware

| Aspek | Wemos D1 Mini | Arduino Uno |
|-------|---------------|-------------|
| Tegangan logika | 3.3V ✅ cocok | 5V ❌ perlu level shifter |
| Library RFID | MFRC522 (by Miguel Balboa) | Software SPI bitbang (buatan sendiri) |
| Komunikasi SPI | Hardware SPI (built-in) | Software SPI (bitbang) |
| Pin SPI | Fixed (D5-D7) | Bebas (pilih sendiri) |
| Harga board | ~Rp50.000 | ~Rp70.000 |
| Ukuran | Sangat kecil | Besar |
| Butuh level shifter? | Tidak | Ya |

## Struktur File

```
rfid_perpustakaan/
├── main.py                    # Entry point aplikasi
├── app.py                     # GUI utama (CustomTkinter)
├── database.py                # Operasi database SQLite
├── serial_reader.py           # Komunikasi serial + mode simulasi
├── db_viewer.py               # GUI untuk liat database
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

Database SQLite (`perpustakaan.db`) dibuat otomatis saat pertama jalan.

2 tabel:

- **mahasiswa** — UID, NIM, Nama, Prodi
- **kunjungan** — UID, NIM, Nama, waktu_masuk, tanggal

## Troubleshooting

**`pip install` error / module not found:**
```powershell
pip install customtkinter pyserial pandas openpyxl
```

**"Kartu tidak terdeteksi" padahal Wemos nyala:**
- Cek baudrate di sketch: harus **115200**
- Cek wiring, pastiin pin SDA & RST sesuai
- Aplikasi output Serial cuma format `A3:4F:2B:11` (tanpa teks tambahan)
- Coba klik **Refresh** port di tab Pengaturan

**Error "invalid command name" di terminal:**
Abaikan, itu cuma sisa callback dari logout. Udah diamankan pake try/except.

**Port COM tidak muncul:**
- Cek Device Manager → Ports (COM & LPT)
- Cabut pasang USB Arduino/Wemos
- Klik **Refresh** di tab Pengaturan

**Mau ganti password admin:**
Buka `app.py`, cari `password == "admin"`, ganti "admin" dengan password baru.

## Untuk Developer / Kontributor

```powershell
git clone https://github.com/thefulan123/RFID-Perpustakaan-Polban.git
cd RFID-Perpustakaan-Polban
pip install -r requirements.txt
python main.py
```
