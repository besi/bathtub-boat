from network import WLAN, STA_IF, AP_IF
from time import sleep_ms
import secrets
import machine
import utime
import time

import neopixel
np = neopixel.NeoPixel(machine.Pin(10),1)
#### Careful GRB instead of RGB ###
np.fill((0,10,0));np.write()
time.sleep(0.3)
def try_connection(timeout = 12):

    while not wlan.isconnected() and timeout > 0:
        print('.', end='')
        sleep_ms(500)
        timeout = timeout - 1
    return wlan.isconnected();

wlan = WLAN(STA_IF)
wlan.active(True)

ap = WLAN(AP_IF)
ap.active(False)

# Only for deep sleep ?
# print('connecting to last AP', end='')
# print(try_connection(3))
print("\nStartup...")
np.fill((0,0,10));np.write()
if not wlan.isconnected():
    ap_list = wlan.scan()
    ## sort APs by signal strength
    ap_list.sort(key=lambda ap: ap[3], reverse=True)
    ## filter only trusted APs
    ap_list = list(filter(lambda ap: ap[0].decode('UTF-8') in
              secrets.wifi.aps.keys(), ap_list))
    for ap in ap_list:
        essid = ap[0].decode('UTF-8')
        if not wlan.isconnected():
            print('connecting to "', essid, end='"')
            wlan.connect(essid, secrets.wifi.aps[essid])
            print(try_connection())



# Update the time
from ntptime import settime
settime()
utime.sleep_ms(1000)

import gc
gc.collect()

print(wlan.ifconfig()[0])
import webrepl
webrepl.start()

np.fill((10,0,0));np.write()