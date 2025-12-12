from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
import serial

from listserial import format_ports_output, main, serial_ports


class MockPort:
    """Minimal mock that avoids importing the heavy serial.tools.list_ports infrastructure
    
    We only need device and description, the rest of ListPortInfo attributes
    (hwid, vid, pid, etc.) are not used in the logic under test
    """

    def __init__(self, device, description):
        self.device = device
        self.description = description


@pytest.fixture
def mock_comports():
    """Standard dataset of 3 ports to verify multi-port scenarios
    
    We use multiple ports instead of just one because iteration and filtering
    behavior is critical (common bugs: returning only the first one,
    losing intermediate ports, etc.)
    """
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
    """Mock serial.Serial to avoid real hardware dependencies in tests
    
    Without this, tests would fail in environments without serial ports (CI/CD, containers)
    or could interfere with real connected hardware
    """
    with patch("serial.Serial") as mock:
        # Context manager protocol required because code uses "with serial.Serial(...)"
        # Without __enter__/__exit__ it would fail with AttributeError
        mock.return_value.__enter__ = Mock(return_value=Mock())
        mock.return_value.__exit__ = Mock(return_value=False)
        yield mock


def test_serial_ports_all_available(mock_serial, mock_list_ports, mock_comports):
    """Validates the happy path where all detected ports are accessible
    
    This is the ideal but rare scenario in practice (usually there are phantom ports
    or ports in use by other processes)
    """
    mock_list_ports.return_value = mock_comports
    
    # Context manager setup duplicated here because fixture doesn't persist between tests
    # (each test reconfigures the mock according to its specific scenario)
    mock_instance = Mock()
    mock_instance.__enter__ = Mock(return_value=mock_instance)
    mock_instance.__exit__ = Mock(return_value=False)
    mock_serial.return_value = mock_instance

    result = serial_ports()

    assert len(result) == 3
    assert result[0] == ("/dev/ttyS0", "Serial Port 0")
    assert result[1] == ("/dev/ttyS1", "Serial Port 1")
    assert result[2] == ("/dev/ttyS2", "Serial Port 2")
    # Verify that each port was tested individually (critical for verify_access logic)
    assert mock_serial.call_count == 3


def test_serial_ports_some_unavailable(mock_serial, mock_list_ports, mock_comports):
    """Ensures that locked/inaccessible ports are filtered without breaking the process
    
    Common scenario: Arduino IDE has a port open, or the user lacks permissions.
    The function should continue and return available ports instead of failing completely
    """
    mock_list_ports.return_value = mock_comports

    # Simulate port in use by another process (e.g., Arduino IDE, minicom, another script instance)
    def side_effect(port, **kwargs):
        if port == "/dev/ttyS1":
            raise serial.SerialException("Access denied")
        mock_instance = Mock()
        mock_instance.__enter__ = Mock(return_value=mock_instance)
        mock_instance.__exit__ = Mock(return_value=False)
        return mock_instance

    mock_serial.side_effect = side_effect

    result = serial_ports()

    # The locked port should be silently excluded from the results
    assert len(result) == 2
    assert result[0] == ("/dev/ttyS0", "Serial Port 0")
    assert result[1] == ("/dev/ttyS2", "Serial Port 2")


def test_serial_ports_custom_timeout(mock_serial, mock_list_ports, mock_comports):
    """Validates that timeout is correctly propagated to PySerial
    
    Important for slow devices (e.g., GPS, old modems) that take time to respond.
    Without configurable timeout, the code would hang with slow hardware
    """
    mock_list_ports.return_value = mock_comports
    
    mock_instance = Mock()
    mock_instance.__enter__ = Mock(return_value=mock_instance)
    mock_instance.__exit__ = Mock(return_value=False)
    mock_serial.return_value = mock_instance

    result = serial_ports(timeout=2.5)

    assert len(result) == 3
    # Critical: timeout must reach serial.Serial to prevent hangs with unresponsive hardware
    calls = mock_serial.call_args_list
    assert all(call[1]["timeout"] == 2.5 for call in calls)


