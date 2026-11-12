from machine import Pin, Timer, ADC
from time import ticks_ms, ticks_diff
from utime import sleep

# ------------------------- CONSTANTS --------------------------- #
SMOKE_THRESHOLD = 30000
MQ2_PIN = 26







# -------------------------------- SET-UP ------------------------- #
mq2 = ADC(Pin(MQ2_PIN))







# --------------------------------- FUNCTIONS ----------------------- #







# --------------------------------- MAIN LOOP ---------------------------- #

print("Warming up MQ-2 smoke sensor (please wait 10 seconds)...")
sleep(10)
print("Sensor ready!")

while True:
    # Read the raw analog value (16-bit integer: 0 to 65535)
    raw_value = mq2.read_u16()
    print(f"Raw ADC Value: {raw_value}")

    # if raw_value > SMOKE_THRESHOLD:
    #     print("WARNING: Smoke or Gas detected!")
    # else:
    #     print("Air quality normal.")
    
    sleep(0.4)