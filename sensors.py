import time
from random import randint
from threading import Thread
import paho.mqtt.client as mqtt
import callbacks
import configuration


import board
import adafruit_dht
import RPi.GPIO as GPIO

# set GPIO Pins
ENTRANCE_TRIGGER = 23
ENTRANCE_ECHO = 24
# set GPIO Pins
EXIT_TRIGGER = 5
EXIT_ECHO = 6
# set GPIO direction (IN / OUT)
GPIO.setup(ENTRANCE_TRIGGER, GPIO.OUT)
GPIO.setup(ENTRANCE_ECHO, GPIO.IN)
GPIO.setup(EXIT_TRIGGER, GPIO.OUT)
GPIO.setup(EXIT_ECHO, GPIO.IN)


IP = configuration.IP




operateFlag = True #Variable to start or stop publishing actions

# Temp and humidity class
class DHT11:
    temperature = 0
    humidity = 0

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
                self.setTemp(randint(18, 31))
                self.setHumidity(randint(0, 100))


# Class for people tracking
class HeadCount:
    headcount = 0
    outsideFlag = False
    entranceFlag = False
    exitFlag = False
    i = 1


    # Return head count
    def getHeadCount(self):
        return self.headcount

    #Function to get distance from ultrasonic sensor
    def distance(self, trig, echo):
        # set Trigger to HIGH
        GPIO.output(trig, True)

        # set Trigger after 0.01ms to LOW
        time.sleep(0.00001)
        GPIO.output(trig, False)

        StartTime = time.time()
        StopTime = time.time()

        # save StartTime
        while GPIO.input(echo) == 0:
            StartTime = time.time()

        # save time of arrival
        while GPIO.input(echo) == 1:
            StopTime = time.time()

        # time difference between start and arrival
        TimeElapsed = StopTime - StartTime
        # multiply with the sonic speed (34300 cm/s)
        # and divide by 2, because there and back
        distance = (TimeElapsed * 34300) / 2

        return distance


    def logic(self, entrance, exit):

        if entrance < 20:
            self.entranceFlag = True

        if exit < 20:
            self.exitFlag = True

        if entrance >= 20 and self.i==1 and self.entranceFlag:
            self.outsideFlag=True
            time.sleep(0.1)
            self.i = self.i + 1
            self.entranceFlag = False

        if exit >= 20 and self.i==2 and self.exitFlag:
            print("Entering room")
            self.outsideFlag=True
            time.sleep(0.1)
            self.i = 1
            self.headcount = self.headcount + 1
            self.exitFlag = False

        if exit >= 20 and self.i == 1 and self.exitFlag:
            self.outsideFlag = True
            time.sleep(0.1)
            self.i = 2
            self.exitFlag = False

        if entrance >= 20 and self.i == 2 and self.entranceFlag:
            print("Exiting room")
            self.outsideFlag = True
            time.sleep(0.1)
            if self.headcount > 0:
                self.headcount = self.headcount - 1
            self.i = 1
            self.entranceFlag = False







    def run(self):
        try:
            while True:
                entrance = self.distance(ENTRANCE_TRIGGER, ENTRANCE_ECHO)
                exit = self.distance(EXIT_TRIGGER, EXIT_ECHO)
                self.logic(entrance,exit)
                time.sleep(0.1)



        except:
            print("ultrasonic error")
            pass




# Publish runner
class Publisher:
    Topic = ""
    dht11 = None
    headcount = None
    deviceFlag = False

    # Initialize mqtt client instance and bind callback functions
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = callbacks.on_connect
        self.client.on_disconnect = callbacks.on_disconnect
        self.client.on_publish = callbacks.on_publish
        self.dht11 = DHT11()
        self.headcount = HeadCount()

    # Sets topic from input parameter
    def setTopic(self, topic):
        self.Topic = topic

    # Toggle to use simulated values or not
    def setDeviceFlag(self, deviceFlag):
        self.deviceFlag = deviceFlag

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
        Thread(target=self.headcount.run).start()
        Thread(target=self.publish).start()

    def tempHum(self):
        device2temp = 15
        device2humidity = 30
        incrementTemp = True
        incrementHumidity = True

        while True:
            #Publish using real sensors
            if self.deviceFlag == False:
                self.client.publish(self.Topic + "/temperature", "{0:.2f}".format(self.dht11.getTemp()), qos=2, retain=True)

                self.client.publish(self.Topic + "/humidity", "{0:.2f}".format(self.dht11.getHumidity()), qos=2,
                                    retain=True)
                print(self.Topic + " publishing: " + str(self.dht11.getTemp()) + "   " + str(
                    self.dht11.getHumidity()))

            # Else, publish simulated data if argument is "device2"
            else:
                self.client.publish(self.Topic + "/temperature", device2temp, qos=2,
                                    retain=True)

                self.client.publish(self.Topic + "/humidity", device2temp, qos=2,
                                    retain=True)

                # Temperature data simulation
                if incrementTemp:
                    device2temp = device2temp + 1
                    if device2temp > 35:
                        incrementTemp = False

                else:
                    device2temp = device2temp - 1
                    if device2temp < 15:
                        incrementHumidity = True

                #Humidiity data simulation
                if incrementHumidity:
                    device2humidity = device2humidity + 1
                    if device2humidity > 55:
                        incrementHumidity = False

                else:
                    device2humidity = device2humidity - 1
                    if device2humidity < 45:
                        incrementHumidity = True

                self.client.publish(self.Topic + "/temperature", str(float(device2temp)), qos=2,
                                    retain=True)
                self.client.publish(self.Topic + "/humidity", str(float(device2humidity)), qos=2,
                                    retain=True)

            time.sleep(3)


    #Publish values
    def publish(self):
        try:
            self.connect()
            time.sleep(1)
            Thread(target=self.tempHum).start()
            while True:
                # self.client.publish(self.Topic+"/temperature", "{0:.2f}".format(self.dht11.getTemp()), qos=2, retain=True)
                # self.client.publish(self.Topic+"/humidity", "{0:.2f}".format(self.dht11.getHumidity()), qos=2, retain=True)
                self.client.publish(self.Topic+"/headcount", str(self.headcount.getHeadCount()), qos=2, retain=True)

                print(self.Topic + " publishing: " + str(self.headcount.getHeadCount()))
                time.sleep(1)
        except:
            print("Failed to establish connection")
