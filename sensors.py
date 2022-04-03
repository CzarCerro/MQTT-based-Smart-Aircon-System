import time
from threading import Thread
import paho.mqtt.client as mqtt
import callbacks
import configuration

try:
    import board
    import adafruit_dht
except:
    pass

IP = configuration.IP

operateFlag = True #Variable to start or stop publishing actions

# Temp and humidity class
class DHT11:
    temperature = ""
    humidity = ""

    # Return temperature
    def getTemp(self):
        return self.temperature

    # Return humidity
    def getHumidity(self):
        return self.humidity

    # Set temperature
    def setTemp(self, temperature):
        self.temperature = temperature

    # Set humidity
    def setHumidity(self, humidity):
        self.humidity = humidity

    # Start reading
    def run(self):

        try:
            dhtDevice = adafruit_dht.DHT11(board.D4)
        except:
            pass

        while True:
            time.sleep(0.1)
            try:
                self.setTemp(dhtDevice.temperature)
                self.setHumidity(dhtDevice.humidity)
            except:
                #If failed to init DHT11 instance, set placeholder values
                self.setTemp(23.23)
                self.setHumidity(23)





# Class for people tracking
class HeadCount:

    # Return temperature
    def getHeadCount(self):
        return 1

# Publish runner
class Publisher:
    Topic = ""
    dht11 = None
    Headcount = None

    # Initialize mqtt client instance and bind callback functions
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = callbacks.on_connect
        self.client.on_disconnect = callbacks.on_disconnect
        self.client.on_publish = callbacks.on_publish
        self.dht11 = DHT11()




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

        #Multi-threading
        Thread(target=self.dht11.run).start()
        Thread(target=self.publish).start()

    #Publish values
    def publish(self):
        try:
            self.connect()
            while operateFlag:
                self.client.publish(self.Topic+"/temperature", "{0:.2f}".format(self.dht11.getTemp()), qos=2, retain=True)
                self.client.publish(self.Topic+"/humidity", "{0:.2f}".format(self.dht11.getHumidity()), qos=2, retain=True)
                self.client.publish(self.Topic+"/headcount", str(HeadCount().getHeadCount()), qos=2, retain=True)
                time.sleep(3)
        except:
            print("Failed to establish connection")
