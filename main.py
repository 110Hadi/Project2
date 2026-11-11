
import network
import time

SSID = "YOUR_WIFI_NAME"
PASSWORD = "YOUR_WIFI_PASSWORD"

# Initialize Wi-Fi in station mode
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Connect to Wi-Fi
wlan.connect(SSID, PASSWORD)

print("Connecting to Wi-Fi...")

while not wlan.isconnected():
    time.sleep(1)
    print("Waiting...")

print("Connected!")
print("Network configuration:", wlan.ifconfig())
