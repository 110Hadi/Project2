from machine import Pin, ADC
import time

# MQ-2 analog output -> Pico GP26
mq2 = ADC(Pin(26))

# HX711: DT/DOUT -> Pico GP16, SCK/CLK -> Pico GP17
DT = Pin(16, Pin.IN, Pin.PULL_UP)
SCK = Pin(17, Pin.OUT)
SCK.value(0)

# Calibrated load-cell values
CALIBRATION_FACTOR = 201.75
POLARITY = -1
TARE_SAMPLES = 20


def read_load_cell_raw():
    # HX711 pulls DT low when a reading is ready.
    started = time.ticks_ms()
    while DT.value() == 1:
        if time.ticks_diff(time.ticks_ms(), started) > 3000:
            raise OSError("HX711 timeout: check DT, SCK, power, and GND")
        time.sleep_ms(1)

    value = 0
    for _ in range(24):
        SCK.value(1)
        value = (value << 1) | DT.value()
        SCK.value(0)

    # Extra pulse selects channel A, gain 128.
    SCK.value(1)
    SCK.value(0)

    # Convert signed 24-bit data to a normal integer.
    if value & 0x800000:
        value -= 0x1000000
    return value


def tare_load_cell():
    total = 0
    for _ in range(TARE_SAMPLES):
        total += read_load_cell_raw()
    return total / TARE_SAMPLES


print("Keep load cell empty; setting zero...")
time.sleep(2)
zero_value = tare_load_cell()
print("MQ-2 and load-cell readings start now:")

while True:
    mq2_value = mq2.read_u16()

    raw_value = read_load_cell_raw()
    grams = max(0, (raw_value - zero_value) * POLARITY / CALIBRATION_FACTOR)
    kilograms = grams / 1000

    print("MQ-2:", mq2_value, "| Weight:", round(grams, 1), "g /", round(kilograms, 3), "kg")
    time.sleep(2)
