import serial


def serial_ports() -> list[tuple[str, str]]:
    """Lists available and accessible serial ports with descriptions

    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of tuples (port_name, description) of the serial ports that can be opened on the system
    """
    from serial.tools import list_ports

    ports = list(list_ports.comports())
    result: list[tuple[str, str]] = []

    # Filter to only include ports we can open
    for port in ports:
        try:
            s = serial.Serial(port.device)
            s.close()
            result.append((port.device, port.description))
        except (OSError, serial.SerialException):
            print(f"Port {port.device} not available")
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
