# ListSerial

ListSerial is a Python utility for listing available serial ports on the
system, showing their name and description (when available).

## Installation

1. Clone this repository or download the files.
2. Change to the cloned repository.
3. Install the program and required dependencies by running:

> [!IMPORTANT]
> [uv](https://docs.astral.sh/uv/getting-started/installation/) is required

```bash
uv tool install -U .
```

## Usage

You can run the main script to display available serial ports:

```bash
listserial
```

The output will show a list of detected serial ports, for example:

```text
Available serial ports:

* COM3 - USB Serial Device
* COM4 - Arduino Uno
```

If no ports are available, you will see:

```text
No serial port is being used
```

## Compatibility

- Windows
- Linux
- MacOS

## Credits

Inspired by:  
<https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python>
