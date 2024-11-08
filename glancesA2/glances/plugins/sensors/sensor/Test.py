import subprocess
import time

def check_nvme_temperature():
    try:
        # Run smartctl to get NVMe stats
        output = subprocess.check_output(
            [r"C:\Program Files\Smartmontools\bin\smartctl.exe", '-a', '/dev/sdc', '-d', 'nvme'],
            universal_newlines=True
        )

        # Parse output to find the temperature line
        for line in output.splitlines():
            if 'Temperature:' in line:
                temperature = int(line.split()[-2])  # Gets the temperature value
                print(f"NVMe Temperature: {temperature}°C")
                return temperature

    except subprocess.CalledProcessError as e:
        print(f"Error executing smartctl: {e}")

if __name__ == "__main__":
    while True:
        check_nvme_temperature()
        time.sleep(5)  # Check every 5 seconds
