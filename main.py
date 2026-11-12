
import network
import time

SSID = "TECNO SPARK"
PASSWORD = "777777di"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

print("WiFi active:", wlan.active())
print("Connecting to:", SSID)

wlan.connect(SSID, PASSWORD)

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