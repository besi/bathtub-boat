import webrepl
from neopixel import NeoPixel
from time import sleep
from machine import Pin

np = NeoPixel(Pin(9),1) # GRB

np.fill((0,10,0));np.write()
sleep(0.3)
import startwifi
np.fill((0,10,10));np.write()
sleep(.5)
webrepl.start()
