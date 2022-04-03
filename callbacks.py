"""
For reuseable callbacks. Customized callbacks are overriden if needed
"""

# Prints log messages
from paho.mqtt.client import connack_string


def on_log(client, userdata, level, buf):
    print("Log: " + buf)

# Callback to print connection status
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Successfully connected with result: "+ connack_string(rc))
    else:
        print("Bad connection")

# Callback to print disconnect status
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")
    else:
        print("Disconnected from broker")

# Callback to print disconnect status
def on_publish(client, userdata, mid):
    print("Published data")
    pass

# Callback to print message
def on_message(client, userdata, msg):
    topic = msg.topic
    m_decode = str(msg.payload.decode("utf-8","ignore"))
    print("Subscriber: "+msg.topic, m_decode)