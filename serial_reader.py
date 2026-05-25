import serial
import serial.tools.list_ports
import threading
import random
import time


class SerialReader:
    def __init__(self, port=None, baudrate=115200, simulation_mode=False):
        self.port = port
        self.baudrate = baudrate
        self.simulation_mode = simulation_mode
        self.ser = None
        self._running = False
        self._callback = None
        self._thread = None
        self._simulated_uids = [
            "A3:4F:2B:11", "B1:2C:3D:44", "C5:6E:7F:88", "D9:0A:1B:2C",
            "E3:F4:5A:6B", "17:8C:9D:0E", "2F:3A:4B:5C", "6D:7E:8F:9A",
        ]

    def get_available_ports(self):
        ports = serial.tools.list_ports.comports()
        return [p.device for p in ports]

    def _auto_detect_port(self):
        ports = self.get_available_ports()
        for p in ports:
            try:
                s = serial.Serial(p, timeout=0.5)
                s.close()
                return p
            except (serial.SerialException, OSError):
                continue
        return None

    def connect(self):
        if self.simulation_mode:
            self._running = True
            return True

        if self.port is None:
            detected = self._auto_detect_port()
            if detected:
                self.port = detected
            else:
                return False

        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=0.1,
                write_timeout=0.1,
            )
            self._running = True
            return True
        except (serial.SerialException, OSError) as e:
            self.ser = None
            return False

    def disconnect(self):
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1)
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
            except Exception:
                pass
        self.ser = None

    def flush(self):
        if self.ser and self.ser.is_open:
            self.ser.reset_input_buffer()

    def read_uid(self):
        if self.simulation_mode:
            import time
            uid = random.choice(self._simulated_uids)
            time.sleep(random.uniform(0.5, 2.0))
            return uid

        if not self.ser or not self.ser.is_open:
            return None

        try:
            if self.ser.in_waiting > 0:
                raw = self.ser.readline()
                try:
                    data = raw.decode("utf-8").strip()
                except UnicodeDecodeError:
                    return None
                if data and ":" in data:
                    return data
            return None
        except (serial.SerialException, OSError):
            return None

    def set_callback(self, callback):
        self._callback = callback

    def start_background_reading(self):
        if self._thread and self._thread.is_alive():
            return
        self._running = True
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()

    def stop_background_reading(self):
        self._running = False

    def _read_loop(self):
        while self._running:
            uid = self.read_uid()
            if uid and self._callback:
                self._callback(uid)
            if self.simulation_mode:
                time.sleep(0.1)
            else:
                time.sleep(0.05)
