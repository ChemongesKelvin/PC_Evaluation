import psutil
import subprocess
import os
from datetime import datetime
from fpdf import FPDF
import json

# -------------------------------
# 1. Hardware & Age Logic
# -------------------------------
def run_ps(cmd):
    """Modern PowerShell interface for Windows 10/11."""
    try:
        completed = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True, check=True)
        return completed.stdout.strip()
    except:
        return ""

def decode_hp_age(sn):
    """Decodes HP Serial Number for manufacturing date (4th, 5th, 6th digits)."""
    if len(sn) >= 6:
        try:
            year_digit = int(sn[3])
            week_digits = sn[4:6]
            base_year = 2020 if year_digit <= 6 else 2010
            actual_year = base_year + year_digit
            return f"{actual_year} (Week {week_digits})"
        except:
            return "Unknown Format"
    return "N/A"

def get_input_status():
    """Checks for active Keyboard and Touchpad/Pointing devices."""
    kb = run_ps("Get-CimInstance Win32_Keyboard | Select-Object -ExpandProperty Status")
    tp = run_ps("Get-CimInstance Win32_PointingDevice | Select-Object -ExpandProperty Status")
    
    kb_health = "Operational" if "OK" in kb or kb == "" else "Driver Error/Not Found"
    tp_health = "Operational" if "OK" in tp or tp == "" else "Driver Error/Not Found"
    
    return kb_health, tp_health

def get_cpu_health_status():
    """Calculates CPU health based on Load and Thermal Throttling flags."""
    load = psutil.cpu_percent(interval=1)
    current_clk = run_ps("(Get-CimInstance Win32_Processor).CurrentClockSpeed")
    max_clk = run_ps("(Get-CimInstance Win32_Processor).MaxClockSpeed")
    
    try:
        if int(current_clk) < (int(max_clk) * 0.5) and load > 80:
            return f"Poor (Thermal Throttling Detected - {load}% Load)"
        return f"Good ({100-load}% Idle Capacity)"
    except:
        return "Operational"

def get_all_storage():
    """Iterates through all logical drives."""
    storage_list = []
    raw_data = run_ps("Get-Volume | Select-Object DriveLetter, FriendlyName, Size, SizeRemaining | ConvertTo-Json")
    try:
        volumes = json.loads(raw_data)
        if isinstance(volumes, dict): volumes = [volumes]
        for vol in volumes:
            letter = vol.get("DriveLetter")
            if letter:
                total = round(vol.get("Size", 0) / (1024**3), 1)
                free = round(vol.get("SizeRemaining", 0) / (1024**3), 1)
                storage_list.append(f"{letter}: {free}GB free / {total}GB")
    except:
        storage_list.append("C: Detected (Details restricted)")
    return storage_list

# -------------------------------
# 2. Driver Health Checks
# -------------------------------
def get_driver_status(device_filter):
    """Generic driver status checker using Win32_PnPEntity."""
    cmd = f"Get-CimInstance Win32_PnPEntity | Where-Object {{$_.Name -like '*{device_filter}*'}} | Select-Object -ExpandProperty Status"
    result = run_ps(cmd)
    if "OK" in result or result == "":
        return "Operational"
    return "Driver Error/Not Found"

def get_bluetooth_status():
    return get_driver_status("Bluetooth")

def get_audio_status():
    return get_driver_status("Audio")

def get_wifi_status():
    return get_driver_status("Wi-Fi")

def get_display_status():
    return get_driver_status("Display")

# -------------------------------
# 3. Main Logic & PDF Report
# -------------------------------
def generate_audit():
    print("Gathering Deep System Metrics...")
    
    # System Branding
    mfr = run_ps("(Get-CimInstance Win32_ComputerSystem).Manufacturer")
    model = run_ps("(Get-CimInstance Win32_ComputerSystem).Model")
    sn = run_ps("(Get-CimInstance Win32_Bios).SerialNumber")
    
    # CPU & Inputs
    cpu_name = run_ps("(Get-CimInstance Win32_Processor).Name")
    cpu_age = decode_hp_age(sn) if "HP" in mfr.upper() else "N/A"
    cpu_health = get_cpu_health_status()
    kb_status, tp_status = get_input_status()
    
    # Battery Health
    full = run_ps("(Get-CimInstance -Namespace root/wmi -ClassName BatteryFullChargedCapacity).FullChargedCapacity")
    design = run_ps("(Get-CimInstance -Namespace root/wmi -ClassName BatteryStaticData).DefaultCapacity")
    try:
        bat_health = f"{round((int(full)/int(design))*100, 1)}% of Original Capacity"
    except:
        bat_health = "Desktop (No Battery)"

    # Driver Health Checks
    bt_status = get_bluetooth_status()
    audio_status = get_audio_status()
    wifi_status = get_wifi_status()
    display_status = get_display_status()

    # Report Data Mapping
    data = {
        "Manufacturer": mfr,
        "Model": model,
        "Serial Number": sn,
        "CPU Model": cpu_name,
        "CPU Mfg Date": cpu_age,
        "CPU Health": cpu_health,
        "Battery Health": bat_health,
        "RAM Total": f"{round(psutil.virtual_memory().total / (1024**3), 1)} GB",
        "Keyboard Status": kb_status,
        "Touchpad Status": tp_status,
        "Bluetooth Status": bt_status,
        "Audio Status": audio_status,
        "Wi-Fi Status": wifi_status,
        "Display Driver Status": display_status,
        "Drives": " | ".join(get_all_storage())
    }

    # PDF Creation
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(30, 60, 120)
    pdf.cell(0, 15, "HARDWARE EVALUATION CERTIFICATE", ln=True, align='C')
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 10)
    pdf.set_fill_color(240, 240, 240)
    
    for key, val in data.items():
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(50, 10, f" {key}", 1, 0, 'L', True)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 10, f" {val}", 1, 1, 'L')

    # Buying Guide & Conclusion
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Critical Purchase Evaluation:", ln=True)
    pdf.set_font("Arial", '', 10)
    
    guide = [
        "- CPU: If CPU Health shows 'Throttling', the cooling system likely needs cleaning.",
        "- Inputs: Keyboard/Touchpad 'Operational' status confirms drivers are active.",
        "- Battery: Health less than 75% means the laptop is tethered to the wall; expect low mobility.",
        "- Storage: Always ensure at least one drive is an SSD for system speed.",
        "- RAM: 16GB is the target for 2026; 8GB will struggle with modern multitasking.",
        "- Bluetooth: Errors may prevent pairing with peripherals.",
        "- Audio: Driver issues can cause sound distortion or no output.",
        "- Wi-Fi: Faulty drivers may lead to unstable connectivity.",
        "- Display: Errors may cause resolution or graphics problems."
    ]
    for item in guide:
        pdf.cell(0, 7, item, ln=True)

    filename = f"System_Audit_{datetime.now().strftime('%H%M%S')}.pdf"
    pdf.output(filename)
    print(f"Success! Report generated as: {filename}")

if __name__ == "__main__":
    generate_audit()

