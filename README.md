# Sistem Pendataan Pengunjung Perpustakaan Berbasis RFID

Aplikasi desktop untuk mendata pengunjung perpustakaan menggunakan kartu RFID. Dibangun dengan Python dan CustomTkinter sebagai proyek akhir mata kuliah Sistem Instrumentasi Elektronika di Politeknik Negeri Bandung.

## Fitur

- **Monitoring Real-time**: Menampilkan statistik kunjungan harian, mingguan, dan bulanan
- **Scan RFID**: Membaca kartu RFID via Arduino + RC522 dan mencatat kunjungan otomatis
- **Manajemen Kartu**: Daftarkan, cari, dan hapus data mahasiswa
- **Import/Export Excel**: Import data mahasiswa dan export kunjungan ke file Excel
- **Mode Simulasi**: Testing tanpa hardware Arduino
- **Dark Theme**: Tampilan modern dengan tema gelap

## Requirements

- Python **3.10 atau lebih baru**
- Library tercantum di `requirements.txt`

## Cara Install

```bash
pip install -r requirements.txt
```

## Cara Menjalankan

```bash
cd rfid_perpustakaan
python main.py
```

## Koneksi Arduino

1. Upload program RFID ke Arduino Uno
2. Hubungkan Arduino ke komputer via USB
3. Jalankan aplikasi
4. Pilih port COM yang sesuai di tab **Pengaturan**
5. Matikan **Mode Simulasi** untuk menggunakan hardware

### Format Data dari Arduino

Arduino mengirim data UID melalui serial dalam format:
```
A3:4F:2B:11
```

Baudrate: **115200**

## Mode Simulasi

Jika belum memiliki hardware Arduino, aktifkan **Mode Simulasi** di tab Pengaturan. Aplikasi akan menghasilkan UID random untuk testing.

## Struktur Database

Database SQLite (`perpustakaan.db`) dibuat otomatis saat pertama kali aplikasi dijalankan, terdiri dari 2 tabel:

- **mahasiswa**: menyimpan data kartu RFID dan identitas mahasiswa
- **kunjungan**: mencatat setiap kali kartu di-tap

## Struktur File

```
rfid_perpustakaan/
├── main.py            # Entry point
├── app.py             # GUI utama (CustomTkinter)
├── database.py        # Operasi database SQLite
├── serial_reader.py   # Komunikasi serial dengan Arduino
├── requirements.txt   # Dependencies
└── README.md          # Dokumentasi
```

## Troubleshooting

**Aplikasi tidak bisa jalan:**
```bash
pip install -r requirements.txt
```

**Port serial tidak terdeteksi:**
- Pastikan Arduino terhubung via USB
- Cek di Device Manager (Windows) atau `ls /dev/tty*` (Linux)
- Klik tombol **Refresh** di tab Pengaturan
