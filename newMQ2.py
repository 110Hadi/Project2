from machine import Pin, ADC
import ujson
import urequests
import gc
import time

API_BASE_URL = "https://hasnain-gdg7hmhdh7fyc9b4.eastasia-01.azurewebsites.net/api"
MQ2_API_URL = API_BASE_URL + "/readings"
LOAD_CELL_API_URL = API_BASE_URL + "/load-cell"
DEVICE_ID = "pico-mq2-1"
DEVICE_TOKEN = "8nmWa9S8z62d3Ts3RdDB68MNfjCIxWt8mTcBFCatjtw"

# HX711: DOUT/DT -> Pico GP16, SCK/CLK -> Pico GP17.
HX711_DT_PIN = 16
HX711_SCK_PIN = 17
HX711_CALIBRATION_FACTOR = 201.75  # Calibrated raw counts per gram.
HX711_POLARITY = -1
HX711_ZERO_SAMPLES = 20

MQ2_INTERVAL_MS = 5000
# Load-cell interval: change 60 * 1000 to 60 * 60 * 1000 for hourly readings.
LOAD_CELL_INTERVAL_MS = 60 * 1000

LED = Pin("LED", Pin.OUT)
mq2 = ADC(Pin(26))


class HX711:
    def __init__(self, data_pin, clock_pin):
        self.data = Pin(data_pin, Pin.IN, Pin.PULL_UP)
        self.clock = Pin(clock_pin, Pin.OUT)
        self.clock.value(0)

    def read_raw(self):
        started = time.ticks_ms()
        while self.data.value():
            if time.ticks_diff(time.ticks_ms(), started) > 1000:
                raise OSError("HX711 timeout; check DT/SCK wiring and power")
            time.sleep_ms(1)

        value = 0
        for _ in range(24):
            self.clock.value(1)
            value = (value << 1) | self.data.value()
            self.clock.value(0)
        # 25th pulse selects channel A, gain 128 for the next conversion.
        self.clock.value(1)
        self.clock.value(0)
        if value & 0x800000:
            value -= 0x1000000
        return value

    def read_average(self, samples=5):
        total = 0
        for _ in range(samples):
            total += self.read_raw()
        return total / samples


load_cell = HX711(HX711_DT_PIN, HX711_SCK_PIN)


def blink_led(times):
    for _ in range(times):
        LED.on()
        time.sleep_ms(150)
        LED.off()
        time.sleep_ms(150)


def post_json(url, payload):
    response = None
    try:
        gc.collect()
        response = urequests.post(
            url,
            data=ujson.dumps(payload),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + DEVICE_TOKEN,
            },
        )
        return response.status_code
    finally:
        if response is not None:
            try:
                response.close()
            except Exception:
                pass
        gc.collect()


def send_reading(value):
    try:
        status = post_json(MQ2_API_URL, {"value": int(value), "device_id": DEVICE_ID})
        if status != 201:
            print("MQ-2 upload rejected. HTTP status:", status)
            return False
        print("MQ-2 reading uploaded:", value)
        return True
    except Exception as exc:
        print("MQ-2 upload failed:", exc)
        return False


def send_weight(weight_grams):
    try:
        status = post_json(LOAD_CELL_API_URL, {
            "weight_grams": weight_grams,
            "device_id": DEVICE_ID,
        })
        if status != 201:
            print("Load-cell upload rejected. HTTP status:", status)
            return False
        print("Load-cell weight uploaded:", weight_grams, "g")
        return True
    except Exception as exc:
        print("Load-cell upload failed:", exc)
        return False


try:
    print("Taring load cell; keep the platform empty...")
    time.sleep(2)
    load_cell_offset = load_cell.read_average(HX711_ZERO_SAMPLES)
    print("Load-cell zero offset:", load_cell_offset)
    last_load_cell_send = time.ticks_ms() - LOAD_CELL_INTERVAL_MS

    while True:
        value = mq2.read_u16()
        print("MQ2 raw:", value)
        if send_reading(value):
            blink_led(1)

        if time.ticks_diff(time.ticks_ms(), last_load_cell_send) >= LOAD_CELL_INTERVAL_MS:
            try:
                # Save one live reading; no per-reading averaging or smoothing.
                raw_value = load_cell.read_raw()
                raw_difference = (raw_value - load_cell_offset) * HX711_POLARITY
                weight_grams = round(max(0, raw_difference / HX711_CALIBRATION_FACTOR), 1)
                print("Load-cell weight:", weight_grams, "g")
                if send_weight(weight_grams):
                    blink_led(2)
            except Exception as exc:
                print("Load-cell read failed:", exc)
            last_load_cell_send = time.ticks_ms()

        time.sleep_ms(MQ2_INTERVAL_MS)

finally:
    load_cell.clock.value(0)
    LED.off()
