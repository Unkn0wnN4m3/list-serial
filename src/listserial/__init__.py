def serial_ports() -> list[tuple[str, str]]:
    """Lists serial port names with descriptions

    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of tuples (port_name, description) of the serial ports available on the system
    """
    from serial.tools import list_ports

    return [(port.device, port.description) for port in list_ports.comports()]


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
