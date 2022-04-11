import aircon
roomType = "conferenceroom"

if __name__ == "__main__":
    Aircon = aircon.Subscriber()
    Aircon.setTopic(roomType)
    Aircon.run()