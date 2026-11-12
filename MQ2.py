from machine import Pin, Timer, ADC
from time import ticks_ms, ticks_diff
from utime import sleep

# ------------------------- CONSTANTS --------------------------- #
LPG_THRESHOLD = 11000
MQ2_PIN = 26
SAMPLE_PERIOD = 1000







# -------------------------------- SET-UP ------------------------- #
mq2 = ADC(Pin(MQ2_PIN))
fresh = False
latest = mq2.read_u16()






# --------------------------------- FUNCTIONS ----------------------- #

def mq2Reading(n):
    global latest, fresh
    latest = mq2.read_u16()
    fresh = True

def is_leakage(value):
    if value > LPG_THRESHOLD:
        print('!!! LEAKAGE !!!')
    
    







# --------------------------------- MAIN LOOP ---------------------------- #

reader = Timer(period=SAMPLE_PERIOD, mode=Timer.PERIODIC, callback=mq2Reading)

while True:
    # Read the raw analog value (16-bit integer: 0 to 65535)
    if fresh:
        print(latest)
        fresh = False
        is_leakage(latest)
        



    # if raw_value > SMOKE_THRESHOLD:
    #     print("WARNING: Smoke or Gas detected!")
    # else:
    #     print("Air quality normal.")
