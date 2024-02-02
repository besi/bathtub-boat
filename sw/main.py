import secrets
import time
import ubinascii
import umqttsimple
from umqttsimple import MQTTClient 

import neopixel
np = neopixel.NeoPixel(machine.Pin(10),1) # New Pin 9
#### Careful GRB instead of RGB ###

DELAY = 5
IDEAL = 41
## MQTT
client_id = ubinascii.hexlify(machine.unique_id())
topic_pub = secrets.mqtt.topic
mqtt_server = secrets.mqtt.host
mqtt_port = secrets.mqtt.port
mqtt_user = secrets.mqtt.user
mqtt_password = secrets.mqtt.password

# 1 Wire
import machine
import onewire, ds18x20
from onewire import OneWireError
dat = machine.Pin(9) # New Pin 4
ds = ds18x20.DS18X20(onewire.OneWire(dat))

# If another sensor is plugged in the internal one will be ignored.
internalSensor = bytearray(b'(\xd8)\x95\xf0\x01<D')

def waitForSensors(ds):
    np.fill((10,0,0));np.write()
    sensors = []
    while len(sensors) == 0:
        sensors = ds.scan()
        print('found devices:', sensors)
        if len(sensors) == 0:
            time.sleep(1)
        if len(sensors) > 1:
            print("Ignoring internal sensor")
            sensors.remove(internalSensor)
    np.fill((10,10,10));np.write()
    return sensors

sensors = waitForSensors(ds)

def connect():
  # if you set keepalive value - you have to send something to mqtt server to inform that you are alive in less time than keepalive value of seconds.
  client = MQTTClient(client_id, mqtt_server, mqtt_port, mqtt_user, mqtt_password,keepalive=DELAY * 2)
  client.set_last_will(topic_pub, '{ "status":"offline"} ', retain=False, qos=0)
  client.connect()
  print('Connected to %s MQTT broker' % mqtt_server)
  client.publish(topic_pub, bytes('{"status":"hello"}', 'utf-8'))
  return client


def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  machine.reset()


try:
  print("Connecting to MQTT...")
  client = connect()
except OSError as e:
  restart_and_reconnect()

startup = True

def updateLED(temp):
    (red,green,blue) = (0,0,0)
    green = max((255 - abs(int((IDEAL - temp) * 30))),0)

    if temp < IDEAL:
        blue = max((int((IDEAL - temp) * 30)),0) 
    else:
        red = min((int((temp - IDEAL) * 60)),255)

    d = 15 # dim the leds by this factor
    np.fill((int(green/d), int(red/d), int(blue/d)))
    np.write()


while True:
  try:
    ds.convert_temp()
    for sensor in sensors:
        t = ds.read_temp(sensor)
        if startup and (int(t) == 85 or int(t) == 0 or int(t) == 25):
            print(f"Ignoring {int(t)} degrees at startup")
        print("Temperature: %f" % t)
        updateLED(t)
        client.publish(topic_pub, bytes('{"temp":%f}'% t, 'utf-8'))
        startup = False
    time.sleep(DELAY)
  except OneWireError as e:
      print("Sensor lost")
      sensors =  waitForSensors(ds)
  except OSError as e:
    restart_and_reconnect()
  except Exception as e:
      print("Sensor lost")
      sensors =  waitForSensors(ds)
