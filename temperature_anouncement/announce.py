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
        execute_shell(['say', 'temperature announcement started'])


def on_message(client, userdata, msg):
    handleMessage(msg)

def execute_shell(commands):
    subprocess.call(commands)


def handleMessage(msg):
    global LAST_TEMP
    import json
    # print(msg.payload.decode('utf-8'))
    payload = msg.payload.decode("utf-8").strip()
    data = json.loads(payload)
    if 'temp' in data:
        temp = int(data['temp'])
        string = f"{int(temp)} degrees"
        if temp != LAST_TEMP:
            print(string)
            execute_shell(['say', string])
            LAST_TEMP = temp
    
    if 'status' in data:
        status = data['status']
        LAST_TEMP = -1
        if status == 'hello':
            execute_shell(['say', 'sensor detected'])
        if status == 'offline':
            execute_shell(['say', 'sensor disconnected'])

print("Starting...")
client = mqtt.Client(client_id="", clean_session=True, userdata=None, protocol=mqtt.MQTTv31, transport="tcp")
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(mqtt_user, mqtt_password)
client.connect(mqtt_server, mqtt_port)
client.loop_forever()
