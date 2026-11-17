from machine import Pin, Timer, ADC
import ujson
import urequests

# API settings: keep these values in sync with Project2/api/app.py.
API_URL = "http://10.232.175.68:8000/api/readings"
DEVICE_ID = "pico-mq2-1"
DEVICE_TOKEN = "8nmWa9S8z62d3Ts3RdDB68MNfjCIxWt8mTcBFCatjtw"

# ------------------------- CONSTANTS --------------------------- #
LPG_THRESHOLD = 11000
MQ2_PIN = 26
SAMPLE_PERIOD = 1000







# -------------------------------- SET-UP ------------------------- #
mq2 = ADC(Pin(MQ2_PIN))
fresh = False
latest = mq2.read_u16()


def send_reading(value):
    response = None
    try:
        response = urequests.post(
            API_URL,
            data=ujson.dumps(
                {
                    "value": int(value),
                    "device_id": DEVICE_ID
                }),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + DEVICE_TOKEN,
            },
        )
        return response.status_code == 201
    except Exception as exc:
        print("Upload failed:", exc)
        return False





# --------------------------------- FUNCTIONS ----------------------- #

def mq2Reading(n):
    global latest, fresh
    latest = mq2.read_u16()
    fresh = True

def is_leakage(value):
    if value > LPG_THRESHOLD:
        print('!!! LEAKAGE !!!')
    


# --------------------------------- MAIN LOOP ---------------------------- #

reader = Timer(-1)
reader.init(period=SAMPLE_PERIOD, mode=Timer.PERIODIC, callback=mq2Reading)

while True:
    # Read the raw analog value (16-bit integer: 0 to 65535)
    if fresh:
        print(latest)
        fresh = False
        is_leakage(latest)
        if send_reading(latest):
            print("Uploaded to database API")
        
