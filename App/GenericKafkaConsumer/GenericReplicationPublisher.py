import json
import os
import sys
from App.Json_Class.Edge import Edgefromdict
from App.GenericKafkaConsumer.GenericKafkaPublisher import kafka_generic_publisher


def read_setting():
    filePath = './App/JsonConfiguration/JSONCONFIG.json'
    with open(filePath) as f:
        json_string = json.load(f)
        a = Edgefromdict(json_string)
        f.close()
    return a


def publish_to_replication_server(collection_name, entry_mode, loaded_data, device_id, query, return_response):
    try:
        json_settings = read_setting()
        kafka_setting = json_settings.edgedevice.Service.Kafka
        cloud_servers: str = kafka_setting.cloudServers
        prefix = "mobile" if os.environ["ApplicationMode"] != "web" else "web"
        kafka_topic = prefix + '_apiRequest_' + device_id.replace("-", "_")
        obj_request = {
            "collectionName": collection_name,
            "entryMode": entry_mode,
            "data": loaded_data,
            "machineID": device_id,
            "query": query,
            "returnResponse": return_response
        }
        request_data = json.dumps(obj_request, default=str)

        kafka_generic_publisher(kafka_server=cloud_servers, kafka_topic=kafka_topic, message=request_data)
    except Exception as ex:
        print("publishToReplicationServer Error:", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
