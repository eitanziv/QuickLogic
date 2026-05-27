# QuickLogic
```
   ____       _      _      __             _      
  /___ \_   _(_) ___| | __ / /  ___   __ _(_) ___ 
 //  / / | | | |/ __| |/ // /  / _ \ / _` | |/ __|
/ \_/ /| |_| | | (__|   </ /__| (_) | (_| | | (__ 
\___,_\ \__,_|_|\___|_|\_\____/\___/ \__, |_|\___|
                                     |___/        
```
**The automated logic capture tool for hardware enumeration**

QuickLogic is a command line tool designed for hardware security researchers and penetration testers. It automates the process of capturing logic analyzer data from embedded devices, analyzing the captured signals, and identifying common communication protocols such as UART. Captured data can be saved in the standard `.sr` format for further review in tools like PulseView.

---

## Features

- Automatic device discovery via Sigrok
- Configurable sample rate, capture size, and timeout
- Saves captures in `.sr` format compatible with PulseView
- Active channel detection — ignores idle/flat lines automatically
- UART detection across common baud rates
- Full UART decode to file with header information
- Analyze existing `.sr` captures without needing hardware connected
- Color coded terminal output for quick readability
- Analysis summary at the end of each run

---

## Requirements

- Python 3
- [Sigrok](https://sigrok.org/) with Python bindings
- Compatible logic analyzer (default driver: `fx2lafw` for generic USB analyzers and Saleae clones)

### Python Dependencies
```
colorama
sigrok
```

Install with:
```bash
pip install colorama
```

---

## Usage

### Basic Capture
```bash
python3 QuickLogic.py --file capture_name --ch 0,1,2
```

### Capture with Custom Settings
```bash
python3 QuickLogic.py --file capture_name --ch 0,1 --speed 8000000 --size 50000000 --timeout 30
```

### Analyze an Existing Capture
```bash
python3 QuickLogic.py --file existing_capture.sr --analyze
```

### Analyze Without Specifying Channels
When using `--analyze` without `--ch`, all 8 channels are checked automatically:
```bash
python3 QuickLogic.py --file existing_capture.sr --analyze
```

---

## Arguments

| Argument | Required | Default | Description |
|---|---|---|---|
| `--file` | Yes | — | Name of the capture file (`.sr` extension added automatically) |
| `--ch` | No | All (0-7) | Comma separated list of channels to analyze (e.g. `0,4,7`) |
| `-cs` / `--speed` | No | 4000000 | Sample rate in Hz |
| `-s` / `--size` | No | 100000000 | Number of samples to capture |
| `--timeout` | No | 15 | Timeout in seconds before stopping capture |
| `--analyze` | No | False | Skip capture and analyze an existing `.sr` file |

---

## Output

### Terminal
QuickLogic provides color coded output throughout the run:
- **Green** — Successful operations and positive detections
- **Cyan** — Status and progress updates
- **Yellow** — Warnings
- **Red** — Errors

### Analysis Summary
At the end of each run a summary is printed showing findings per channel:
```
========= Analysis Summary =========
Channel 0: Most likely UART @ 115200 baud rate
Channel 1: No Traffic
Channel 2: No Traffic
...
====================================
```

### UART Decode File
When UART is detected and the operator confirms a full decode, the output is saved as:
```
<capture_name>_UART_Decode.txt
```

The file includes a header with channel and baud rate information followed by the full decoded ASCII output:
```
Channel: 0
Baudrate: 115200
=========================================
[71]HELLO! BOOT0 is starting!
...
```

---

## Supported Protocols

| Protocol | Status |
|---|---|
| UART | v1.0 |
| Clock Detection | Planned v1.1 |
| SPI | Planned |
| I2C | Planned |

---

## Notes

- The default driver is `fx2lafw` which supports generic USB logic analyzers and Saleae clones. Support for additional drivers is planned for future versions.
- Captured `.sr` files are compatible with [PulseView](https://sigrok.org/wiki/PulseView) for manual review and further analysis.
- UART detection uses a printable ASCII ratio check across common baud rates. A match requires 90% or higher printable characters in the sample decode.
- Non-printable bytes in UART output are written as hex (e.g. `\x0b`) so no data is lost.

---

## Version History

| Version | Notes |
|---|---|
| v1.0 | Initial release — UART detection and full decode |

---

## Disclaimer

This tool is intended for use on hardware you own or have explicit permission to test. Always ensure you have proper authorization before connecting to or capturing data from any device.
