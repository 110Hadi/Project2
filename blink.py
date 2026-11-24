from machine import Pin
import time

# HX711 connections: DT/DOUT -> Pico GP16, SCK/CLK -> Pico GP17
DT = Pin(16, Pin.IN, Pin.PULL_UP)
SCK = Pin(17, Pin.OUT)
SCK.value(0)

# Calibrated values from the working load-cell setup.
CALIBRATION_FACTOR = 201.75
POLARITY = -1
ZERO_SAMPLES = 20


def read_raw():
    # HX711 pulls DT low when one reading is ready.
    started = time.ticks_ms()
    while DT.value():
        if time.ticks_diff(time.ticks_ms(), started) > 3000:
            raise OSError("HX711 timeout: check its power and DT/SCK wiring")
        time.sleep_ms(1)

    value = 0
    for _ in range(24):
        SCK.value(1)
        value = (value << 1) | DT.value()
        SCK.value(0)

    # 25th pulse selects channel A, gain 128.
    SCK.value(1)
    SCK.value(0)

    # Convert signed 24-bit data to a normal integer.
    if value & 0x800000:
        value -= 0x1000000
    return value


def tare():
    # Average only the empty-scale baseline. Live readings stay unsmoothed.
    total = 0
    for _ in range(ZERO_SAMPLES):
        total += read_raw()
    return total / ZERO_SAMPLES


print("Keep scale empty; setting zero...")
time.sleep(2)
zero_value = tare()
print("Ready. Showing live readings:")

while True:
    raw_value = read_raw()
    grams = max(0, (raw_value - zero_value) * POLARITY / CALIBRATION_FACTOR)
    kilograms = grams / 1000

    print("Raw:", round(raw_value), " | Weight:", round(grams, 1), "g /", round(kilograms, 3), "kg")
    time.sleep(1)
