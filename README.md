# PC Health Evaluation Tool

A comprehensive Windows system auditing tool that gathers hardware metrics, checks driver health, and generates a professional PDF Hardware Evaluation Certificate.

## Features

- **Hardware Discovery**: Detects manufacturer, model, CPU, RAM, and serial numbers
- **CPU Health Analysis**: Monitors CPU load and detects thermal throttling
- **Battery Health**: Calculates current battery capacity as a percentage of original design capacity (laptop only)
- **Storage Analysis**: Scans all logical drives and reports free/total space in GB
- **Driver Health Checks**:
  - Keyboard & Touchpad (Input Devices)
  - Bluetooth
  - Audio
  - Wi-Fi
  - Display Driver
- **Manufacturing Date Decoding**: Extracts manufacturing date from HP serial numbers
- **PDF Report Generation**: Creates a professional Hardware Evaluation Certificate with purchase recommendations

## Requirements

- **Operating System**: Windows 10/11
- **Python**: 3.7 or higher
- **Administrator Access**: Required for comprehensive hardware queries

## Dependencies

Install required Python packages:

```bash
pip install psutil fpdf2
```

## Usage

### Running the Script

```bash
python pcHealth.py
```

The tool will gather system metrics and generate a PDF report named `System_Audit_[HHmmss].pdf` in the current directory.

### Output

The generated PDF includes:
- System identification (Manufacturer, Model, Serial Number)
- CPU information and health status
- Battery capacity percentage
- RAM amount
- Storage drives and free space
- Input device status
- Wireless connectivity status (Bluetooth, Wi-Fi)
- Audio and display driver status
- Critical purchase evaluation guide with recommendations

## Building Executable

To compile the script into a standalone Windows executable using PyInstaller:

```bash
pyinstaller pcHealth.spec
```

The compiled executable will be located in the `dist/` directory.

## Report Interpretation

### CPU Health
- **Good**: Indicates idle capacity available and no thermal issues
- **Poor (Thermal Throttling)**: CPU is being throttled; cooling system may need cleaning

### Battery Health
- **75%+**: Battery in good condition, laptop is mobile
- **Below 75%**: Battery degraded; laptop should stay plugged in

### Driver Status
- **Operational**: Driver is active and functional
- **Driver Error/Not Found**: Device driver installation or updates needed

### Storage Recommendation
- Ensure at least one SSD for system speed
- Monitor free space to maintain system performance

### RAM Recommendation
- 16GB: Adequate for modern multitasking (target for 2026)
- 8GB: May struggle with contemporary workloads

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Permission Denied" errors | Run script as Administrator |
| Battery health shows "Desktop" | Script running on desktop computer (expected) |
| Driver status shows errors | Update device drivers via Device Manager or manufacturer website |
| PDF fails to generate | Ensure `fpdf2` package is installed |

## Technical Details

The tool uses:
- **psutil**: For memory and CPU metrics
- **subprocess**: To execute PowerShell commands for Windows-specific hardware queries
- **fpdf2**: For PDF generation
- **json**: For parsing PowerShell JSON output

## Notes

- All hardware queries use Windows WMI (Win32) classes for accuracy
- Serial number decoding currently supports HP manufacturing date format
- Requires PowerShell 5.1+ (standard on Windows 10/11)

## License

Developed for PC evaluation and audit purposes.
