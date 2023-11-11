import subprocess

import paho.mqtt.client as mqtt
import secrets

mqtt_server = secrets.mqtt.host
mqtt_port = secrets.mqtt.port
mqtt_user = secrets.mqtt.user
mqtt_password = secrets.mqtt.password


LAST_TEMP = -1

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT server '%s'" % mqtt_server)
        client.subscribe("services/bathtub")


def on_message(client, userdata, msg):
    handleMessage(msg)

def execute_shell(commands):
    subprocess.call(commands)


def handleMessage(msg):
    global LAST_TEMP
    import json
    data = msg.payload.decode("utf-8").strip()
    temp = int(json.loads(data)['temp'])
    string = f"{int(temp)} degrees"
    
    if temp != LAST_TEMP:
        print(string)
        execute_shell(['say', string])
        LAST_TEMP = temp


client = mqtt.Client(client_id="", clean_session=True, userdata=None, protocol=mqtt.MQTTv31, transport="tcp")
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(mqtt_user, mqtt_password)
client.connect(mqtt_server, mqtt_port)
client.loop_forever()
