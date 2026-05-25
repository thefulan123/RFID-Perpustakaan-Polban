import sqlite3
import os
from datetime import datetime, timedelta, date

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "perpustakaan.db")


class Database:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        conn = self._connect()
        cur = conn.cursor()
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS mahasiswa (
                uid TEXT PRIMARY KEY,
                nim TEXT UNIQUE NOT NULL,
                nama TEXT NOT NULL,
                prodi TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS kunjungan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uid TEXT,
                nim TEXT,
                nama TEXT,
                waktu_masuk TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tanggal DATE DEFAULT (date('now','localtime')),
                FOREIGN KEY (uid) REFERENCES mahasiswa(uid)
            );

            CREATE INDEX IF NOT EXISTS idx_kunjungan_tanggal ON kunjungan(tanggal);
        """)
        conn.commit()
        conn.close()

    def tambah_mahasiswa(self, uid, nim, nama, prodi):
        conn = self._connect()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO mahasiswa (uid, nim, nama, prodi) VALUES (?, ?, ?, ?)",
                (uid, nim, nama, prodi),
            )
            conn.commit()
            return True, "Mahasiswa berhasil didaftarkan"
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: mahasiswa.uid" in str(e):
                return False, "UID sudah terdaftar"
            elif "UNIQUE constraint failed: mahasiswa.nim" in str(e):
                return False, "NIM sudah terdaftar"
            return False, f"Kesalahan database: {str(e)}"
        finally:
            conn.close()

    def cari_mahasiswa_by_uid(self, uid):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM mahasiswa WHERE uid = ?", (uid,))
        row = cur.fetchone()
        conn.close()
        if row:
            return {
                "uid": row[0],
                "nim": row[1],
                "nama": row[2],
                "prodi": row[3],
                "created_at": row[4],
            }
        return None

    def get_semua_mahasiswa(self):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM mahasiswa ORDER BY nama ASC")
        rows = cur.fetchall()
        conn.close()
        return [
            {
                "uid": r[0],
                "nim": r[1],
                "nama": r[2],
                "prodi": r[3],
                "created_at": r[4],
            }
            for r in rows
        ]

    def hapus_mahasiswa(self, uid):
        conn = self._connect()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM mahasiswa WHERE uid = ?", (uid,))
            if cur.rowcount == 0:
                return False, "Mahasiswa tidak ditemukan"
            conn.commit()
            return True, "Mahasiswa berhasil dihapus"
        except Exception as e:
            return False, f"Kesalahan: {str(e)}"
        finally:
            conn.close()

    def catat_kunjungan(self, uid):
        conn = self._connect()
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM mahasiswa WHERE uid = ?", (uid,))
            mhs = cur.fetchone()
            if not mhs:
                return False, "Kartu tidak terdaftar"
            today = date.today().isoformat()
            cur.execute(
                "INSERT INTO kunjungan (uid, nim, nama, tanggal) VALUES (?, ?, ?, ?)",
                (mhs[0], mhs[1], mhs[2], today),
            )
            conn.commit()
            waktu = datetime.now().strftime("%H:%M:%S")
            return True, {"nama": mhs[2], "nim": mhs[1], "waktu": waktu}
        except Exception as e:
            return False, f"Kesalahan: {str(e)}"
        finally:
            conn.close()

    def get_kunjungan_hari_ini(self):
        conn = self._connect()
        cur = conn.cursor()
        today = date.today().isoformat()
        cur.execute(
            "SELECT * FROM kunjungan WHERE tanggal = ? ORDER BY waktu_masuk DESC",
            (today,),
        )
        rows = cur.fetchall()
        conn.close()
        return [
            {"id": r[0], "uid": r[1], "nim": r[2], "nama": r[3], "waktu_masuk": r[4], "tanggal": r[5]}
            for r in rows
        ]

    def get_semua_kunjungan(self):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM kunjungan ORDER BY waktu_masuk DESC")
        rows = cur.fetchall()
        conn.close()
        return [
            {"id": r[0], "uid": r[1], "nim": r[2], "nama": r[3], "waktu_masuk": r[4], "tanggal": r[5]}
            for r in rows
        ]

    def get_statistik(self):
        conn = self._connect()
        cur = conn.cursor()
        today = date.today().isoformat()
        stats = {}

        cur.execute("SELECT COUNT(*) FROM kunjungan WHERE tanggal = ?", (today,))
        stats["total_hari_ini"] = cur.fetchone()[0]

        start_minggu = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d")
        cur.execute(
            "SELECT COUNT(*) FROM kunjungan WHERE tanggal >= ?", (start_minggu,)
        )
        stats["total_minggu_ini"] = cur.fetchone()[0]

        start_bulan = datetime.now().strftime("%Y-%m-01")
        cur.execute(
            "SELECT COUNT(*) FROM kunjungan WHERE tanggal >= ?", (start_bulan,)
        )
        stats["total_bulan_ini"] = cur.fetchone()[0]

        cur.execute(
            "SELECT strftime('%H', waktu_masuk) as jam, COUNT(*) as cnt FROM kunjungan WHERE tanggal = ? GROUP BY jam ORDER BY cnt DESC LIMIT 1",
            (today,),
        )
        jam_tersibuk = cur.fetchone()
        stats["jam_tersibuk"] = f"{jam_tersibuk[0]}:00-{int(jam_tersibuk[0])+1}:00" if jam_tersibuk else "-"

        hari_map = {0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis", 4: "Jumat", 5: "Sabtu", 6: "Minggu"}
        cur.execute(
            "SELECT strftime('%w', tanggal) as hari, COUNT(*) as cnt FROM kunjungan WHERE tanggal >= ? GROUP BY hari ORDER BY cnt DESC LIMIT 1",
            (start_minggu,),
        )
        hari_tersibuk = cur.fetchone()
        stats["hari_tersibuk"] = hari_map.get(int(hari_tersibuk[0]), "-") if hari_tersibuk else "-"

        conn.close()
        return stats

    def import_dari_excel(self, filepath):
        try:
            import pandas as pd
        except ImportError:
            return False, "Library pandas tidak terinstall. Jalankan: pip install pandas openpyxl"

        try:
            df = pd.read_excel(filepath)
            required = {"uid", "nim", "nama"}
            if not required.issubset(df.columns):
                return False, f"Kolom wajib: uid, nim, nama. Ditemukan: {list(df.columns)}"

            conn = self._connect()
            cur = conn.cursor()
            sukses = 0
            gagal = 0
            for _, row in df.iterrows():
                try:
                    cur.execute(
                        "INSERT OR IGNORE INTO mahasiswa (uid, nim, nama, prodi) VALUES (?, ?, ?, ?)",
                        (str(row["uid"]), str(row["nim"]), str(row["nama"]), str(row.get("prodi", ""))),
                    )
                    if cur.rowcount > 0:
                        sukses += 1
                    else:
                        gagal += 1
                except Exception:
                    gagal += 1
            conn.commit()
            conn.close()
            return True, f"Import selesai. {sukses} berhasil, {gagal} gagal (duplikat)"
        except Exception as e:
            return False, f"Gagal import Excel: {str(e)}"

    def export_ke_excel(self, filepath):
        try:
            import pandas as pd
        except ImportError:
            return False, "Library pandas tidak terinstall. Jalankan: pip install pandas openpyxl"

        try:
            data = self.get_semua_kunjungan()
            df = pd.DataFrame(data)
            if not df.empty:
                df = df.drop(columns=["id", "uid"], errors="ignore")
            df.to_excel(filepath, index=False)
            return True, f"Data berhasil diexport ke {filepath}"
        except Exception as e:
            return False, f"Gagal export Excel: {str(e)}"

    def bulk_insert_mahasiswa(self, list_of_dicts):
        conn = self._connect()
        cur = conn.cursor()
        sukses = 0
        gagal = 0
        for m in list_of_dicts:
            try:
                cur.execute(
                    "INSERT OR IGNORE INTO mahasiswa (uid, nim, nama, prodi) VALUES (?, ?, ?, ?)",
                    (m["uid"], m["nim"], m["nama"], m.get("prodi", "")),
                )
                if cur.rowcount > 0:
                    sukses += 1
                else:
                    gagal += 1
            except Exception:
                gagal += 1
        conn.commit()
        conn.close()
        return sukses, gagal

    def cari_mahasiswa(self, keyword):
        conn = self._connect()
        cur = conn.cursor()
        pattern = f"%{keyword}%"
        cur.execute(
            "SELECT * FROM mahasiswa WHERE nama LIKE ? OR nim LIKE ? OR uid LIKE ? ORDER BY nama ASC",
            (pattern, pattern, pattern),
        )
        rows = cur.fetchall()
        conn.close()
        return [
            {
                "uid": r[0],
                "nim": r[1],
                "nama": r[2],
                "prodi": r[3],
                "created_at": r[4],
            }
            for r in rows
        ]
