# Luminous Rex Clock Update Tool (Linux Fork)

This is a Linux-exclusive fork of the Luminous Rex clock update tool. It has been refactored to work specifically with standard serial devices (e.g., `/dev/ttyUSB0`) on Linux systems.

## Key Features (Linux Only)
- **Serial Port Communication:** Uses `pyserial` for broad compatibility with Linux USB-to-Serial bridges.
- **I/O Capture & Logging:** Includes a `DEBUG` mode that provides a hexadecimal dump of all transmitted (`TX`) and received (`RX`) data.
- **64-bit Compatible:** Fixed protocol alignment issues that cause crashes on 64-bit Linux distributions.
- **Simplified Configuration:** No proprietary FTDI drivers required; works with standard kernel drivers.

## Getting Started
See the [python directory](./python) for installation and usage instructions specific to Linux.
