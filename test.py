import paho.mqtt.client as mqtt
import time

import callbacks
import configuration











# Set instance name
client = mqtt.Client()

# Bind to callback functions
client.on_connect = callbacks.on_connect
client.on_disconnect = callbacks.on_disconnect
client.on_message = callbacks.on_message
client.on_publish = callbacks.on_publish

IP = configuration.IP

print("Connecting to broker", IP)



client.connect(IP)  # Connect to IP address
client.loop_start()  # Loop start
client.subscribe("myoffice/conferenceroom/temperature")

while True:
    pass