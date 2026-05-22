#!/usr/bin/env python3
"""
Serial Communication Module for Arduino Nano
PRO Stable Version
"""

import serial
import serial.tools.list_ports
import json
import time
import threading
from queue import Queue, Empty


class NanoSerial:
    def __init__(self, port, baudrate=115200, logger=None):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.logger = logger
        self.running = False
        self.callback = None
        self.receive_queue = Queue()
        self.relay_ack_queue = Queue()
        self.read_thread = None
        self.last_lcd_time = 0
        self.lcd_delay = 0.12  # smoother timing
        self._write_lock = threading.Lock()
        self.last_send_time = 0
        self.send_delay = 0.08

    def _log_serial(self, level, message):
        if not self.logger:
            return

        log_method = getattr(self.logger, level, None)
        if callable(log_method):
            log_method(message)
        else:
            self.logger.info(message)

    def _format_json_message(self, payload):
        return json.dumps(payload, separators=(",", ":"), ensure_ascii=True)

    def _handle_non_json_line(self, raw_line):
        if raw_line.startswith("[DEBUG]"):
            debug_message = raw_line[7:].strip()

            if 'RX RAW:' in debug_message and '"type":"display"' in debug_message:
                return

            if 'deserializeJson gagal' in debug_message:
                self._log_serial("warning", f"[ARDUINO DEBUG] {debug_message}")
                return

            self._log_serial("debug", f"[ARDUINO DEBUG] {debug_message}")
            return

        self._log_serial("warning", f"[SERIAL] Non JSON: {raw_line}")

    def _is_relay_ack(self, data, expected_action=None):
        if not isinstance(data, dict):
            return False
        if data.get("type") != "ack":
            return False
        if data.get("device") != "relay":
            return False
        if expected_action is None:
            return True
        return data.get("action") == expected_action

    def _dispatch_incoming_message(self, data, invoke_callback=True):
        if self._is_relay_ack(data):
            self.relay_ack_queue.put(data)

        self.receive_queue.put(data)

        if invoke_callback and self.callback:
            self.callback(data)

    def _drain_relay_ack_queue(self):
        while True:
            try:
                self.relay_ack_queue.get_nowait()
            except Empty:
                return

    def _wait_for_relay_ack_from_queue(self, expected_action, timeout):
        deadline = time.time() + timeout

        while time.time() < deadline:
            remaining = deadline - time.time()
            try:
                message = self.relay_ack_queue.get(timeout=min(0.2, max(remaining, 0.01)))
            except Empty:
                continue

            action = message.get("action")
            if action == expected_action:
                self._log_serial("info", f"[ACK OK] relay {expected_action}")
                return True

            if action == "timeout-close":
                self._log_serial("info", "[RX] relay timeout-close")
                continue

            self._log_serial("warning", f"[RX] unexpected relay ack: {message}")

        self._log_serial("warning", f"[ACK TIMEOUT] relay {expected_action}")
        return False

    def _wait_for_relay_ack_direct(self, expected_action, timeout):
        if not self.ser or not self.ser.is_open:
            self._log_serial("warning", f"[ACK TIMEOUT] relay {expected_action}")
            return False

        original_timeout = self.ser.timeout
        deadline = time.time() + timeout

        try:
            while time.time() < deadline:
                remaining = deadline - time.time()
                self.ser.timeout = min(0.2, max(remaining, 0.01))
                raw_line = self.ser.readline().decode("utf-8", errors="ignore").strip()
                if not raw_line:
                    continue

                self._log_serial("info", f"[RX] {raw_line}")

                try:
                    data = json.loads(raw_line)
                except json.JSONDecodeError:
                    self._handle_non_json_line(raw_line)
                    continue

                self._dispatch_incoming_message(data, invoke_callback=False)

                if not self._is_relay_ack(data):
                    continue

                action = data.get("action")
                if action == expected_action:
                    self._log_serial("info", f"[ACK OK] relay {expected_action}")
                    return True

                if action == "timeout-close":
                    self._log_serial("info", "[RX] relay timeout-close")
                    continue

                self._log_serial("warning", f"[RX] unexpected relay ack: {data}")
        finally:
            self.ser.timeout = original_timeout

        self._log_serial("warning", f"[ACK TIMEOUT] relay {expected_action}")
        return False

    def _wait_for_relay_ack(self, expected_action, timeout=3.0):
        read_loop_alive = (
            self.running and
            self.read_thread and
            self.read_thread.is_alive()
        )

        if read_loop_alive and threading.current_thread() is not self.read_thread:
            return self._wait_for_relay_ack_from_queue(expected_action, timeout)

        return self._wait_for_relay_ack_direct(expected_action, timeout)

    # ================= CONNECT =================
    def connect(self):
        try:
            self.ser = serial.Serial(
                self.port,
                self.baudrate,
                timeout=1,
                write_timeout=1
            )

            # Opening the port resets many Nano boards. Clear stale bytes first,
            # then wait long enough for setup() to finish before sending commands.
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()

            # setup() does I2C/LCD/keypad init before emitting the boot JSON.
            time.sleep(1.8)

            if self.logger:
                self.logger.info(f"[SERIAL] Connected at {self.port}")

            return True

        except Exception as e:
            if self.logger:
                self.logger.error(f"[SERIAL] Connection failed: {e}")
            return False

    # ================= DISCONNECT =================
    def disconnect(self):
        self.running = False

        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=2)

        if self.ser and self.ser.is_open:
            self.ser.close()

        if self.logger:
            self.logger.info("[SERIAL] Disconnected")

    # ================= SEND JSON =================
    def send_json(self, payload):

        if not self.ser or not self.ser.is_open:
            if self.logger:
                self.logger.warning("[SERIAL] Not connected")
            return False

        try:
            message = self._format_json_message(payload) + "\n"
            with self._write_lock:
                now = time.time()
                wait_time = self.send_delay - (now - self.last_send_time)
                if wait_time > 0:
                    time.sleep(wait_time)
                self.ser.write(message.encode("utf-8"))
                self.ser.flush()
                self.last_send_time = time.time()

            self._log_serial("info", f"[TX] {message.strip()}")

            return True

        except Exception as e:
            if self.logger:
                self.logger.error(f"[SERIAL] Send failed: {e}")
            return False

    # ================= DISPLAY =================
    def send_display(self, lines):

        now = time.time()
        if now - self.last_lcd_time < self.lcd_delay:
            time.sleep(self.lcd_delay - (now - self.last_lcd_time))

        while len(lines) < 4:
            lines.append("")

        lines = [str(line)[:20] for line in lines[:4]]

        payload = {
            "type": "display",
            "lines": lines
        }

        self.last_lcd_time = time.time()
        return self.send_json(payload)

    # ================= RELAY =================
    def _send_relay_with_ack(self, action="open", duration=5, ack_timeout=3.0, retries=3):
        payload = {
            "type": "actuator",
            "device": "relay",
            "action": action,
            "duration": int(duration or 0)
        }

        self._log_serial("info", f"[RELAY] dispatch {self._format_json_message(payload)}")

        for attempt in range(1, retries + 1):
            self._drain_relay_ack_queue()

            if not self.send_json(payload):
                self._log_serial("warning", f"[TX FAIL] relay {action} attempt {attempt}/{retries}")
                time.sleep(0.1)
                continue

            if self._wait_for_relay_ack(action, timeout=ack_timeout):
                return True

            if attempt < retries:
                self._log_serial("warning", f"[RETRY] relay {action} attempt {attempt + 1}/{retries}")

            time.sleep(0.1)

        return False

    def open_door(self, duration=5, ack_timeout=3.0, retries=3):
        return self._send_relay_with_ack(
            action="open",
            duration=duration,
            ack_timeout=ack_timeout,
            retries=retries,
        )

    def close_door(self, ack_timeout=3.0, retries=3):
        return self._send_relay_with_ack(
            action="close",
            duration=0,
            ack_timeout=ack_timeout,
            retries=retries,
        )

    def send_relay(self, action="open", duration=5, ack_timeout=3.0, retries=3):
        if action == "open":
            time.sleep(0.15)
            return self.open_door(duration=duration, ack_timeout=ack_timeout, retries=retries)
        if action == "close":
            return self.close_door(ack_timeout=ack_timeout, retries=retries)

        self._log_serial("warning", f"[RELAY] Unsupported action: {action}")
        return False

    # ================= READ LOOP =================
    def _read_loop(self):

        while self.running:

            try:
                if self.ser and self.ser.in_waiting > 0:

                    line = self.ser.readline().decode("utf-8", errors="ignore").strip()

                    if line:

                        if self.logger:
                            self.logger.debug(f"[SERIAL RECV] {line}")

                        try:
                            data = json.loads(line)
                            self._log_serial("info", f"[RX] {line}")
                            self._dispatch_incoming_message(data)

                        except json.JSONDecodeError:
                            self._handle_non_json_line(line)

                time.sleep(0.03)

            except Exception as e:
                if self.logger:
                    self.logger.error(f"[SERIAL] Read error: {e}")
                time.sleep(0.5)

    # ================= START READ LOOP =================
    def start_read_loop(self, callback=None):

        self.callback = callback
        self.running = True

        self.read_thread = threading.Thread(
            target=self._read_loop,
            daemon=True
        )

        self.read_thread.start()

        if self.logger:
            self.logger.info("[SERIAL] Read loop started")

    # ================= GET MESSAGE =================
    def get_message(self, timeout=None):
        try:
            return self.receive_queue.get(timeout=timeout)
        except:
            return None


# ================= AUTO DETECT =================
def find_arduino_port(logger=None):

    ports = serial.tools.list_ports.comports()

    for port in ports:
        if any(k in port.description for k in
               ["Arduino", "CH340", "USB Serial", "CP210"]):
            if logger:
                logger.info(f"[SERIAL] Found at {port.device}")
            return port.device

    if logger:
        logger.warning("[SERIAL] Arduino not detected")

    return None