import time
import callbacks
import configuration
import paho.mqtt.client as mqtt

IP = configuration.IP

operateFlag = True #Variable to start or stop publishing actions

# Temp and humidity class
class DHT11:

    # Return temperature
    def getTemp(self):
        return 30

    # Return humidity
    def getHumidity(self):
        return 50


# Class for people tracking
class HeadCount:

    # Return temperature
    def getHeadCount(self):
        return 1

# Publish runner
class Publisher:
    Topic = ""

    # Initialize mqtt client instance and bind callback functions
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = callbacks.on_connect
        self.client.on_disconnect = callbacks.on_disconnect
        self.client.on_publish = callbacks.on_publish

    # Sets topic from input parameter
    def setTopic(self, topic):
        self.Topic = topic

    # Connects to broker
    def connect(self):
        print("Connecting to broker", IP)
        self.client.connect(IP)
        self.client.loop_start()
        time.sleep(1)

    # Disconnects from broker
    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()

    # Publish actions runner
    def run(self):
        self.connect()

        while operateFlag:
            self.client.publish(self.Topic+"/temperature", str(DHT11().getTemp()), qos=2, retain=True)
            self.client.publish(self.Topic+"/humidity", str(DHT11().getHumidity()), qos=2, retain=True)
            self.client.publish(self.Topic+"/headcount", str(HeadCount().getHeadCount()), qos=2, retain=True)
            time.sleep(5)
