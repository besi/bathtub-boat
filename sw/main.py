import secrets
import time
import ubinascii
import umqttsimple
from umqttsimple import MQTTClient 
from machine import Pin, reset, unique_id

import neopixel
np = neopixel.NeoPixel(Pin(9),1)
#### Careful GRB instead of RGB ###

DELAY = 3
IDEAL = 40
## MQTT
client_id = ubinascii.hexlify(unique_id())
topic_pub = secrets.mqtt.topic
topic_wled = secrets.mqtt.topic_wled
mqtt_server = secrets.mqtt.host
mqtt_port = secrets.mqtt.port
mqtt_user = secrets.mqtt.user
mqtt_password = secrets.mqtt.password

# 1 Wire

import onewire, ds18x20
from onewire import OneWireError
dat = Pin(4) # was pin 9
ds = ds18x20.DS18X20(onewire.OneWire(dat))

print(f"Internal sensor 0x{secrets.internalSensor.hex()}")

def waitForSensors(ds):
    np.fill((0,10,10));np.write()
    sensors = []
    while len(sensors) == 0:
        sensors = ds.scan()
        [print(f"Found sensor 0x{sensor.hex()}") for sensor in sensors]

        if len(sensors) == 0:
            time.sleep(1)
        if len(sensors) > 1:
            # If another sensor is plugged in the internal one will be ignored.
            print("Ignoring internal sensor")
            sensors.remove(internalSensor)
    np.fill((10,10,10));np.write()
    return sensors

sensors = waitForSensors(ds)

def connect():
  # if you set keepalive value - you have to send something to mqtt server to inform that you are alive in less time than keepalive value of seconds.
  client = MQTTClient(client_id, mqtt_server, mqtt_port, mqtt_user, mqtt_password,keepalive=DELAY * 2)
  client.set_last_will(topic_pub, '{ "status":"offline","temp":-999} ', retain=False, qos=0)
  client.connect()
  print('Connected to %s MQTT broker' % mqtt_server)
  client.publish(topic_pub, bytes('{"status":"hello","temp":-999}', 'utf-8'))
  return client


def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  reset()


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
    return (red,green,blue)


while True:
  try:
    ds.convert_temp()
    for sensor in sensors:
        t = ds.read_temp(sensor)
        if startup and (int(t) == 85 or int(t) == 0 or int(t) == 25):
            print(f"Ignoring {int(t)} degrees at startup")
        print("Temperature: %f" % t)
        (r,g,b) = updateLED(t)
        client.publish(topic_pub, bytes('{"temp":%f}'% t, 'utf-8'))
        client.publish(topic_wled, bytes(f'#{r:02x}{g:02x}{b:02x}', 'utf-8'))
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

