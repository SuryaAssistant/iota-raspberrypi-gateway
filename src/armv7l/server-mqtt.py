from config.config import *
import paho.mqtt.client as mqtt
import socket
import os


MQTT_SERVER = mqtt_addr
MQTT_PATH = gateway_name + '/' + submit_subaddr

def on_connect(client, userdata, flags, rc):
	print("=====================================================")
	print("Run MQTT with address ")
	os.system("hostname -I")
	print("\nConnected with result code " + str(rc))
	print("=====================================================")
	client.subscribe(MQTT_PATH)
    
def on_message(client, userdata, msg):
    print(msg.payload)
    payload = (msg.payload).decode('UTF-8')
    f = open("temp.txt", "a")
    f.write(payload + '\n')
    f.close()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_SERVER)

client.loop_forever()
    
