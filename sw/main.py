import secrets
import time
import ubinascii
import umqttsimple
from umqttsimple import MQTTClient 

DELAY = 5

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
dat = machine.Pin(9)
ds = ds18x20.DS18X20(onewire.OneWire(dat))
sensors = ds.scan()
print('found devices:', sensors)
ds.read_temp(sensors[0]) # Prevent reading 85 Degrees at startup
time.sleep(.5)
ds.read_temp(sensors[0]) # Prevent reading 85 Degrees at startup

def connect():
  # if you set keepalive value - you have to send something to mqtt server to inform that you are alive in less time than keepalive value of seconds.
  client = MQTTClient(client_id, mqtt_server, mqtt_port, mqtt_user, mqtt_password,keepalive=1000)
  client.connect()
  client.set_last_will(topic_pub, '{{ "status":"offline"}} ', retain=False, qos=0)
  print('Connected to %s MQTT broker' % mqtt_server)
  
  return client


def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  machine.reset()


try:
  print("Connecting to MQTT...")
  client = connect()
except OSError as e:
  restart_and_reconnect()

while True:
  try:
    ds.convert_temp()
    for sensor in sensors:
        t = ds.read_temp(sensor)
        print("Temperature: %f" % t) 
        client.publish(topic_pub, bytes('{"temp":%f}'% t, 'utf-8'))
    time.sleep(DELAY)
  except OSError as e:
    restart_and_reconnect()
