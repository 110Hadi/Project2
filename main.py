
import network
import time
from machine import Pin, PWM, ADC, Timer

LED = Pin("LED", Pin.OUT) 

time.sleep(2)
WIFI_SSID = 'Error'
WIFI_PASSWORD = 'rimjhim125'

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
        LED.toggle()
        time.sleep(0.1)
        LED.toggle()
        time.sleep(0.1)
        LED.toggle()
        time.sleep(0.1)
        LED.toggle()
        time.sleep(0.1)
        break

    time.sleep(1)
else:
    print("Connection failed!")
    print("Final status:", wlan.status())

if wlan.isconnected():
    # newMQ2.py starts the sensor sampling/upload loop.
    import newMQ2
