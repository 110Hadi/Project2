from machine import Pin
import time

# HX711 connections
DT = Pin(16, Pin.IN, Pin.PULL_UP)
SCK = Pin(17, Pin.OUT)
SCK.value(0)

# Calibrated load-cell values
CALIBRATION_FACTOR = 201.75
POLARITY = -1

# Averaging and smoothing settings
ZERO_SAMPLES = 20
READ_SAMPLES = 10
FILTER_ALPHA = 0.25
ZERO_DEADBAND_G = 3


def read_raw():
    while DT.value() == 1:
        time.sleep_ms(1)

    value = 0
    for _ in range(24):
        SCK.value(1)
        value = (value << 1) | DT.value()
        SCK.value(0)

    # 25th pulse selects channel A, gain 128.
    SCK.value(1)
    SCK.value(0)

    # Convert signed 24-bit value to a normal integer.
    if value & 0x800000:
        value -= 0x1000000
    return value


def read_average(samples):
    total = 0
    for _ in range(samples):
        total += read_raw()
    return total / samples


print("Keep scale empty...")
time.sleep(2)
zero_value = read_average(ZERO_SAMPLES)
print("Zero set:", zero_value)
filtered_grams = 0

while True:
    raw_value = read_average(READ_SAMPLES)
    difference = raw_value - zero_value
    corrected_difference = difference * POLARITY
    grams = corrected_difference / CALIBRATION_FACTOR

    filtered_grams += FILTER_ALPHA * (grams - filtered_grams)
    if abs(filtered_grams) < ZERO_DEADBAND_G:
        filtered_grams = 0

    kilograms = filtered_grams / 1000

    print("Raw average:", round(raw_value))
    print("Zero se farq:", round(corrected_difference))
    print("Raw weight:", round(grams, 1), "g")
    print("Smoothed weight:", round(filtered_grams, 1), "g")
    print("Weight:", round(kilograms, 3), "kg")
    print("-------------------")

    time.sleep(1)
