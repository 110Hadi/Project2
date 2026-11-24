
import network
import time
from machine import Pin

LED = Pin("LED", Pin.OUT)
LED.off()

time.sleep(2)
WIFI_SSID = 'Error'
WIFI_PASSWORD = 'rimjhim125'

wlan = network.WLAN(network.STA_IF)


def all_lights_off():
    LED.off()


def disconnect_wifi():
    all_lights_off()
    try:
        wlan.disconnect()
    except Exception:
        pass
    try:
        wlan.active(False)
    except Exception:
        pass


def connect_wifi():
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    print("Connecting to Wi-Fi...")
    for _ in range(400):
        if wlan.isconnected():
            print("Wi-Fi connected:", wlan.ifconfig())
            for _ in range(4):
                LED.on()
                time.sleep_ms(100)
                LED.off()
                time.sleep_ms(100)
            return True
        time.sleep_ms(100)
    print("Wi-Fi connection timed out.")
    return False

try:
    while True:
        if connect_wifi():
            import newMQ2
        else:
            disconnect_wifi()
            time.sleep_ms(1000)

finally:
    # Ctrl+C / IDE Stop par lights off aur Wi-Fi disconnect.
    disconnect_wifi()
