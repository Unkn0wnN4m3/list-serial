import glob
import sys

import serial

# inspired by https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python?__cf_chl_tk=sRttuoRZRJoPKNFlEp3L6qAr_Y6WXl8KGTsQkzg4vdo-1748131557-1.0.1.1-CGa.p9qYeX3r45SujttJU20sGGU5PTK0X7gfwXiGMIs


def serial_ports() -> list[tuple[str, str]]:
    """Lists serial port names with descriptions

    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of tuples (port_name, description) of the serial ports available on the system
    """
    if sys.platform.startswith("win"):
        from serial.tools import list_ports

        return [(port.device, port.description) for port in list_ports.comports()]
    elif sys.platform.startswith("linux") or sys.platform.startswith("cygwin"):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob("/dev/tty[A-Za-z]*")
    elif sys.platform.startswith("darwin"):
        ports = glob.glob("/dev/tty.*")
    else:
        raise EnvironmentError("Unsupported platform")

    result = []

    # For Linux/Mac we don't have built-in descriptions, so we'll just use the port name
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append((port, ""))
        except (OSError, serial.SerialException):
            pass
    return result


def main() -> None:
    ports = serial_ports()

    if not ports:
        print("No serial port is being used")
    else:
        print("Serial ports:\n")

        for port, description in ports:
            port_info = f"- {port}"
            if description:
                port_info += f" ({description})"
            print("\t" + port_info)
