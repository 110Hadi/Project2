from machine import Pin, ADC, Timer
import time
import ujson
import urequests
import gc

# API and device settings
API = "https://hasnain-gdg7hmhdh7fyc9b4.eastasia-01.azurewebsites.net/api"
TOKEN = "8nmWa9S8z62d3Ts3RdDB68MNfjCIxWt8mTcBFCatjtw"
DEVICE_ID = "pico-mq2-1"

# Sensor pins and load-cell calibration
mq2 = ADC(Pin(26))
DT = Pin(16, Pin.IN, Pin.PULL_UP)
SCK = Pin(17, Pin.OUT)
SCK.value(0)
CALIBRATION_FACTOR = 201.75
POLARITY = -1

MQ2_INTERVAL_MS = 5000
# Change to 60 * 60 * 1000 when you want one load-cell upload per hour.
LOAD_CELL_INTERVAL_MS = 60 * 1000

LED = Pin("LED", Pin.OUT)
mq2_pending = True
weight_pending = True


# Timer callbacks only set flags. Sensor/network work runs below, outside IRQs.
def mq2_timer_irq(timer):
    global mq2_pending
    mq2_pending = True


def weight_timer_irq(timer):
    global weight_pending
    weight_pending = True


def read_load_cell():
    started = time.ticks_ms()
    while DT.value():
        if time.ticks_diff(time.ticks_ms(), started) > 3000:
            raise OSError("HX711 timeout: check DT, SCK, power, and GND")
        time.sleep_ms(1)

    value = 0
    for _ in range(24):
        SCK.value(1)
        value = (value << 1) | DT.value()
        SCK.value(0)

    # 25th clock pulse selects channel A, gain 128.
    SCK.value(1)
    SCK.value(0)

    if value & 0x800000:
        value -= 0x1000000
    return value


def tare_load_cell():
    total = 0
    for _ in range(20):
        total += read_load_cell()
    return total / 20


def blink(times):
    for _ in range(times):
        LED.on()
        time.sleep_ms(120)
        LED.off()
        time.sleep_ms(120)


def send(url, data):
    response = None
    try:
        gc.collect()
        response = urequests.post(
            API + url,
            data=ujson.dumps(data),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + TOKEN,
            },
        )
        if response.status_code == 201:
            return True
        print("Upload failed. HTTP:", response.status_code)
        return False
    except Exception as error:
        print("Upload error:", error)
        return False
    finally:
        if response is not None:
            try:
                response.close()
            except Exception:
                pass
        gc.collect()


print("Keep the load cell empty; setting zero...")
time.sleep(2)
zero_value = tare_load_cell()

# RP2040 MicroPython uses virtual timers; IRQs just mark work as due.
mq2_timer = Timer(-1)
weight_timer = Timer(-1)
mq2_timer.init(period=MQ2_INTERVAL_MS, mode=Timer.PERIODIC, callback=mq2_timer_irq)
weight_timer.init(period=LOAD_CELL_INTERVAL_MS, mode=Timer.PERIODIC, callback=weight_timer_irq)

try:
    while True:
        if mq2_pending:
            mq2_pending = False
            mq2_value = mq2.read_u16()
            print("MQ-2:", mq2_value)
            if send("/readings", {"value": mq2_value, "device_id": DEVICE_ID}):
                blink(1)

        if weight_pending:
            weight_pending = False
            try:
                raw_value = read_load_cell()
                grams = max(0, (raw_value - zero_value) * POLARITY / CALIBRATION_FACTOR)
                weight_grams = round(grams, 1)
                print("Load cell:", weight_grams, "g")
                if send("/load-cell", {"weight_grams": weight_grams, "device_id": DEVICE_ID}):
                    blink(2)
            except Exception as error:
                print("Load-cell error:", error)

        time.sleep_ms(10)
finally:
    mq2_timer.deinit()
    weight_timer.deinit()
    SCK.value(0)
    LED.off()
