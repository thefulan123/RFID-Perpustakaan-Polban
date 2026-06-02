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

## Koneksi Hardware RFID

### Opsi 1: Wemos D1 Mini (RECOMMENDED)

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

Wiring:

```
RC522      →  Arduino Uno
SDA (SS)   →  Pin 7
RST        →  Pin 9
MOSI       →  Pin 6
MISO       →  Pin 5
SCK        →  Pin 4
3.3V       →  3.3V
GND        →  GND
```

Upload `arduino_rfid/arduino_rfid.ino` ke Arduino Uno lewat Arduino IDE.

> **Catatan**: Sketch Arduino Uno pake Software SPI (bitbang), jadi pin BEBAS.
> Ini khusus untuk board yang pin 10/13 hardware SPI-nya rusak.

### Opsi 3: Mode Simulasi (tanpa hardware)

Gasah pake Arduino/Wemos. Buka **Pengaturan** → nyalakan **Mode Simulasi**,
atau tinggal klik **"Kartu Valid"** / **"Kartu Tidak Valid"** di layar Guest.

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
