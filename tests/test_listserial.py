from unittest.mock import Mock, patch

import pytest
import serial

from listserial import main, serial_ports


class MockPort:
    """Mock class for serial port objects"""

    def __init__(self, device, description):
        self.device = device
        self.description = description


@pytest.fixture
def mock_comports():
    """Fixture to provide mock serial ports"""
    return [
        MockPort("/dev/ttyS0", "Serial Port 0"),
        MockPort("/dev/ttyS1", "Serial Port 1"),
        MockPort("/dev/ttyS2", "Serial Port 2"),
    ]


@patch("serial.tools.list_ports.comports")
@patch("serial.Serial")
def test_serial_ports_all_available(mock_serial, mock_list_ports, mock_comports):
    """Test serial_ports function when all ports are available"""
    # Setup mocks
    mock_list_ports.return_value = mock_comports
    mock_serial.return_value = Mock()

    # Call function
    result = serial_ports()

    # Verify results
    assert len(result) == 3
    assert result[0] == ("/dev/ttyS0", "Serial Port 0")
    assert result[1] == ("/dev/ttyS1", "Serial Port 1")
    assert result[2] == ("/dev/ttyS2", "Serial Port 2")
    assert mock_serial.call_count == 3


@patch("serial.tools.list_ports.comports")
@patch("serial.Serial")
def test_serial_ports_some_unavailable(mock_serial, mock_list_ports, mock_comports):
    """Test serial_ports function when some ports raise exceptions"""
    # Setup mocks
    mock_list_ports.return_value = mock_comports

    # Make second port unavailable
    def side_effect(port, **kwargs):
        if port == "/dev/ttyS1":
            raise serial.SerialException("Access denied")
        return Mock()

    mock_serial.side_effect = side_effect

    # Call function
    result = serial_ports()

    # Verify results
    assert len(result) == 2
    assert result[0] == ("/dev/ttyS0", "Serial Port 0")
    assert result[1] == ("/dev/ttyS2", "Serial Port 2")


@patch("listserial.serial_ports")
@patch("builtins.print")
def test_main_no_ports(mock_print, mock_serial_ports):
    """Test main function when no ports are available"""
    mock_serial_ports.return_value = []

    main()

    mock_print.assert_called_once_with("No serial port is being used")


@patch("listserial.serial_ports")
@patch("builtins.print")
def test_main_with_ports(mock_print, mock_serial_ports):
    """Test main function when ports are available"""
    mock_serial_ports.return_value = [
        ("/dev/ttyS0", "Serial Port 0"),
        ("/dev/ttyS1", ""),
    ]

    main()

    # Check that print was called with the expected arguments
    assert mock_print.call_count == 3  # Header + 2 ports
    mock_print.assert_any_call("Available serial ports:\n")
    mock_print.assert_any_call("* /dev/ttyS0 - Serial Port 0")
    mock_print.assert_any_call("* /dev/ttyS1")
