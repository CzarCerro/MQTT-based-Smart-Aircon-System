import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import paho.mqtt.client as mqtt

# Fetch the service account key JSON file contents
import callbacks
import configuration

cred = credentials.Certificate('serviceAccount.json')

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://iot-aircon-26c87-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

IP = configuration.IP

# Callback to print message
def on_message(client, userdata, msg):
    m_decode = str(msg.payload.decode("utf-8","ignore"))
    print("Subscriber: "+msg.topic, m_decode)
    db.reference(msg.topic).set(m_decode)

if __name__ == "__main__":
    #Init client
    client = mqtt.Client()
    client.on_connect = callbacks.on_connect
    client.on_disconnect = callbacks.on_disconnect
    client.on_message = on_message

    print("Connecting to broker", IP)
    client.connect(IP)  # Connect to IP address
    client.loop_start()  # Loop start
    client.subscribe("#") #Subscribe to all topics

    while True:
        pass