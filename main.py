
import network
import time

# TODO: Replace these sample values with your Wi-Fi credentials.
WIFI_SSID = "TECNO SPARK"
WIFI_PASSWORD = "777777di"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

print("WiFi active:", wlan.active())
print("Connecting to:", WIFI_SSID)

wlan.connect(WIFI_SSID, WIFI_PASSWORD)

for i in range(40):
    status = wlan.status()

    print("Attempt:", i + 1)
    print("Status:", status)
    print("Connected:", wlan.isconnected())

    if wlan.isconnected():
        print("SUCCESS!")
        print("IP Config:", wlan.ifconfig())
        break

    time.sleep(1)
else:
    print("Connection failed!")
    print("Final status:", wlan.status())

if wlan.isconnected():
    # MQ2.py starts the sensor sampling/upload loop.
    import MQ2
