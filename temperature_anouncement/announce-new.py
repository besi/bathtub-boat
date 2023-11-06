import subprocess

import paho.mqtt.client as mqtt
import secrets

mqtt_server = secrets.mqtt.host
mqtt_port = secrets.mqtt.port
mqtt_user = secrets.mqtt.user
mqtt_password = secrets.mqtt.password


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT server '%s'" % mqtt_server)
        client.subscribe("services/temperature")


def on_message(client, userdata, msg):
    handleMessage(msg)

def execute_shell(commands):
    subprocess.call(commands)


def handleMessage(msg):
    tag = msg.payload.decode("utf-8").strip()
    print(tag)
    execute_shell(['say', 'todo'])


client = mqtt.Client(client_id="", clean_session=True, userdata=None, protocol=mqtt.MQTTv31, transport="tcp")
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(mqtt_user, mqtt_password)
client.connect(mqtt_server, mqtt_port)
client.loop_forever()
