from machine import Pin
from utime import sleep

pin = Pin("LED", Pin.OUT)

print("LED starts flashing...")
while True:
    try:
        pin.toggle()
        sleep(1) # sleep 1sec
    except KeyboardInterrupt:
        break
pin.off()
print("Finished.")


# delete codeing
# import os

# for item in os.listdir():
#     try:
#         os.remove(item)
#     except OSError:
#         print("Folder skipped:", item)