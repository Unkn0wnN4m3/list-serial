# ListSerial

A simple Python CLI utility to list available serial ports on your system with their names and descriptions.

## Requirements

- Python >= 3.9
- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager

## Installation

```bash
git clone <repository-url>
cd list-serial
uv tool install .
```

## Usage

Simply run:

```bash
listserial
```

**Example output:**

```text
Available serial ports:

* COM3 - USB Serial Device
* COM4 - Arduino Uno
```

If no ports are detected:

```text
No serial port is being used
```

## Development

Install with development dependencies:

```bash
uv sync --dev
```

Run tests:

```bash
uv run pytest
```

## Compatibility

- Windows
- Linux
- macOS

## Credits

Inspired by:  
<https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python>
