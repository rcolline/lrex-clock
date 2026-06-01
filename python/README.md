# Luminous Rex Clock Update Tool (Linux)

This Python script updates your [Luminous Rex clock](https://www.luminousrex.com/clocks) time via a standard serial port on Linux.

## Requirements

1. Python >= 3.6
2. [pyserial](https://pythonhosted.org/pyserial/)

## Installation

Install the required Python library:

```bash
pip install pyserial
```

### Permissions
In order to access the USB serial device without root, ensure your user is in the `dialout` group:

```bash
sudo usermod -a -G dialout $USER
```
*(You may need to log out and back in for this to take effect.)*

## Usage

Connect the Luminous Rex clock to a USB port and verify it appears as `/dev/ttyUSB0`. Then run:

```bash
python3 lrexclock.py
```

The script will:
1. Synchronize the clock's time with your system clock.
2. Set the display brightness to maximum.
3. Output a hexadecimal trace of the communication if `DEBUG` is enabled.
