import customtkinter as ctk
import sqlite3
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "perpustakaan.db")

class DBViewer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Database Viewer - Perpustakaan POLBAN")
        self.geometry("800x500")

        tab = ctk.CTkTabview(self, corner_radius=10)
        tab.pack(fill="both", expand=True, padx=10, pady=10)

        tab_mhs = tab.add("Mahasiswa")
        tab_kun = tab.add("Kunjungan")

        self._build_tabel(tab_mhs, "mahasiswa")
        self._build_tabel(tab_kun, "kunjungan")

        btn = ctk.CTkButton(self, text="Refresh", command=self._refresh_all)
        btn.pack(pady=5)

    def _build_tabel(self, parent, tabel):
        frame = ctk.CTkScrollableFrame(parent, corner_radius=5)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        setattr(self, f"_{tabel}_container", frame)

    def _refresh_all(self):
        for t in ("mahasiswa", "kunjungan"):
            self._refresh_tabel(t)

    def _refresh_tabel(self, tabel):
        container = getattr(self, f"_{tabel}_container")
        for w in container.winfo_children():
            w.destroy()

        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM {tabel}")
            rows = cur.fetchall()
            conn.close()
        except Exception:
            rows = []

        for i, row in enumerate(rows):
            f = ctk.CTkFrame(container, fg_color="transparent")
            f.pack(fill="x", padx=5, pady=1)
            ctk.CTkLabel(f, text=str(i+1), width=40, anchor="w").pack(side="left")
            for val in row:
                ctk.CTkLabel(f, text=str(val), width=150, anchor="w").pack(side="left", padx=5)

if __name__ == "__main__":
    DBViewer().mainloop()
