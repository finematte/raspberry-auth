from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import wifi
import string
import os
import subprocess
import time
from dotenv import load_dotenv


WIFI_INTERFACE = "wlan0"


def check_wifi_connection(ssid):
    try:
        result = subprocess.check_output(["sudo", "iwgetid"]).decode()
    except:
        return "Error!"
    result = result.split('"')[1]

    return result == ssid


def check_wifi_connection_ping():
    result = subprocess.run(
        ["ping", "-c", "1", "-W", "1", "8.8.8.8"], capture_output=True
    )

    return result.returncode == 0


def connect_to_wifi(ssid, password):
    subprocess.run(
        ["sudo", "cp", "config/regular/wpa_supplicant.conf", "/etc/wpa_supplicant/"]
    )

    config_lines = [
        "network={\n",
        '  ssid="{}"\n'.format(ssid),
        '  psk="{}"\n'.format(password),
        "}\n",
    ]

    with open("/etc/wpa_supplicant/wpa_supplicant.conf", "a") as wifi_config_file:
        wifi_config_file.writelines(config_lines)

    return os.system(f"wpa_cli -i {WIFI_INTERFACE} reconfigure")


def wifi_view(request):
    wifilist = []

    try:
        cells = wifi.Cell.all(f"{WIFI_INTERFACE}")

        for cell in cells:
            ssid = "".join(filter(lambda x: x in string.printable, cell.ssid))

            if ssid and ssid not in [info["ssid"] for info in wifilist]:
                wifi_info = {"ssid": ssid}

                wifilist.append(wifi_info)

        context = {"wifilist": wifilist}

        return render(request, "wifi.html", context)

    except Exception as e:
        if not wifilist:
            return f"Error! {e}"

        else:
            context = {"wifilist": wifilist}

            return render(request, "wifi.html", context)


@csrf_exempt
def connect_to_network(request):
    if request.method == "POST":
        ssid = request.POST.get("ssid")

        return render(request, "connect.html", {"ssid": ssid})

    else:
        return redirect("wifi_view")


@csrf_exempt
def try_connect(request):
    if request.method == "POST":
        ssid = request.POST.get("ssid")

        password = request.POST.get("password")

        connect_to_wifi(ssid, password)

        time.sleep(5)

        if check_wifi_connection(ssid) or check_wifi_connection_ping():
            return redirect("success_view", ssid=ssid)

        else:
            return render(
                request, "connect.html", {"ssid": ssid, "password_error": True}
            )

    else:
        return redirect("wifi_view")


def success_view(request, ssid):
    return render(request, "success.html", {"ssid": ssid})


def shutdown_hotspot(request):
    time.sleep(5)

    subprocess.run(["sudo", "python3", "hotspot.py", "stop"])

    return JsonResponse({"status": "success"})
