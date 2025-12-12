from __future__ import annotations

import logging
import sys
from typing import Optional

import serial
from serial.tools import list_ports

logger = logging.getLogger(__name__)


def serial_ports(
    timeout: float = 1.0, verify_access: bool = True
) -> list[tuple[str, str]]:
    """Lists available and accessible serial ports with descriptions

    :param timeout:
        Timeout in seconds when opening ports for verification (default: 1.0)
    :param verify_access:
        If True, only returns ports that can be opened. If False, returns all detected ports (default: True)
    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of tuples (port_name, description) of the serial ports on the system
    """
    ports = list(list_ports.comports())
    result: list[tuple[str, str]] = []

    for port in ports:
        # PySerial returns None for ports without metadata (e.g., some USB adapters)
        # Normalize to empty string to maintain consistent type and avoid errors in client code
        description = port.description if port.description is not None else ""
        
        if verify_access:
            # Opening the port is the only reliable way to verify actual accessibility
            # The system may list ports that are locked by other processes (Arduino IDE, minicom, etc.)
            # or require special permissions (e.g., not being in dialout group on Linux)
            try:
                with serial.Serial(port.device, timeout=timeout):
                    result.append((port.device, description))
            # OSError captures permission/device issues, SerialException captures port-specific errors
            # We separate both because they require different solutions (permissions vs hardware)
            except (OSError, serial.SerialException) as e:
                logger.debug(
                    f"Port {port.device} is not accessible: {type(e).__name__}: {e}"
                )
        else:
            result.append((port.device, description))
    
    return result


def format_ports_output(ports: list[tuple[str, str]]) -> str:
    """Formats the list of ports as a string for display
    
    :param ports:
        List of tuples (port_name, description)
    :returns:
        Formatted string with port information
    """
    if not ports:
        return "No serial port is being used"
    
    lines = ["Available serial ports:\n"]
    for port, description in ports:
        port_info = f"* {port}"
        if description:
            port_info += f" - {description}"
        lines.append(port_info)
    
    return "\n".join(lines)


def main() -> int:
    """Main entry point for the CLI
    
    :returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        ports = serial_ports()
        output = format_ports_output(ports)
        print(output)
        return 0
    except Exception as e:
        logger.error(f"Error listing serial ports: {type(e).__name__}: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1
