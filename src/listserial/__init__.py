import sys

import serial


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
        import glob

        # this excludes your current terminal "/dev/tty"
        ports = glob.glob("/dev/tty[A-Za-z]*")
    elif sys.platform.startswith("darwin"):
        import glob

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
        print("Available serial ports:\n")

        for port, description in ports:
            port_info = f"{port}"
            if description:
                port_info += f" - {description}"
            print("* " + port_info)
