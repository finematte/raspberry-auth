import subprocess
import os
import argparse
from dotenv import load_dotenv

load_dotenv()


SERVICES = ["hostapd", "dnsmasq", "dhcpcd"]

WIFI_INTERFACE = os.getenv("WIFI_INTERFACE")

INTERFACE_ADDRESS = os.getenv("INTERFACE_ADDRESS")

CONFIG_FILES = [
    ("config/hotspot/dhcpcd.conf", "/etc/dhcpcd.conf"),
    ("config/hotspot/dnsmasq.conf", "/etc/dnsmasq.conf"),
    ("config/hotspot/hostapd.conf", "/etc/hostapd/hostapd.conf"),
]


def run_systemctl(action, service):
    subprocess.run(["sudo", "systemctl", action, service], check=True)


def is_service_active(service_name):
    result = subprocess.run(
        ["systemctl", "is-active", service_name], capture_output=True, text=True
    )

    return result.stdout.strip() == "active"


def kill_process_on_port(port):
    command = f"sudo lsof -t -i tcp:{port}"
    try:
        process_id = subprocess.check_output(command, shell=True)
        if process_id:
            process_id = process_id.decode().strip()
            print(f"Killing process {process_id} on port {port}")
            subprocess.run(["sudo", "kill", "-9", process_id], check=True)
        else:
            print(f"No process is running on port {port}")
    except:
        print("Port is free, no need to kill..")


def create_hotspot():
    print("Stopping services..")

    for service in SERVICES:
        run_systemctl("stop", service)

    print("Configuring hotspot files.")

    for src, dest in CONFIG_FILES:
        subprocess.run(["sudo", "cp", src, dest], check=True)

    print("Pointing system to new hostapd file..")

    with open("/etc/default/hostapd", "w") as file:
        file.write('DAEMON_CONF="/etc/hostapd/hostapd.conf"')

    print("Starting all needed services..")

    for service in SERVICES:
        run_systemctl("unmask", service)
        run_systemctl("start", service)

    print("Checking if services started correctly..")

    for service in SERVICES:
        if not is_service_active(service):
            print(f"{service} service did not start correctly")

    print("Configuring iptables to redirect user to the website..")

    try:
        subprocess.run(["sudo", "iptables", "-F"], check=True)

        subprocess.run(
            [
                "sudo",
                "iptables",
                "-A",
                "FORWARD",
                "-d",
                f"{INTERFACE_ADDRESS}",
                "-j",
                "ACCEPT",
            ],
            check=True,
        )

        subprocess.run(["sudo", "iptables", "-A", "FORWARD", "-j", "DROP"], check=True)

        subprocess.run(
            [
                "sudo",
                "iptables",
                "-t",
                "nat",
                "-A",
                "PREROUTING",
                "-i",
                f"{WIFI_INTERFACE}",
                "-p",
                "tcp",
                "--dport",
                "80",
                "-j",
                "DNAT",
                "--to-destination",
                f"{INTERFACE_ADDRESS}:8000",
            ],
            check=True,
        )

        """subprocess.run(
            [
                "sudo",
                "iptables",
                "-t",
                "nat",
                "-A",
                "PREROUTING",
                "-i",
                f"{WIFI_INTERFACE}",
                "-p",
                "tcp",
                "--dport",
                "443",
                "-j",
                "DNAT",
                "--to-destination",
                f"{INTERFACE_ADDRESS}:8000",
            ],
            check=True,
        )"""

        subprocess.run(["sudo", "sysctl", "-w", "net.ipv4.ip_forward=1"], check=True)
    except:
        return "Error!"

    print("Finishing..")

    try:
        print("Checking if port 80 is free..")
        kill_process_on_port(80)
        kill_process_on_port(8000)
        print("Starting captive portal..")
        subprocess.Popen(["sudo", "python3", "captive_portal.py"])

        print("Starting Django server..")
        subprocess.Popen(["sudo", "python3", "manage.py", "runserver", "0.0.0.0:8000"])
    except:
        return "Error!"

    print("--- Hotspot Started Successfully --- ")


def stop_hotspot():
    print("Stopping services..")

    for service in SERVICES:
        run_systemctl("stop", service)

    print("Restoring original files..")

    for src, dest in CONFIG_FILES:
        subprocess.run(["sudo", "cp", src, dest], check=True)

    run_systemctl("start", "dhcpcd")

    print("Unblocking all outgoing traffic..")

    subprocess.run(["sudo", "iptables", "-A", "FORWARD", "-j", "DROP"], check=True)

    print("Allowing access to local website..")

    subprocess.run(
        [
            "sudo",
            "iptables",
            "-A",
            "FORWARD",
            "-d",
            f"{INTERFACE_ADDRESS}",
            "-j",
            "ACCEPT",
        ],
        check=True,
    )

    print("Killing Django server..")
    kill_process_on_port(8000)
    print("Killing Captive Portal..")
    kill_process_on_port(80)

    os.system(f"wpa_cli -i {WIFI_INTERFACE} reconfigure")

    print("Hotspot stopped and original files restored")


def reset_wifi_connection():
    subprocess.run(
        [
            "sudo",
            "cp",
            "config/regular/wpa_supplicant.conf",
            "/etc/wpa_supplicant/wpa_supplicant.conf",
        ],
        check=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Control the hotspot.")

    parser.add_argument(
        "command",
        choices=["start", "stop", "reset"],
        help='Use "start" to create a hotspot or "stop" to stop the hotspot and restore the files or "reset" to reset WiFi connection to default..',
    )

    args = parser.parse_args()

    if args.command == "start":
        create_hotspot()

    elif args.command == "stop":
        stop_hotspot()

    elif args.command == "reset":
        reset_wifi_connection()
