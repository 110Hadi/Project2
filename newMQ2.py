from machine import Pin, ADC
import ujson
import urequests
import gc
import time

API_URL = 'http://192.168.1.140:8000/api/readings'
DEVICE_ID = 'pico-mq2-1'
DEVICE_TOKEN = '8nmWa9S8z62d3Ts3RdDB68MNfjCIxWt8mTcBFCatjtw'

MQ2_PIN = 26
SAMPLE_PERIOD_MQ2 = 1000

mq2 = ADC(Pin(MQ2_PIN))
led = Pin("LED", Pin.OUT)
led.off()


def send_reading(value):
    response = None
    try:
        gc.collect()
        response = urequests.post(
            API_URL,
            data=ujson.dumps({"value": int(value), "device_id": DEVICE_ID}),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + DEVICE_TOKEN,
            },
        )
        if response.status_code != 201:
            print("Upload rejected by API; HTTP status:", response.status_code)
            try:
                print("API response:", response.text)
            except Exception:
                pass
            return False
        return True
    except Exception as exc:
        print("Upload failed:", exc)
        return False
    finally:
        if response is not None:
            response.close()
        gc.collect()


while True:
    value = mq2.read_u16()
    print("MQ2 raw:", value)

    # One short pulse per sample confirms the recording loop is alive.
    led.on()
    time.sleep_ms(100)
    led.off()

    if send_reading(value):
        print("Uploaded to database API")

    time.sleep_ms(SAMPLE_PERIOD_MQ2)