def test_serial_ports_without_verification(mock_list_ports, mock_comports):
    """Tests fast listing mode without opening ports
    
    Useful for quick discovery where it doesn't matter if ports are accessible
    (e.g., showing complete list to user for selection, system debugging).
    Trade-off: speed over accuracy
    """
    mock_list_ports.return_value = mock_comports

    result = serial_ports(verify_access=False)

    # All ports returned, even if they would fail to open
    # (none are attempted to be opened, that's why we don't need mock_serial)
    assert len(result) == 3
    assert result[0] == ("/dev/ttyS0", "Serial Port 0")
    assert result[1] == ("/dev/ttyS1", "Serial Port 1")
    assert result[2] == ("/dev/ttyS2", "Serial Port 2")


def test_serial_ports_none_description(mock_serial, mock_list_ports):
    """Covers edge case where PySerial returns None in description
    
    Happens with some cheap USB adapters without EEPROM or generic drivers.
    We must normalize to "" to maintain consistent tuple[str, str] type and avoid
    client code having to check for None
    """
    mock_list_ports.return_value = [MockPort("/dev/ttyUSB0", None)]
    
    mock_instance = Mock()
    mock_instance.__enter__ = Mock(return_value=mock_instance)
    mock_instance.__exit__ = Mock(return_value=False)
    mock_serial.return_value = mock_instance

    result = serial_ports()

    # None converted to "" for type consistency
    assert len(result) == 1
    assert result[0] == ("/dev/ttyUSB0", "")


def test_format_ports_output_empty():
    """Ensures user-friendly message when there are no ports
    
    Avoids empty/confusing output that would make the user think the command failed.
    Explicit message helps distinguish "no ports" from "broken command"
    """
    result = format_ports_output([])
    assert result == "No serial port is being used"


def test_format_ports_output_with_ports():
    """Validates correct formatting of ports with and without description
    
    Port without description ("") case is important: it should not add " - " 
    at the end (would look ugly and confusing). Mix of both types is
    the most common real scenario
    """
    ports = [
        ("/dev/ttyS0", "Serial Port 0"),
        ("/dev/ttyS1", ""),  # No description: should not add " - "
    ]
    result = format_ports_output(ports)
    
    expected = "Available serial ports:\n\n* /dev/ttyS0 - Serial Port 0\n* /dev/ttyS1"
    assert result == expected


@patch("listserial.serial_ports")
@patch("builtins.print")
def test_main_no_ports(mock_print, mock_serial_ports):
    """Validates that absence of ports is NOT an error
    
    Exit code 0 because "no ports" is a valid system state, not a failure.
    Exit code 1 would break scripts that use this command and expect only
    technical errors to return != 0
    """
    mock_serial_ports.return_value = []

    exit_code = main()

    # Exit 0 because no ports is a valid state, not an error
    assert exit_code == 0
    mock_print.assert_called_once_with("No serial port is being used")


@patch("listserial.serial_ports")
@patch("builtins.print")
def test_main_with_ports(mock_print, mock_serial_ports):
    """Integration test for complete happy path CLI flow
    
    Verifies that the complete pipeline (serial_ports -> format -> print) works.
    This is the test that would catch regressions in component integration
    """
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
    """Ensures exceptions are caught and reported to stderr
    
    Without this, stack traces would be shown to the end user (bad UX).
    Exit code 1 allows scripts/CI to detect real technical errors.
    stderr vs stdout allows scripts to capture only valid output from stdout
    """
    mock_serial_ports.side_effect = OSError("Unable to list ports")

    exit_code = main()

    # Exit 1 signals real error to shell scripts/CI
    assert exit_code == 1
    captured = capsys.readouterr()
    # Error goes to stderr to not contaminate stdout that scripts might parse
    assert "Error:" in captured.err
