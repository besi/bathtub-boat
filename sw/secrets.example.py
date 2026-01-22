class boat:
    internalSensor = bytearray(bytes.fromhex('deadbeef'))

class wifi:
   aps = {
       'SSID1': 'PASSWORD1',
       'SSID2': 'PASSWORD2',       
       }

class mqtt:
    host = 'mqtt://yourserver.com'
    topic = b'your/topic'
    topic_wled = b'wled/all/col'
    user = 'john'
    password = 'secret'
    port = 1883
