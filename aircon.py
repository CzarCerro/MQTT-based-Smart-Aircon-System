import time
from threading import Thread
import paho.mqtt.client as mqtt

import callbacks
import configuration

try:
    from sense_hat import SenseHat

    s = SenseHat()
except:
    pass

IP = configuration.IP

MAX_PEOPLE = 10

black = (0, 0, 0)
blue = (0, 0, 255)
red = (255, 0, 0)
green = (0, 255, 0)
yellow = (255, 255, 0)


class Aircon:
    blank = [black] * 64
    display = [black] * 64
    mainroomCount = 0
    conferenceroomCount = 0
    ID = ""
    client = ""

    # Set ID
    def setID(self, ID):
        self.ID = ID

    # Cooling/normal mode
    def cool(self):
        for i in range(4):
            self.display[i + 24] = blue
            self.display[i + 32] = blue

        for i in range(4):
            self.display[i + 24 + 4] = black
            self.display[i + 32 + 4] = black

    # Dehumidifying mode
    def dry(self):
        for i in range(4):
            self.display[i + 24] = black
            self.display[i + 32] = black

        for i in range(4):
            self.display[i + 24 + 4] = red
            self.display[i + 32 + 4] = red

    def temperature(self, control):
        if control < 0.13:
            control = 0.13
        if control > 1:
            control = 1

        for i in range(8):
            self.display[i] = black
            self.display[i + 8] = black

        for i in range(int(8 * control)):
            self.display[i] = yellow
            self.display[i + 8] = yellow

    def power(self, control):
        print(control)
        if control < 0.13:
            control = 0.13
        if control > 1:
            control = 1


        # Reset LED display
        for i in range(8):
            self.display[i + 48] = black
            self.display[i + 56] = black

        for i in range(int(8 * control)):
            self.display[i + 48] = green
            self.display[i + 56] = green

    def process(self, topic, value):

        # Either run in cooling or drying mode, depending on the humidity sensed.
        if "humidity" in topic:
            if float(value) < 50:
                self.cool()
            else:
                self.dry()

        if "temperature" in topic:
            value = float(value)
            value = value - 15
            control = round(1 - (value / (31 - 15)), 1)
            self.temperature(control)

        if topic == "myoffice/mainroom/headcount":
            self.mainroomCount = int(value)

        if topic == "myoffice/conferenceroom/headcount":
            if int(value) <= self.mainroomCount:
                self.conferenceroomCount = int(value)

    def processPower(self):

        print(str(self.mainroomCount) + " " + str(self.conferenceroomCount))
        if self.mainroomCount == 0:
            self.power(0)
        else:
            if self.ID == "conferenceroom":

                self.power(float(self.conferenceroomCount/10.0))

            elif self.ID == "mainroom":
                print("mainroom")
                self.power((self.mainroomCount-self.conferenceroomCount)/MAX_PEOPLE)


    def run(self):
        while True:
            self.processPower()
            try:
                s.set_pixels(self.display)
            except:
                print(self.display)
                pass
            time.sleep(1)


class Subscriber:
    Topic = ""
    client = ""
    aircon = Aircon()

    # Initialize mqtt client instance and bind callback functions
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = callbacks.on_disconnect
        self.client.on_message = self.on_message

    # Sets topic from input parameter
    def setTopic(self, topic):
        self.Topic = topic
        self.aircon.setID(topic)

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

        # Multi-threading
        Thread(target=self.subscribe).start()
        Thread(target=self.aircon.run()).start()

    # Callback to handle connection status
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Successfully connected with result: " + mqtt.connack_string(rc))
            topic = "myoffice/" + self.Topic + "/temperature"
            print("Subscribing to " + topic)
            self.client.subscribe(topic)

            topic = "myoffice/" + self.Topic + "/humidity"
            print("Subscribing to " + topic)
            self.client.subscribe(topic)

            topic = "myoffice/+/" + "headcount"
            print("Subscribing to " + topic)
            self.client.subscribe(topic)

        else:
            print("Bad connection")

    # Receive message callback
    def on_message(self, client, userdata, msg):
        m_decode = str(msg.payload.decode("utf-8", "ignore"))
        print(self.Topic + " " + msg.topic, m_decode)

        self.aircon.process(msg.topic, m_decode)

    def subscribe(self):
        try:
            self.connect()

            while True:
                pass
        except:
            print("Failed to establish connection")
