import unittest
import struct
import datetime
import time
from io import BytesIO
from unittest.mock import MagicMock, patch, ANY
import sys

# Import the script
import lrexclock

class MockSerial:
    """Simulates a serial port and the Luminous Rex clock hardware logic."""
    def __init__(self):
        self.read_buffer = BytesIO()
        self.write_history = []

        # Internal "EEPROM" state
        self.version = 3
        self.timestamp_initialized = 0
        self.timestamp = 946684800 # 2000-01-01
        self.brightness_hours = 100
        self.brightness_minutes = 100
        self.brightness_seconds = 100
        self.is_24_hour = 1
        self.calibration_value = 0
        self.padding = b'\x00' * 110

    def write(self, data):
        self.write_history.append(data)

        # If it's a 16-byte command packet
        if len(data) == 16:
            cmd = data[0]
            if cmd == 4: # CMD_READ_EEPROM_STRUCT
                response = struct.pack(
                    '<IIIBBBBh110s',
                    self.version, self.timestamp_initialized, self.timestamp,
                    self.brightness_hours, self.brightness_minutes,
                    self.brightness_seconds, self.is_24_hour,
                    self.calibration_value, self.padding
                )
                self.read_buffer = BytesIO(response)
            elif cmd == 3: # CMD_WRITE_EEPROM_STRUCT
                self.read_buffer = BytesIO(b'\x00') # OK

        # If it's the 128-byte payload packet
        elif len(data) == 128:
            (self.version, self.timestamp_initialized, self.timestamp,
             self.brightness_hours, self.brightness_minutes,
             self.brightness_seconds, self.is_24_hour,
             self.calibration_value, self.padding) = struct.unpack(
                '<IIIBBBBh110s', data
            )
            self.read_buffer = BytesIO(b'\x00') # OK

    def read(self, n):
        return self.read_buffer.read(n)

class TestLrexClockCLI(unittest.TestCase):

    @patch('serial.Serial')
    @patch('time.time')
    @patch('time.localtime')
    def test_sync_system_time_default(
        self, mock_localtime, mock_time, mock_serial
    ):
        """Test syncing with default system time."""
        mock_dev = MockSerial()
        mock_serial.return_value = mock_dev

        # Fixed "now" time: 2026-01-01 12:00:00 UTC
        fixed_now = 1767268800
        mock_time.return_value = fixed_now

        # Mock localtime to return non-DST (offset 0 for simplicity)
        mock_lt = MagicMock()
        mock_lt.tm_isdst = 0
        mock_localtime.return_value = mock_lt

        with patch('time.timezone', 0):
            with patch('sys.argv', ['lrexclock.py']):
                lrexclock.main()

        # Verify clock state
        self.assertEqual(mock_dev.timestamp, fixed_now)
        self.assertEqual(mock_dev.brightness_hours, 255) # Default
        self.assertEqual(mock_dev.brightness_minutes, 255)
        self.assertEqual(mock_dev.brightness_seconds, 255)

    @patch('serial.Serial')
    def test_custom_iso_time(self, mock_serial):
        """Test syncing with a specific ISO 8601 time string."""
        mock_dev = MockSerial()
        mock_serial.return_value = mock_dev

        target_iso = "2026-12-25T10:00:00"
        dt = datetime.datetime.fromisoformat(target_iso)
        expected_ts = int(dt.timestamp())

        with patch('sys.argv', ['lrexclock.py', '--time', target_iso]):
            lrexclock.main()

        self.assertEqual(mock_dev.timestamp, expected_ts)

    @patch('serial.Serial')
    def test_custom_brightness(self, mock_serial):
        """Test setting a custom brightness level."""
        mock_dev = MockSerial()
        mock_serial.return_value = mock_dev

        with patch('sys.argv', ['lrexclock.py', '--brightness', '128']):
            lrexclock.main()

        self.assertEqual(mock_dev.brightness_hours, 128)
        self.assertEqual(mock_dev.brightness_minutes, 128)
        self.assertEqual(mock_dev.brightness_seconds, 128)

    @patch('serial.Serial')
    @patch('builtins.print')
    def test_debug_logging_output(self, mock_print, mock_serial):
        """Test that TX/RX logs are printed when debug is enabled (default)."""
        mock_dev = MockSerial()
        mock_serial.return_value = mock_dev

        with patch('sys.argv', ['lrexclock.py']):
            lrexclock.main()

        # Check if "TX:" and "RX:" were printed
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        self.assertTrue(any(s.startswith("TX:") for s in print_calls))
        self.assertTrue(any(s.startswith("RX:") for s in print_calls))

    @patch('serial.Serial')
    @patch('builtins.print')
    def test_no_debug_logging(self, mock_print, mock_serial):
        """Test that TX/RX logs are suppressed when --no-debug is used."""
        mock_dev = MockSerial()
        mock_serial.return_value = mock_dev

        with patch('sys.argv', ['lrexclock.py', '--no-debug']):
            lrexclock.main()

        # Check if "TX:" and "RX:" were NOT printed
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        self.assertFalse(any(s.startswith("TX:") for s in print_calls))
        self.assertFalse(any(s.startswith("RX:") for s in print_calls))

    @patch('serial.Serial')
    def test_custom_port(self, mock_serial):
        """Test that the script attempts to open the specified port."""
        mock_dev = MockSerial()
        mock_serial.return_value = mock_dev

        custom_port = "/dev/ttyUSB9"
        with patch('sys.argv', ['lrexclock.py', '--port', custom_port]):
            lrexclock.main()

        mock_serial.assert_called_once_with(custom_port, 1000000, timeout=1)

if __name__ == '__main__':
    # Add the current directory to sys.path so we can import lrexclock
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    unittest.main()
