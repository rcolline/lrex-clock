# Luminous Rex Clock Update Tool (Linux)

This Python script updates your [Luminous Rex clock](https://www.luminousrex.com/clocks) time via a standard serial port on Linux.

## Requirements

1. Python >= 3.6
2. [pyserial](https://pythonhosted.org/pyserial/)

## Installation

Install the required Python library:

```bash
pip3 install pyserial
```

### Permissions
In order to access the USB serial device without root, ensure your user is in the `dialout` group:

```bash
sudo usermod -a -G dialout $USER
```
*(You may need to log out and back in for this to take effect.)*

## Usage

Connect the Luminous Rex clock to a USB port and verify it appears as `/dev/ttyUSB0`.

### Basic Usage
Sync with the current system time:
```bash
python3 lrexclock.py
```

### Advanced Examples
```bash
# Sync using a different serial port
python3 lrexclock.py --port /dev/ttyUSB1

# Set a specific brightness level (mid-range)
python3 lrexclock.py --brightness 128

# Sync to a specific ISO 8601 time/date
python3 lrexclock.py --time 2026-12-25T12:00:00

# Disable hexadecimal debug logging
python3 lrexclock.py --no-debug
```

## CLI Arguments

| Argument | Description | Default |
| :--- | :--- | :--- |
| `-p`, `--port` | Serial port path | `/dev/ttyUSB0` |
| `-b`, `--brightness` | Brightness (0-255) | `255` |
| `-t`, `--time` | ISO 8601 time string | System Time |
| `-d`, `--debug` | Enable hex I/O logging | `True` |
| `--no-debug` | Disable hex I/O logging | `False` |

## Features
- **Protocol Stability:** Uses explicit 4-byte little-endian packing, ensuring compatibility across both 32-bit and 64-bit Linux systems.
- **I/O Capture:** Provides a hexadecimal trace of the raw communication for verification and debugging.
- **Flexible Time:** Supports both automatic system clock synchronization and manual ISO 8601 input.
