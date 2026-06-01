# Luminous Rex Clock Project Status (Linux Fork)

## Overview
This project is a Linux-exclusive fork of the Luminous Rex clock update tool. It has been refactored to prioritize standard serial communication and debugging on Linux systems.

## Current Configuration
- **Driver:** Linux Standard Serial (`pyserial`)
- **Port:** Default `/dev/ttyUSB0` (configurable via CLI)
- **Baudrate:** 1,000,000
- **Logging:** Enabled by default (configurable via CLI)
- **Line Endings:** LF (Linux standard)

## Accomplishments
1.  **Linux Refactor:** Stripped out legacy drivers. The project now exclusively uses `pyserial`.
2.  **Hexadecimal Logging:** Implemented `log_write` and `log_read` wrappers for debugging.
3.  **64-bit Protocol Fix:** Enforced explicit 4-byte integers and little-endian alignment in the protocol.
4.  **CLI Arguments:** Added `argparse` support for port, brightness, and custom ISO 8601 time.
5.  **Codebase Cleanup:** Standardized line endings and removed trailing whitespace.
6.  **Testing Framework:** Added a `MockClock` simulation and unit tests.

## Usage Instructions
```bash
# Sync with system time (default)
python3 python/lrexclock.py

# Sync with custom port and brightness
python3 python/lrexclock.py --port /dev/ttyUSB1 --brightness 128

# Sync with custom ISO 8601 time
python3 python/lrexclock.py --time 2026-12-25T00:00:00
```

## CLI Arguments
| Argument | Description | Default |
| :--- | :--- | :--- |
| `-p`, `--port` | Serial port path | `/dev/ttyUSB0` |
| `-b`, `--brightness` | Brightness (0-255) | `255` |
| `-t`, `--time` | ISO 8601 time string | System Time |
| `-d`, `--debug` | Enable hex I/O logging | `True` |
| `--no-debug` | Disable hex I/O logging | `False` |

## Testing Approach
A robust testing framework is included in `python/test_lrexclock.py` to allow for development without physical hardware.

### Mock Clock Simulation
- **`MockSerial`**: A simulation class that mimics the Luminous Rex hardware protocol. It maintains an internal EEPROM state and handles 16-byte command packets and 128-byte data payloads.
- **Protocol Validation**: Tests verify that struct packing/unpacking matches the hardware's expected little-endian, 4-byte integer format.

### Test Coverage
The suite covers all core CLI and logic paths:
- **System Time Sync**: Default behavior using the local system clock.
- **ISO 8601 Parsing**: Verification of custom timestamp handling.
- **Brightness Control**: Validation of brightness values (0-255) across all fields.
- **Logging Toggles**: Verification that `--debug` and `--no-debug` correctly control output.
- **Port Selection**: Ensuring custom `/dev/` paths are passed correctly to the driver.

### Running Tests
To run the test suite:
```bash
cd python
python3 test_lrexclock.py
```

## Hardware Notes
- **Reset Behavior:** The clock may reset its internal epoch to `946684800` on power cycle.
- **Brightness Range:** 0-255.
