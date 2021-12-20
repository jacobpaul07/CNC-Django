
def returnApiToIoT(params: dict, url: str):

    deviceId = params["deviceID"]

    # Kafka Request Produce --> Url and device ID
    # Kafka Response Consumer --> Different Topic
