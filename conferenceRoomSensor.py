import sensors
import sys
Topic = "myoffice/conferenceroom"


if __name__ == "__main__":
    client = sensors.Publisher()
    client.setTopic(Topic)

    #If system argument = device2, use simulated values instead
    if sys.argv[1] == "device2":
        client.setDeviceFlag(True)

    client.run()