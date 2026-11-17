from machine import Pin, PWM, ADC, Timer
from time import ticks_ms, ticks_diff
from drive_strength import set_drive_strength
# --------------------CONSTANTS---------------------------------- #
LED_PIN        = 0      # YOUR LED's GPIO number, from its flag
POT_PIN = 26
LDR_PIN = 27
DARK = 1000
BRIGHT = 61000
SAMPLE_MS = 1
BRIGHTER_BUTTON_PIN  = 13      # YOUR button's GPIO number, from its flag
DEBOUNCE_MS    = 0.8      # YOUR Session 10 DEBOUNCE_S, in milliseconds
AB_DEBOUNCE = 0.9
HEARTBEAT_MS   = 500     # how often the heartbeat flips
PWM_FREQ       = 500    # YOUR LED's PWM frequency, in Hz
DRIVE_STRENGTH = 12      # YOUR LED's drive strength, in mA
DIMMER_BUTTON_PIN = 15
AB_BUTTON_PIN = 14

FULL_SCALE = 65535

LEVEL = [10,20,30,40,50,60,70,80,90]
level = 0

# ----------------------SETUP-------------------------------------#
led = PWM(Pin(0))
led.freq(PWM_FREQ)
Dimmer_button = Pin(DIMMER_BUTTON_PIN, Pin.IN, Pin.PULL_UP)
Brighter_button = Pin(BRIGHTER_BUTTON_PIN, Pin.IN, Pin.PULL_UP)
AB_button = Pin(AB_BUTTON_PIN, Pin.IN, Pin.PULL_UP)
heart = Pin("LED", Pin.OUT)       # the on-board LED
pot = ADC(Pin(POT_PIN))
ldr = ADC(Pin(LDR_PIN))
latest = 20 #Most recent LDR reading
fresh = False

pressCount = 0
led_on = False
last_beat = ticks_ms()            # when the heartbeat last flipped
edge_seen = False                 # the flag: the handler saw an edge
last_edge = ticks_ms()            # when it saw the most recent one
stable = Brighter_button.value()
dimmer_stable = Dimmer_button.value()
abstable = AB_button.value()
dedge_seen = False 
last_dedge = ticks_ms()          # the last reading the loop trusted
taps = 0
beat_ms = ticks_ms()
beat_gap = 0
beat_new = False
abge_seen = False
last_abge = ticks_ms()
abge_count = 0
is_adaptive = False
last = 0 #####################################################
caller = 'LDR'




# -----------------------FUNCTIONS------------------------------ #
def set_brightness(level):           # 0 to 100, the same job as yours
    led.duty_u16(int(level * 65535 / 100))


def sample(t):
    global latest, fresh,last
    last = latest
    latest = ldr.read_u16()
    fresh = True

def beat(t):
    # heart.toggle()

    global beat_ms,beat_gap,beat_new
    now = ticks_ms()
    beat_gap = ticks_diff(now,beat_ms)
    beat_ms = now
    beat_new = True
    heart.toggle()


def on_edge(pin):                 # the handler: note WHEN, nothing else
    global edge_seen, last_edge
    last_edge = ticks_ms()
    edge_seen = True
    
def on_dedge(pin):
    global dedge_seen, last_dedge
    last_dedge = ticks_ms()
    dedge_seen = True

def on_abge(pin):
    global abge_seen, last_abge
    last_abge = ticks_ms()
    abge_seen = True


def brighter_pressed():                    # True once per press, after the bounce
    global edge_seen, stable
    if edge_seen and ticks_diff(ticks_ms(), last_edge) >= DEBOUNCE_MS:
        edge_seen = False
        now = Brighter_button.value()
        if now != stable:
            stable = now
            if now == 0:          # it settled pressed
                return True
    return False

def dimmer_pressed():
    global dedge_seen, dimmer_stable
    if dedge_seen and ticks_diff(ticks_ms(), last_dedge) >= DEBOUNCE_MS:
        dedge_seen = False
        now = Dimmer_button.value()
        if now != dimmer_stable:
            dimmer_stable = now
            if now == 0:          # it settled pressed
                return True
        # print('P')
    return False    

def ab_pressed():
    global abge_seen, abstable
    if abge_seen and ticks_diff(ticks_ms(), last_abge) >= DEBOUNCE_MS:
        abge_seen = False
        now = AB_button.value()
        if now != abstable:
            abstable = now
        if now == 0:
            return True
    return False

def light_percent(ldrCount):
    if ldrCount < DARK:
        return 0
    elif ldrCount > BRIGHT:
        return 100
    else:
        return 100 - ((ldrCount / BRIGHT) * 100) 

def report_beat():
    global beat_new
    if beat_new:
        beat_new =False
        print("heartbeat period:",beat_gap,"ms")

def step(val):
    global discrete, LEVEL
    if discrete + val == len(LEVEL) or discrete + val == -1:
        pass
    else:
        discrete += val 
    print('step call')

def set_discrete(val, is_up):
    global discrete, LEVEL
    if is_up:
        for i in range(len(LEVEL)):
            if LEVEL[i] >= val:
                discrete = i
    else:
        for i in range(len(LEVEL)-2):
            if LEVEL[i] >= val:
                discrete = i + 1

    # if discrete < 0:
    #     discrete = 0
    # if discrete >= len(LEVEL):
    #     discrete = len(LEVEL) - 1


    


def toggle_ab():
    global is_adaptive
    is_adaptive = not is_adaptive

# --------------------MAIN LOOP-------------------------------- #
Brighter_button.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=on_edge)
Dimmer_button.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=on_dedge)
AB_button.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=on_abge)
heartbeat = Timer(period=HEARTBEAT_MS, mode=Timer.PERIODIC, callback=beat)
sampler = Timer(period=SAMPLE_MS, mode=Timer.PERIODIC,  callback=sample)



# while True:
#     if fresh:
#         fresh = False
#         ldrCount = ldr.read_u16()
#         set_brightness(100 - light_percent(ldrCount))
#     if brighter_pressed():
#         step(+1)
#     if dimmer_pressed():
#         step(-1)
#     report_beat()
        # print(ldrCount)


discrete = 2
ldrControl = True
countLDR = 0
while True:
    if ab_pressed():
        ldrControl = True
        toggle_ab()

    if is_adaptive:
        set_discrete(light_percent(countLDR),True)
        if ldrControl:
            if fresh:
                countLDR = ldr.read_u16()
                set_brightness(light_percent(countLDR))
                set_discrete(light_percent(countLDR),True)
        if brighter_pressed():
            ldrControl = False
            set_discrete(countLDR, True)
            step(+1)
            set_brightness(LEVEL[discrete])

        if dimmer_pressed():
            ldrControl = False
            set_discrete(countLDR, True)
            step(-1)
            set_brightness(LEVEL[discrete])

        print(light_percent(last), light_percent(latest))
        if abs(light_percent(last) - light_percent(latest)) >= 20:
            ldrControl = True
            print('reset')

    else:
        set_brightness(LEVEL[discrete])
        if brighter_pressed():
            step(1)
        if dimmer_pressed():
            step(-1)
        set_brightness(LEVEL[discrete])
