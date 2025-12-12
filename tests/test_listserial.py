from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
import serial

from listserial import format_ports_output, main, serial_ports


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


@pytest.fixture
def mock_list_ports():
    """Fixture to mock list_ports.comports"""
    with patch("serial.tools.list_ports.comports") as mock:
        yield mock


@pytest.fixture
def mock_serial():
    """Fixture to mock serial.Serial"""
    with patch("serial.Serial") as mock:
        # Make the mock work as a context manager
        mock.return_value.__enter__ = Mock(return_value=Mock())
        mock.return_value.__exit__ = Mock(return_value=False)
        yield mock


def test_serial_ports_all_available(mock_serial, mock_list_ports, mock_comports):
    """Test serial_ports function when all ports are available"""
    # Setup mocks
    mock_list_ports.return_value = mock_comports
    
    # Configure mock to work as context manager
    mock_instance = Mock()
    mock_instance.__enter__ = Mock(return_value=mock_instance)
    mock_instance.__exit__ = Mock(return_value=False)
    mock_serial.return_value = mock_instance

    # Call function
    result = serial_ports()

    # Verify results
    assert len(result) == 3
    assert result[0] == ("/dev/ttyS0", "Serial Port 0")
    assert result[1] == ("/dev/ttyS1", "Serial Port 1")
    assert result[2] == ("/dev/ttyS2", "Serial Port 2")
    assert mock_serial.call_count == 3


def test_serial_ports_some_unavailable(mock_serial, mock_list_ports, mock_comports):
    """Test serial_ports function when some ports raise exceptions"""
    # Setup mocks
    mock_list_ports.return_value = mock_comports

    # Make second port unavailable
    def side_effect(port, **kwargs):
        if port == "/dev/ttyS1":
            raise serial.SerialException("Access denied")
        mock_instance = Mock()
        mock_instance.__enter__ = Mock(return_value=mock_instance)
        mock_instance.__exit__ = Mock(return_value=False)
        return mock_instance

    mock_serial.side_effect = side_effect

    # Call function
    result = serial_ports()

    # Verify results
    assert len(result) == 2
    assert result[0] == ("/dev/ttyS0", "Serial Port 0")
    assert result[1] == ("/dev/ttyS2", "Serial Port 2")


def test_serial_ports_custom_timeout(mock_serial, mock_list_ports, mock_comports):
    """Test serial_ports function with custom timeout"""
    mock_list_ports.return_value = mock_comports
    
    # Configure mock to work as context manager
    mock_instance = Mock()
    mock_instance.__enter__ = Mock(return_value=mock_instance)
    mock_instance.__exit__ = Mock(return_value=False)
    mock_serial.return_value = mock_instance

    result = serial_ports(timeout=2.5)

    assert len(result) == 3
    # Verify timeout parameter was passed
    calls = mock_serial.call_args_list
    assert all(call[1]["timeout"] == 2.5 for call in calls)


def test_serial_ports_without_verification(mock_list_ports, mock_comports):
    """Test serial_ports function without access verification"""
    mock_list_ports.return_value = mock_comports

    result = serial_ports(verify_access=False)

    # Should return all ports without trying to open them
    assert len(result) == 3
    assert result[0] == ("/dev/ttyS0", "Serial Port 0")
    assert result[1] == ("/dev/ttyS1", "Serial Port 1")
    assert result[2] == ("/dev/ttyS2", "Serial Port 2")


def test_serial_ports_none_description(mock_serial, mock_list_ports):
    """Test serial_ports function when description is None"""
    mock_list_ports.return_value = [MockPort("/dev/ttyUSB0", None)]
    
    # Configure mock to work as context manager
    mock_instance = Mock()
    mock_instance.__enter__ = Mock(return_value=mock_instance)
    mock_instance.__exit__ = Mock(return_value=False)
    mock_serial.return_value = mock_instance

    result = serial_ports()

    assert len(result) == 1
    assert result[0] == ("/dev/ttyUSB0", "")


def test_format_ports_output_empty():
    """Test format_ports_output with no ports"""
    result = format_ports_output([])
    assert result == "No serial port is being used"


def test_format_ports_output_with_ports():
    """Test format_ports_output with ports"""
    ports = [
        ("/dev/ttyS0", "Serial Port 0"),
        ("/dev/ttyS1", ""),
    ]
    result = format_ports_output(ports)
    
    expected = "Available serial ports:\n\n* /dev/ttyS0 - Serial Port 0\n* /dev/ttyS1"
    assert result == expected


@patch("listserial.serial_ports")
@patch("builtins.print")
def test_main_no_ports(mock_print, mock_serial_ports):
    """Test main function when no ports are available"""
    mock_serial_ports.return_value = []

    exit_code = main()

    assert exit_code == 0
    mock_print.assert_called_once_with("No serial port is being used")


@patch("listserial.serial_ports")
@patch("builtins.print")
def test_main_with_ports(mock_print, mock_serial_ports):
    """Test main function when ports are available"""
    mock_serial_ports.return_value = [
        ("/dev/ttyS0", "Serial Port 0"),
        ("/dev/ttyS1", ""),
    ]

    exit_code = main()

    assert exit_code == 0
    expected_output = "Available serial ports:\n\n* /dev/ttyS0 - Serial Port 0\n* /dev/ttyS1"
    mock_print.assert_called_once_with(expected_output)


@patch("listserial.serial_ports")
def test_main_with_exception(mock_serial_ports, capsys):
    """Test main function when an exception is raised"""
    mock_serial_ports.side_effect = OSError("Unable to list ports")

    exit_code = main()

    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Error:" in captured.err
