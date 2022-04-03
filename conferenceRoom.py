import sensors
Topic = "myoffice/conferenceroom"


if __name__ == "__main__":
    client = sensors.Publisher()
    client.setTopic(Topic)
    client.run()