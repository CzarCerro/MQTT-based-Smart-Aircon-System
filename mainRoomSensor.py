import sys
import sensors
Topic = "myoffice/mainroom"


if __name__ == "__main__":
    client = sensors.Publisher()
    client.setTopic(Topic)

    #If system argument = device2, use simulated values instead
    try:
        if sys.argv[1] == "device2":
            client.setDeviceFlag(True)
    except:
        pass


    client.run()