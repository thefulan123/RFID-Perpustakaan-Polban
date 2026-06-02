import customtkinter as ctk
from datetime import datetime
import threading

from database import Database
from serial_reader import SerialReader

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

HIJAU = "#2CC985"
MERAH = "#E55A5A"
KUNING = "#F5A623"
ORANYE = "#FF8C00"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistem Pendataan Pengunjung Perpustakaan - POLBAN")
        self.geometry("1100x700")
        self.minsize(1100, 700)

        self.db = Database()
        self.serial_reader = SerialReader(simulation_mode=True)
        self.role = None

        self._seed_demo_data()

        self._registration_mode = False
        self._pending_uid = None
        self._last_uid = None
        self._last_uid_time = None
        self._app_running = False
        self._poll_counter = 0

        self._show_login()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _show_login(self):
        self.login_frame = ctk.CTkFrame(self, corner_radius=15)
        self.login_frame.pack(fill="both", expand=True, padx=0, pady=0)

        self.login_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)

        container = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            container,
            text="SISTEM PENDATAAN PENGUNJUNG\nPERPUSTAKAAN BERBASIS RFID",
            font=ctk.CTkFont(size=24, weight="bold"),
            justify="center",
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            container,
            text="Politeknik Negeri Bandung",
            font=ctk.CTkFont(size=14),
            text_color="gray",
        ).pack(pady=(0, 30))

        ctk.CTkLabel(
            container,
            text="Pilih Jenis Masuk",
            font=ctk.CTkFont(size=16),
        ).pack(pady=(0, 15))

        btn_admin = ctk.CTkButton(
            container, text="Admin", width=250, height=45,
            command=self._login_admin, font=ctk.CTkFont(size=15),
        )
        btn_admin.pack(pady=5)

        btn_guest = ctk.CTkButton(
            container, text="Guest", width=250, height=45,
            command=self._login_guest, font=ctk.CTkFont(size=15),
            fg_color="gray", hover_color="darkgray",
        )
        btn_guest.pack(pady=5)

    def _logout(self):
        self._app_running = False
        self.serial_reader.disconnect()
        for w in self.winfo_children():
            w.destroy()
        self.role = None
        self._registration_mode = False
        self._pending_uid = None
        self._show_login()

    def _login_admin(self):
        dialog = ctk.CTkInputDialog(
            text="Masukkan password admin:", title="Verifikasi Admin",
        )
        password = dialog.get_input()
        if password == "admin":
            self.role = "admin"
            self.login_frame.destroy()
            self._setup_ui("admin")
            self.serial_reader.simulation_mode = False
            if not self.serial_reader.connect():
                self.serial_reader.simulation_mode = True
            else:
                self.serial_reader.flush()
            self._start_background_tasks()
        else:
            import tkinter.messagebox as mb
            mb.showerror("Error", "Password salah!")

    def _login_guest(self):
        self.role = "guest"
        self.login_frame.destroy()
        self._setup_ui("guest")
        self.serial_reader.simulation_mode = False
        if not self.serial_reader.connect():
            self.serial_reader.simulation_mode = True
        else:
            self.serial_reader.flush()
        self._start_background_tasks()

    def _setup_ui(self, role):
        if role == "guest":
            self.title("Sistem Pendataan Pengunjung Perpustakaan - POLBAN (Guest)")
            self._build_guest_view()
            return

        self.tab_view = ctk.CTkTabview(self, corner_radius=10)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_monitoring = self.tab_view.add("Monitoring")
        self.tab_manajemen = self.tab_view.add("Manajemen Kartu")
        self.tab_pengaturan = self.tab_view.add("Pengaturan")

        self._build_monitoring_tab()
        self._build_manajemen_tab()
        self._build_pengaturan_tab()

    def _build_guest_view(self):
        self.geometry("800x500")
        self.minsize(800, 500)

        self._guest_header = ctk.CTkFrame(self, fg_color="transparent")
        self._guest_header.pack(fill="x", padx=20, pady=(15, 5))

        ctk.CTkLabel(
            self._guest_header,
            text="SISTEM PENDATAAN PENGUNJUNG PERPUSTAKAAN",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(side="left")

        self.time_label = ctk.CTkLabel(self._guest_header, text="", font=ctk.CTkFont(size=14))
        self.time_label.pack(side="right")

        btn_logout = ctk.CTkButton(
            self._guest_header, text="Logout", command=self._logout, width=70, height=28,
            fg_color="transparent", border_width=1, text_color=("gray90", "gray90"),
            font=ctk.CTkFont(size=12),
        )
        btn_logout.pack(side="right", padx=(0, 10))

        ctk.CTkLabel(
            self,
            text="Silahkan Tap Kartu RFID Anda",
            font=ctk.CTkFont(size=18),
        ).pack(pady=(20, 5))

        self.scan_area = ctk.CTkFrame(
            self, height=200, corner_radius=15, border_width=2, border_color="gray"
        )
        self.scan_area.pack(fill="x", padx=80, pady=10)
        self.scan_area.pack_propagate(False)

        self.status_icon = ctk.CTkLabel(
            self.scan_area, text="●", font=ctk.CTkFont(size=56), text_color=KUNING,
        )
        self.status_icon.pack(pady=(30, 5))

        self.status_text = ctk.CTkLabel(
            self.scan_area, text="Menunggu kartu...", font=ctk.CTkFont(size=18),
        )
        self.status_text.pack()

        self.last_scan_label = ctk.CTkLabel(
            self.scan_area, text="", font=ctk.CTkFont(size=14), text_color="gray",
        )
        self.last_scan_label.pack(pady=(5, 0))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(pady=15)

        self.btn_random = ctk.CTkButton(
            btn_row, text="Kartu Valid", command=self._random_scan, width=130, height=40,
        )
        self.btn_random.pack(side="left", padx=5)

    def _build_monitoring_tab(self):
        self._mon_header = ctk.CTkFrame(self.tab_monitoring, fg_color="transparent")
        self._mon_header.pack(fill="x", padx=20, pady=(15, 5))

        ctk.CTkLabel(
            self._mon_header,
            text="SISTEM PENDATAAN PENGUNJUNG PERPUSTAKAAN",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(side="left")

        self.time_label = ctk.CTkLabel(
            self._mon_header, text="", font=ctk.CTkFont(size=14)
        )
        self.time_label.pack(side="right")

        ctk.CTkButton(
            self._mon_header, text="Logout", command=self._logout, width=70, height=28,
            fg_color="transparent", border_width=1, text_color=("gray90", "gray90"),
            font=ctk.CTkFont(size=12),
        ).pack(side="right", padx=(0, 10))

        main_row = ctk.CTkFrame(self.tab_monitoring, fg_color="transparent")
        main_row.pack(fill="both", expand=True, padx=20, pady=5)

        left_col = ctk.CTkFrame(main_row, corner_radius=10)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))

        ctk.CTkLabel(
            left_col,
            text="TEMPELKAN KARTU RFID",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=(20, 10))

        self.scan_area = ctk.CTkFrame(
            left_col, height=180, corner_radius=15, border_width=2, border_color="gray"
        )
        self.scan_area.pack(fill="x", padx=30, pady=10)
        self.scan_area.pack_propagate(False)

        self.status_icon = ctk.CTkLabel(
            self.scan_area,
            text="●",
            font=ctk.CTkFont(size=48),
            text_color=KUNING,
        )
        self.status_icon.pack(pady=(25, 5))

        self.status_text = ctk.CTkLabel(
            self.scan_area,
            text="Menunggu kartu...",
            font=ctk.CTkFont(size=16),
        )
        self.status_text.pack()

        self.last_scan_label = ctk.CTkLabel(
            self.scan_area,
            text="",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        )
        self.last_scan_label.pack(pady=(5, 0))

        self.port_status = ctk.CTkLabel(
            left_col,
            text="Mode: Simulasi",
            font=ctk.CTkFont(size=12),
            text_color=KUNING,
        )
        self.port_status.pack(pady=(5, 5))

        btn_row = ctk.CTkFrame(left_col, fg_color="transparent")
        btn_row.pack(pady=(0, 15))

        self.btn_random = ctk.CTkButton(
            btn_row, text="Kartu Valid", command=self._random_scan, width=130, height=35
        )
        self.btn_random.pack(side="left", padx=5)

        self.btn_invalid = ctk.CTkButton(
            btn_row, text="Kartu Tidak Valid", command=self._invalid_scan, width=130, height=35,
            fg_color=MERAH, hover_color="#C44"
        )
        self.btn_invalid.pack(side="left", padx=5)

        right_col = ctk.CTkFrame(main_row, corner_radius=10, width=400)
        right_col.pack(side="right", fill="y")
        right_col.pack_propagate(False)

        ctk.CTkLabel(
            right_col,
            text="STATISTIK KUNJUNGAN",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=(15, 10))

        self.stat_hari_ini = ctk.CTkLabel(
            right_col, text="Hari Ini: 0", font=ctk.CTkFont(size=14)
        )
        self.stat_hari_ini.pack(anchor="w", padx=20, pady=2)

        self.stat_minggu_ini = ctk.CTkLabel(
            right_col, text="Minggu Ini: 0", font=ctk.CTkFont(size=14)
        )
        self.stat_minggu_ini.pack(anchor="w", padx=20, pady=2)

        self.stat_bulan_ini = ctk.CTkLabel(
            right_col, text="Bulan Ini: 0", font=ctk.CTkFont(size=14)
        )
        self.stat_bulan_ini.pack(anchor="w", padx=20, pady=2)

        ctk.CTkLabel(
            right_col,
            text="\nPENGUNJUNG TERAKHIR",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=(15, 5))

        self.last_visitor_frame = ctk.CTkFrame(
            right_col, corner_radius=10, border_width=1, border_color="gray"
        )
        self.last_visitor_frame.pack(fill="x", padx=20, pady=5)

        self.last_nama = ctk.CTkLabel(
            self.last_visitor_frame, text="Nama: -", font=ctk.CTkFont(size=13)
        )
        self.last_nama.pack(anchor="w", padx=15, pady=(10, 2))

        self.last_nim = ctk.CTkLabel(
            self.last_visitor_frame, text="NIM: -", font=ctk.CTkFont(size=13)
        )
        self.last_nim.pack(anchor="w", padx=15, pady=2)

        self.last_waktu = ctk.CTkLabel(
            self.last_visitor_frame, text="Waktu: -", font=ctk.CTkFont(size=13)
        )
        self.last_waktu.pack(anchor="w", padx=15, pady=(2, 10))

        riwayat_frame = ctk.CTkFrame(self.tab_monitoring, corner_radius=10)
        riwayat_frame.pack(fill="both", expand=True, padx=20, pady=10)

        riwayat_header = ctk.CTkFrame(riwayat_frame, fg_color="transparent")
        riwayat_header.pack(fill="x", padx=15, pady=(10, 5))

        ctk.CTkLabel(
            riwayat_header,
            text="RIWAYAT KUNJUNGAN HARI INI",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(side="left")

        btn_frame = ctk.CTkFrame(riwayat_header, fg_color="transparent")
        btn_frame.pack(side="right")

        self.btn_export = ctk.CTkButton(
            btn_frame, text="Export Excel", command=self._export_excel, width=120
        )
        self.btn_export.pack(side="left", padx=5)

        cols = ["No", "Nama", "NIM", "Waktu"]
        col_widths = [50, 250, 130, 150]
        table_frame = ctk.CTkFrame(riwayat_frame, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=15, pady=(5, 10))

        header_row = ctk.CTkFrame(table_frame, fg_color=("gray85", "gray20"), corner_radius=5)
        header_row.pack(fill="x")

        for col, w in zip(cols, col_widths):
            ctk.CTkLabel(header_row, text=col, font=ctk.CTkFont(size=13, weight="bold"), width=w).pack(side="left", padx=5, pady=5)

        scroll_frame = ctk.CTkScrollableFrame(table_frame, corner_radius=5)
        scroll_frame.pack(fill="both", expand=True)

        self.riwayat_container = scroll_frame
        self.riwayat_rows = []

    def _build_manajemen_tab(self):
        form_frame = ctk.CTkFrame(self.tab_manajemen, corner_radius=10)
        form_frame.pack(fill="x", padx=20, pady=(15, 10))

        ctk.CTkLabel(
            form_frame,
            text="DAFTARKAN KARTU RFID BARU",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=(10, 10))

        row1 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row1.pack(fill="x", padx=30, pady=5)

        ctk.CTkLabel(row1, text="UID Kartu:", width=80).pack(side="left")
        self.entry_uid = ctk.CTkEntry(row1, width=200)
        self.entry_uid.pack(side="left", padx=10)
        self.btn_scan_kartu = ctk.CTkButton(
            row1, text="Scan Kartu", command=self._start_registration_mode, width=100
        )
        self.btn_scan_kartu.pack(side="left", padx=5)
        self.reg_status_label = ctk.CTkLabel(row1, text="", font=ctk.CTkFont(size=12))
        self.reg_status_label.pack(side="left", padx=10)

        row2 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row2.pack(fill="x", padx=30, pady=5)
        ctk.CTkLabel(row2, text="NIM:", width=80).pack(side="left")
        self.entry_nim = ctk.CTkEntry(row2, width=200)
        self.entry_nim.pack(side="left", padx=10)

        row3 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row3.pack(fill="x", padx=30, pady=5)
        ctk.CTkLabel(row3, text="Nama:", width=80).pack(side="left")
        self.entry_nama = ctk.CTkEntry(row3, width=300)
        self.entry_nama.pack(side="left", padx=10)

        row4 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row4.pack(fill="x", padx=30, pady=5)
        ctk.CTkLabel(row4, text="Prodi:", width=80).pack(side="left")
        prodi_list = [
            "D3 Teknik Elektronika", "D3 Teknik Informatika",
            "D3 Teknik Elektro", "D3 Teknik Mesin",
            "D3 Teknik Sipil", "D3 Akuntansi", "D3 Administrasi Bisnis",
        ]
        self.combo_prodi = ctk.CTkComboBox(row4, values=prodi_list, width=300)
        self.combo_prodi.set(prodi_list[0])
        self.combo_prodi.pack(side="left", padx=10)

        row5 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row5.pack(fill="x", padx=30, pady=10)
        self.btn_simpan = ctk.CTkButton(
            row5, text="SIMPAN", command=self._simpan_mahasiswa, width=150
        )
        self.btn_simpan.pack(side="left", padx=5)
        self.form_msg = ctk.CTkLabel(row5, text="", font=ctk.CTkFont(size=12))
        self.form_msg.pack(side="left", padx=10)

        daftar_frame = ctk.CTkFrame(self.tab_manajemen, corner_radius=10)
        daftar_frame.pack(fill="both", expand=True, padx=20, pady=10)

        daftar_header = ctk.CTkFrame(daftar_frame, fg_color="transparent")
        daftar_header.pack(fill="x", padx=15, pady=(10, 5))

        ctk.CTkLabel(
            daftar_header,
            text="DAFTAR MAHASISWA TERDAFTAR",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(side="left")

        btn_hdr = ctk.CTkFrame(daftar_header, fg_color="transparent")
        btn_hdr.pack(side="right")

        self.entry_cari = ctk.CTkEntry(btn_hdr, width=180, placeholder_text="Cari nama/NIM/UID...")
        self.entry_cari.pack(side="left", padx=5)
        self.entry_cari.bind("<KeyRelease>", lambda e: self._cari_mahasiswa())

        self.btn_import = ctk.CTkButton(
            btn_hdr, text="Import Excel", command=self._import_excel, width=100
        )
        self.btn_import.pack(side="left", padx=5)

        cols = ["UID", "NIM", "Nama", "Prodi", "Aksi"]
        col_widths = [150, 130, 200, 200, 100]
        tbl_frame = ctk.CTkFrame(daftar_frame, fg_color="transparent")
        tbl_frame.pack(fill="both", expand=True, padx=15, pady=(5, 10))

        hdr_row = ctk.CTkFrame(tbl_frame, fg_color=("gray85", "gray20"), corner_radius=5)
        hdr_row.pack(fill="x")

        for col, w in zip(cols, col_widths):
            ctk.CTkLabel(hdr_row, text=col, font=ctk.CTkFont(size=13, weight="bold"), width=w).pack(side="left", padx=5, pady=5)

        scroll_f = ctk.CTkScrollableFrame(tbl_frame, corner_radius=5)
        scroll_f.pack(fill="both", expand=True)

        self.mahasiswa_container = scroll_f

    def _build_pengaturan_tab(self):
        frame = ctk.CTkFrame(self.tab_pengaturan, corner_radius=10)
        frame.pack(fill="x", padx=40, pady=(30, 10))

        ctk.CTkLabel(
            frame,
            text="PENGATURAN",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(15, 15))

        port_row = ctk.CTkFrame(frame, fg_color="transparent")
        port_row.pack(fill="x", padx=40, pady=5)
        ctk.CTkLabel(port_row, text="Port Serial:", width=120).pack(side="left")
        self.port_var = ctk.StringVar(value="")
        self.combo_port = ctk.CTkComboBox(port_row, values=[], variable=self.port_var, width=200)
        self.combo_port.pack(side="left", padx=10)
        self.btn_refresh_port = ctk.CTkButton(
            port_row, text="Refresh", command=self._refresh_ports, width=80
        )
        self.btn_refresh_port.pack(side="left", padx=5)
        self.btn_test_port = ctk.CTkButton(
            port_row, text="Test Koneksi", command=self._test_koneksi, width=100
        )
        self.btn_test_port.pack(side="left", padx=5)
        self.port_test_label = ctk.CTkLabel(port_row, text="", font=ctk.CTkFont(size=12))
        self.port_test_label.pack(side="left", padx=10)

        sim_row = ctk.CTkFrame(frame, fg_color="transparent")
        sim_row.pack(fill="x", padx=40, pady=5)
        ctk.CTkLabel(sim_row, text="Mode Simulasi:", width=120).pack(side="left")
        self.sim_toggle = ctk.CTkSwitch(
            sim_row, text="Aktif (tanpa Arduino)", command=self._toggle_simulasi
        )
        self.sim_toggle.pack(side="left", padx=10)
        self.sim_toggle.select()

        info_frame = ctk.CTkFrame(self.tab_pengaturan, corner_radius=10)
        info_frame.pack(fill="x", padx=40, pady=10)

        ctk.CTkLabel(
            info_frame,
            text="INFORMASI SISTEM",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=(10, 5))

        info_text = (
            "Aplikasi: Sistem Pendataan Pengunjung Perpustakaan Berbasis RFID\n"
            "Institusi: Politeknik Negeri Bandung\n"
            "Mata Kuliah: Sistem Instrumentasi Elektronika\n"
            "Database: perpustakaan.db (SQLite)\n"
            "Mode Simulasi: Aktif jika tidak ada Arduino terdeteksi"
        )
        ctk.CTkLabel(info_frame, text=info_text, font=ctk.CTkFont(size=12), justify="left").pack(
            anchor="w", padx=30, pady=(5, 15)
        )

    def _start_background_tasks(self):
        self._app_running = True
        self._update_clock()
        self._poll_serial()
        if self.role == "admin":
            self._refresh_monitoring_data()
            self._refresh_mahasiswa_table()
            self._refresh_ports()
        else:
            self._guest_refresh_data()

    def _poll_serial(self):
        if not self.winfo_exists() or not self._app_running:
            return
        if not self.serial_reader.simulation_mode and not self.serial_reader.ser:
            return
        try:
            self._poll_counter += 1
            if self._poll_counter >= 150:
                self._poll_counter = 0
                if not self.serial_reader.simulation_mode and not self.serial_reader.is_connected():
                    self.serial_reader.reconnect()

            if not self.serial_reader.simulation_mode:
                uid = self.serial_reader.read_uid()
                if uid:
                    self._on_uid_received(uid)
        except Exception:
            pass
        finally:
            try:
                self.after(200, self._poll_serial)
            except Exception:
                pass

    def _guest_refresh_data(self):
        if not self.winfo_exists():
            return
        try:
            stats = self.db.get_statistik()
            self.last_scan_label.configure(
                text=f"Pengunjung hari ini: {stats['total_hari_ini']} orang",
                text_color="gray",
            )
        except Exception:
            pass
        self.after(2000, self._guest_refresh_data)

    def _update_clock(self):
        if not self.winfo_exists():
            return
        try:
            now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            self.time_label.configure(text=now)
        except Exception:
            pass
        self.after(1000, self._update_clock)

    def _refresh_monitoring_data(self):
        if not self.winfo_exists():
            return
        try:
            stats = self.db.get_statistik()
            kunjungan = self.db.get_kunjungan_hari_ini()

            self.stat_hari_ini.configure(text=f"Hari Ini: {stats['total_hari_ini']}")
            self.stat_minggu_ini.configure(text=f"Minggu Ini: {stats['total_minggu_ini']}")
            self.stat_bulan_ini.configure(text=f"Bulan Ini: {stats['total_bulan_ini']}")

            for w in self.riwayat_rows:
                w.destroy()
            self.riwayat_rows.clear()

            for i, k in enumerate(kunjungan, 1):
                row = ctk.CTkFrame(self.riwayat_container, fg_color="transparent")
                row.pack(fill="x")
                waktu = k["waktu_masuk"].split(" ")[1][:8] if " " in k["waktu_masuk"] else "-"
                vals = [str(i), k["nama"], k["nim"], waktu]
                widths = [50, 250, 130, 150]
                for v, w in zip(vals, widths):
                    ctk.CTkLabel(row, text=v, width=w, anchor="w").pack(side="left", padx=5, pady=2)
                self.riwayat_rows.append(row)
                if i == 1:
                    self.last_nama.configure(text=f"Nama: {k['nama']}")
                    self.last_nim.configure(text=f"NIM: {k['nim']}")
                    self.last_waktu.configure(text=f"Waktu: {waktu}")
        except Exception as e:
            pass

        self.after(2000, self._refresh_monitoring_data)

    def _on_uid_received(self, uid):
        if self._registration_mode:
            self.after(0, lambda: self._handle_registration_uid(uid))
            return

        now = datetime.now()
        if hasattr(self, '_last_uid_time') and self._last_uid_time:
            if uid == self._last_uid and (now - self._last_uid_time).total_seconds() < 3:
                return
        self._last_uid = uid
        self._last_uid_time = now

        self.after(0, lambda: self._process_scan(uid))

    def _process_scan(self, uid):
        try:
            self.status_icon.configure(text="●", text_color=KUNING)
            self.status_text.configure(text=f"Membaca: {uid}...")

            result = self.db.catat_kunjungan(uid)
            if result[0]:
                data = result[1]
                self.status_icon.configure(text="●", text_color=HIJAU)
                self.status_text.configure(
                    text=f"Selamat datang, {data['nama']}!",
                    text_color=HIJAU,
                )
                self.last_scan_label.configure(text=f"Kartu valid - {data['waktu']}")
                self._flash_scan_area(HIJAU)
            else:
                is_warning = "sudah scan" in result[1].lower()
                color = ORANYE if is_warning else MERAH
                self.status_icon.configure(text="●", text_color=color)
                self.status_text.configure(text=result[1], text_color=color)
                self.last_scan_label.configure(text="")
                self._flash_scan_area(color)
        except Exception:
            pass

        self.after(3000, self._reset_scan_status)

    def _reset_scan_status(self):
        try:
            self.status_icon.configure(text="●", text_color=KUNING)
            self.status_text.configure(text="Menunggu kartu...", text_color=("black", "white"))
            self.last_scan_label.configure(text="")
        except Exception:
            pass

    def _flash_scan_area(self, color):
        try:
            original = self.scan_area.cget("border_color")
            self.scan_area.configure(border_color=color)
            self.after(300, lambda: self._restore_border(original))
        except Exception:
            pass

    def _restore_border(self, original):
        try:
            self.scan_area.configure(border_color=original)
        except Exception:
            pass

    def _start_registration_mode(self):
        self._registration_mode = True
        self.btn_scan_kartu.configure(state="disabled")

        if not self.serial_reader.ser:
            self.serial_reader.simulation_mode = False
            if self.serial_reader.connect():
                self.serial_reader.flush()
                self._poll_serial()
                self.reg_status_label.configure(text="Mode scan aktif... tap kartu RFID", text_color=HIJAU)
            else:
                self.serial_reader.simulation_mode = True
                self.reg_status_label.configure(
                    text="Klik 'Kartu Valid' untuk simulasi UID",
                    text_color=KUNING,
                )
        else:
            self.reg_status_label.configure(text="Mode scan aktif... tap kartu RFID", text_color=HIJAU)

        self.after(15000, self._cancel_registration_mode)

    def _cancel_registration_mode(self):
        self._registration_mode = False
        self.reg_status_label.configure(text="", text_color=KUNING)
        self.btn_scan_kartu.configure(state="normal")

    def _handle_registration_uid(self, uid):
        try:
            self.entry_uid.delete(0, "end")
            self.entry_uid.insert(0, uid)
            self._registration_mode = False
            self.reg_status_label.configure(text=f"UID terbaca: {uid}", text_color=HIJAU)
            self.btn_scan_kartu.configure(state="normal")
        except Exception:
            pass

    def _simpan_mahasiswa(self):
        uid = self.entry_uid.get().strip()
        nim = self.entry_nim.get().strip()
        nama = self.entry_nama.get().strip()
        prodi = self.combo_prodi.get()

        if not uid or not nim or not nama:
            self.form_msg.configure(text="Semua field harus diisi!", text_color=MERAH)
            return

        sukses, pesan = self.db.tambah_mahasiswa(uid, nim, nama, prodi)
        if sukses:
            self.form_msg.configure(text=pesan, text_color=HIJAU)
            self.entry_uid.delete(0, "end")
            self.entry_nim.delete(0, "end")
            self.entry_nama.delete(0, "end")
            self._refresh_mahasiswa_table()
        else:
            self.form_msg.configure(text=pesan, text_color=MERAH)

        self.after(3000, lambda: self.form_msg.configure(text=""))

    def _refresh_mahasiswa_table(self, data=None):
        for w in self.mahasiswa_container.winfo_children():
            w.destroy()
        self.mahasiswa_rows = []

        if data is None:
            data = self.db.get_semua_mahasiswa()

        for m in data:
            row = ctk.CTkFrame(self.mahasiswa_container, fg_color="transparent")
            row.pack(fill="x")
            vals = [m["uid"], m["nim"], m["nama"], m["prodi"]]
            widths = [150, 130, 200, 200]
            for v, w in zip(vals, widths):
                ctk.CTkLabel(row, text=v, width=w, anchor="w").pack(side="left", padx=5, pady=2)
            btn_hapus = ctk.CTkButton(
                row, text="Hapus", width=80, height=25,
                command=lambda u=m["uid"]: self._hapus_mahasiswa(u),
            )
            btn_hapus.pack(side="left", padx=5, pady=2)

    def _cari_mahasiswa(self):
        keyword = self.entry_cari.get().strip()
        if not keyword:
            self._refresh_mahasiswa_table()
            return
        data = self.db.cari_mahasiswa(keyword)
        self._refresh_mahasiswa_table(data)

    def _hapus_mahasiswa(self, uid):
        sukses, pesan = self.db.hapus_mahasiswa(uid)
        if sukses:
            self._refresh_mahasiswa_table()
        else:
            import tkinter.messagebox as mb
            mb.showerror("Error", pesan)

    def _import_excel(self):
        from tkinter import filedialog
        filepath = filedialog.askopenfilename(
            title="Pilih file Excel",
            filetypes=[("Excel files", "*.xlsx *.xls")],
        )
        if not filepath:
            return
        sukses, pesan = self.db.import_dari_excel(filepath)
        import tkinter.messagebox as mb
        if sukses:
            mb.showinfo("Import Excel", pesan)
            self._refresh_mahasiswa_table()
        else:
            mb.showerror("Import Excel", pesan)

    def _export_excel(self):
        from tkinter import filedialog
        today = datetime.now().strftime("%Y-%m-%d")
        default_name = f"kunjungan_{today}.xlsx"
        filepath = filedialog.asksaveasfilename(
            title="Simpan file Excel",
            defaultextension=".xlsx",
            initialfile=default_name,
            filetypes=[("Excel files", "*.xlsx")],
        )
        if not filepath:
            return
        sukses, pesan = self.db.export_ke_excel(filepath)
        import tkinter.messagebox as mb
        if sukses:
            mb.showinfo("Export Excel", pesan)
        else:
            mb.showerror("Export Excel", pesan)

    def _refresh_ports(self):
        if not self.winfo_exists():
            return
        try:
            ports = self.serial_reader.get_available_ports()
            self.combo_port.configure(values=ports if ports else ["Tidak ada port"])
            if ports:
                current = self.port_var.get()
                if current not in ports:
                    self.port_var.set(ports[0])
            else:
                self.port_var.set("Tidak ada port")
        except Exception:
            pass
        self.after(5000, self._refresh_ports)

    def _test_koneksi(self):
        port = self.port_var.get()
        if not port or port == "Tidak ada port":
            self.port_test_label.configure(text="Pilih port terlebih dahulu", text_color=MERAH)
            self.after(3000, lambda: self.port_test_label.configure(text=""))
            return

        self.port_test_label.configure(text="Mengetes...", text_color=KUNING)

        def task():
            import time
            temp_reader = SerialReader(port=port, baudrate=115200, simulation_mode=False)
            hasil = temp_reader.connect()
            if hasil:
                temp_reader.disconnect()
            self.after(0, lambda: self._test_koneksi_result(hasil))

        import threading
        threading.Thread(target=task, daemon=True).start()

    def _test_koneksi_result(self, hasil):
        if hasil:
            self.port_test_label.configure(text="Koneksi berhasil ✓", text_color=HIJAU)
        else:
            self.port_test_label.configure(text="Gagal terhubung ✗", text_color=MERAH)
        self.after(3000, lambda: self.port_test_label.configure(text=""))

    def _random_scan(self):
        import random

        if self._registration_mode:
            uid = f"{random.randint(0,255):02X}:{random.randint(0,255):02X}:{random.randint(0,255):02X}:{random.randint(0,255):02X}"
            self._handle_registration_uid(uid)
            return

        nama_list = [
            "Ujang", "Agus", "Maman", "Entis", "Asep", "Dede", "Yoyo", "Tatang",
            "Dadang", "Usep", "Euis", "Neneng", "Yanti", "Cucu", "Ineu", "Popon",
            "Ade", "Iwan", "Eman", "Koswara", "Jajang", "Cecep", "Dani", "Rudi",
        ]
        nama_belakang = [
            "Suparman", "Hidayat", "Suryana", "Nugraha", "Kusumah", "Permana",
            "Sudrajat", "Wijaya", "Saputra", "Maulana", "Ramdhani", "Sofyan",
            "Rahman", "Firmansyah", "Gunawan", "Junaedi", "Rohman", "Saepudin",
        ]
        prodi_list = [
            "D3 Teknik Elektronika", "D3 Teknik Informatika", "D3 Teknik Elektro",
            "D3 Teknik Mesin", "D3 Teknik Sipil", "D3 Akuntansi", "D3 Administrasi Bisnis",
        ]
        nama = f"{random.choice(nama_list)} {random.choice(nama_belakang)}"
        nim = f"24131{random.randint(1000, 9999)}"
        uid = f"{random.randint(0,255):02X}:{random.randint(0,255):02X}:{random.randint(0,255):02X}:{random.randint(0,255):02X}"
        prodi = random.choice(prodi_list)

        self.db.tambah_mahasiswa(uid, nim, nama, prodi)
        self._process_scan(uid)

    def _invalid_scan(self):
        import random
        uid = f"FF:{random.randint(0,255):02X}:{random.randint(0,255):02X}:{random.randint(0,255):02X}"
        self._process_scan(uid)

    def _toggle_simulasi(self):
        aktif = self.sim_toggle.get()
        self.serial_reader.disconnect()
        self.serial_reader.simulation_mode = aktif
        if aktif:
            self.serial_reader.connect()
            self.port_status.configure(text="Mode: Simulasi", text_color=KUNING)
        else:
            port = self.port_var.get()
            if port and port != "Tidak ada port":
                self.serial_reader.port = port
                self.serial_reader.simulation_mode = False
                if self.serial_reader.connect():
                    self.serial_reader.flush()
                    self._poll_serial()
                    self.port_status.configure(text=f"Port: {port} ✓", text_color=HIJAU)
                else:
                    self.port_status.configure(text="Gagal konek ke port", text_color=MERAH)

    def _seed_demo_data(self):
        data = self.db.get_semua_mahasiswa()
        if data:
            return
        demo = [
            ("A3:4F:2B:11", "241311001", "Ahmad Fauzi", "D3 Teknik Elektronika"),
            ("B1:2C:3D:44", "241311002", "Siti Nurhaliza", "D3 Teknik Informatika"),
            ("C5:6E:7F:88", "241311003", "Rizky Pratama", "D3 Teknik Elektro"),
            ("D9:0A:1B:2C", "241311004", "Dewi Lestari", "D3 Teknik Elektronika"),
            ("E3:F4:5A:6B", "241311005", "Budi Santoso", "D3 Teknik Mesin"),
            ("17:8C:9D:0E", "241311006", "Ani Rahmawati", "D3 Akuntansi"),
            ("2F:3A:4B:5C", "241311007", "Doni Kusuma", "D3 Teknik Informatika"),
            ("6D:7E:8F:9A", "241311008", "Rina Marlina", "D3 Administrasi Bisnis"),
            ("AA:BB:CC:DD", "241311009", "Hendra Gunawan", "D3 Teknik Sipil"),
            ("12:34:56:78", "241311010", "Fitri Handayani", "D3 Teknik Elektronika"),
        ]
        for uid, nim, nama, prodi in demo:
            self.db.tambah_mahasiswa(uid, nim, nama, prodi)

    def _on_close(self):
        self.serial_reader.disconnect()
        self.destroy()
