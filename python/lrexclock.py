"""
This script updates any attached Luminous Rex clock to
the current system time or a specified time.

https://www.luminousrex.com/clocks
"""

import sys
import datetime, time
import struct
import serial
import argparse

def log_write(dev, data, debug=False):
    if debug:
        print(f"TX: {data.hex(' ')}")
    dev.write(data)

def log_read(dev, n, debug=False):
    data = dev.read(n)
    data = bytes(data)
    if debug:
        print(f"RX: {data.hex(' ')}")
    return data

def main():
    parser = argparse.ArgumentParser(
        description="Update Luminous Rex clock time and brightness."
    )
    parser.add_argument(
        "-p", "--port", default="/dev/ttyUSB0",
        help="Serial port (default: /dev/ttyUSB0)"
    )
    parser.add_argument(
        "-b", "--brightness", type=int, default=255,
        help="Brightness 0-255 (default: 255)"
    )
    parser.add_argument(
        "-t", "--time",
        help="ISO 8601 time string (e.g. 2026-05-30T18:00:00). "
             "Defaults to system time."
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", default=True,
        help="Enable hex I/O logging (default: True)"
    )
    parser.add_argument(
        "--no-debug", action="store_false", dest="debug",
        help="Disable hex I/O logging"
    )

    args = parser.parse_args()

    if args.brightness < 0 or args.brightness > 255:
        print("Error: Brightness must be between 0 and 255.")
        sys.exit(1)

    # Command constants
    CMD_WRITE_EEPROM_STRUCT = 3
    CMD_READ_EEPROM_STRUCT = 4
    CMD_RESPONSE_OK = 0

    # Open the device
    try:
        dev = serial.Serial(args.port, 1000000, timeout=1)
    except serial.SerialException as e:
        print(f"Error opening serial port {args.port}: {e}")
        sys.exit(1)

    # 1. Read current state
    cmd = [0] * 16
    cmd[0] = CMD_READ_EEPROM_STRUCT
    log_write(dev, bytes(cmd), args.debug)

    response = log_read(dev, 128, args.debug)
    if len(response) < 128:
        print("Error: Failed to read 128 bytes from clock.")
        sys.exit(1)

    (version, timestamp_initialized, timestamp, brightness_hours,
     brightness_minutes, brightness_seconds, is_24_hour,
     calibration_value, padding) = struct.unpack('<IIIBBBBh110s', response)

    # 2. Determine target time
    if args.time:
        try:
            dt = datetime.datetime.fromisoformat(args.time)
            # If no timezone info, assume local time and convert to epoch
            pc_epoch = int(dt.timestamp())
            pc_offset = 0 # handles local vs utc if tz is present or not
        except ValueError as e:
            print(f"Error parsing time: {e}")
            sys.exit(1)
    else:
        pc_epoch = int(time.time())
        if time.localtime().tm_isdst and time.daylight:
            pc_offset = time.altzone
        else:
            pc_offset = time.timezone

    error_seconds = timestamp - (pc_epoch - pc_offset)

    print(f"Clock epoch: {timestamp}")
    print(f"Target epoch: {pc_epoch - pc_offset}")
    print(f"Lrex clock is {error_seconds} seconds ahead of target\n")

    # 3. Update values
    timestamp = pc_epoch - pc_offset
    brightness_hours = args.brightness
    brightness_minutes = args.brightness
    brightness_seconds = args.brightness

    # 4. Write back
    cmd = [0] * 16
    cmd[0] = CMD_WRITE_EEPROM_STRUCT
    log_write(dev, bytes(cmd), args.debug)

    response = log_read(dev, 1, args.debug)
    if not response or response[0] != CMD_RESPONSE_OK:
        print("Error: Clock did not acknowledge write command.")
        sys.exit(1)

    cmd_data = struct.pack(
        '<IIIBBBBh110s', version, timestamp_initialized, timestamp,
        brightness_hours, brightness_minutes, brightness_seconds,
        is_24_hour, calibration_value, padding
    )
    log_write(dev, bytes(cmd_data), args.debug)

    response = log_read(dev, 1, args.debug)
    if not response or response[0] != CMD_RESPONSE_OK:
        print("Error: Clock did not acknowledge data write.")
        sys.exit(1)
    else:
        print("Clock successfully updated.")

if __name__ == "__main__":
    main()
