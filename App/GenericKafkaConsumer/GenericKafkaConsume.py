import json
import os
import sys
import threading
import time
import bson
import App.globalsettings as gs
import config.databaseconfig as dbc

from confluent_kafka import Consumer
from confluent_kafka.admin import AdminClient
from confluent_kafka.cimpl import NewTopic, KafkaError
from App.globalsettings import GlobalFormats
from App.GeneralUtils.GeneralUtilities import datetime_parser
from App.Json_Class.index import read_setting
from App.GenericKafkaConsumer.GenericReplicationPublisher import publish_to_replication_server
from App.GeneralUtils.index import readCalculation_file, readDeviceList
from config.databaseconfig import Databaseconfig


def kafka_ensure_or_create_topic(bootstrap_servers, topic_names):

    new_topic_created = False
    try:
        client = AdminClient({"bootstrap.servers": bootstrap_servers})
        topic_metadata = client.list_topics()
        for topicName in topic_names:
            formatted_topic = topicName.replace("-", "_")
            if topic_metadata.topics.get(formatted_topic) is None:
                new_topic_created = True
                topic_list = [NewTopic(formatted_topic, 1, 1)]
                client.create_topics(topic_list)

    except KeyboardInterrupt and Exception as ex:
        print("GenericKafkaConsumer -> GenericKafkaConsumer -> kafka_ensure_or_create_topic:", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

    finally:
        if new_topic_created:
            time.sleep(10)


def kafka_generic_consumer(mode):
    data = read_setting()
    kafka_setting = data.edgedevice.Service.Kafka
    bootstrap_servers: str = kafka_setting.cloudServers

    if mode != "web":
        read_calculation_data_json = readCalculation_file()
        device_id = read_calculation_data_json["MachineId"]
        prefix = "web"
        group_name = device_id + "_python_example_group_3"
        topic_name = [prefix + '_apiRequest_' + device_id.replace("-", "_")]
        kafka_ensure_or_create_topic(bootstrap_servers=bootstrap_servers, topic_names=topic_name)
    else:
        device_list = readDeviceList()
        prefix = "mobile"
        group_name = "web_python_example_group_4"
        topic_name = [prefix + '_apiRequest_' + obj["deviceID"].replace("-", "_") for obj in device_list]
        kafka_ensure_or_create_topic(bootstrap_servers=bootstrap_servers, topic_names=topic_name)

    kafka_consumer_config = {
        "bootstrap.servers": bootstrap_servers,
        "group.id": group_name,
        'enable.auto.commit': False,
        'session.timeout.ms': 6000,
        "auto.offset.reset": "latest",
        "allow.auto.create.topics": True,
        "api.version.request": False
    }

    # Create Consumer instance
    api_consumer = Consumer(kafka_consumer_config)
    api_consumer.subscribe(topic_name)

    try:
        while not GlobalFormats.new_device_added:
            msg = api_consumer.poll(0.1)
            if msg is None:
                continue
            elif not msg.error():
                received_value = msg.value().decode('utf-8')
                print("kafka 'Api Web' --> Consumed")
                load_value = json.loads(received_value)
                handle_replication_data(data=load_value)
                api_consumer.commit()
                # callApiAndResponseToWeb(loadValue)

            elif msg.error().code() == KafkaError._PARTITION_EOF:
                print('End of partition reached {0}/{1}'
                      .format(msg.topic(), msg.partition()))
            else:
                print('Error occurred: {0}'.format(msg.error().str()))

    except KeyboardInterrupt and Exception as ex:
        print("Kafka api Web Consumer Error:", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

    finally:
        GlobalFormats.new_device_added = False
        api_consumer.close()
        thread = threading.Thread(
            target=kafka_generic_consumer,
            args=[mode]
        )
        # Starting the Thread
        thread.start()


def handle_replication_data(data):
    try:
        collection_name = data["collectionName"]
        entry_mode = data["entryMode"]
        device_id = data["machineID"]
        query = data["query"]
        return_response = data["returnResponse"]

        if entry_mode == "C":
            create_replica(data)
        elif entry_mode == "U":
            update_replica(data)
        elif entry_mode == "D":
            delete_replica(data)
        elif entry_mode == "DM":
            delete_many_replica(data)
        elif entry_mode == "DC":
            drop_document_collection(data)
        elif entry_mode == "INC":
            increment_document_collection(data)

        if not return_response:
            print('inserted doc :', data["data"])
            publish_to_replication_server(collection_name, entry_mode, data["data"], device_id, query, True)

    except Exception as ex:
        print("handleReplicationData Error:", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)


def update_id_as_mongo_id(key, json_obj):
    if isinstance(json_obj, dict):
        for (object_key, value) in json_obj.items():

            if isinstance(value, dict):
                update_id_as_mongo_id(object_key, value)

            elif isinstance(value, list):
                for obj in value:
                    for (object_key1, value1) in obj.items():
                        if str(object_key1).lower() == str(key).lower():
                            new_value = bson.ObjectId(value1)
                            obj[object_key1] = new_value

    return json_obj


def create_replica(data):
    try:
        if not data["returnResponse"]:
            print("Insert Data")
            replica_data = json.loads(json.dumps(data["data"]), object_hook=datetime_parser)
            collection_name = data["collectionName"]
            ReplicaDocument().insert(col=collection_name, data=replica_data)
            data["data"] = replica_data
            return replica_data

        else:
            replica_data = data["data"]
            collection_name = data["collectionName"]
            device_id = data["machineID"]
            document_reference_id = replica_data["_id"]
            document_id = replica_data["ReferenceID"]
            update_document_query = {"$and": [{"_id": bson.ObjectId(document_id)}, {"machineID": device_id}]}
            updated_data = {"$set": {"ReferenceID": document_reference_id}}
            ReplicaDocument().update(col=collection_name, query=update_document_query, update_data=updated_data)
            print("Insert Successfully")
            return updated_data
    except Exception as ex:
        print("GenericKafkaConsumer -> createReplica Error:", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)


def update_replica(data):
    try:
        print(data)
        print("update request started")
        replica_data = json.loads(json.dumps(data["data"]), object_hook=datetime_parser)
        collection_name = data["collectionName"]
        document_query = data["query"]
        document_query = update_id_as_mongo_id("_id", document_query)
        ReplicaDocument().update(col=collection_name, query=document_query, update_data=replica_data)
        data["data"] = replica_data
        print("update request completed")
    except Exception as ex:
        print("updateReplica Error:", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)


def delete_replica(data):
    print("delete Successfully")
    collection_name = data["collectionName"]
    document_query = data["query"]
    ReplicaDocument().delete(col=collection_name, query=document_query)


def delete_many_replica(data):
    print("delete many Successfully")
    collection_name = data["collectionName"]
    document_query = data["query"]
    ReplicaDocument().collection_delete_many(col=collection_name, query=document_query)


def drop_document_collection(data):
    print("drop collection Successfully")
    collection_name = data["collectionName"]
    device_id = data["machineID"]
    ReplicaDocument().collection_drop(col=collection_name, machine_id=device_id)


def increment_document_collection(data):
    print("documents incremented successfully")
    increment_field = data["data"]
    document_query = data["query"]
    collection_name = data["collectionName"]
    ReplicaDocument().collection_increment(col=collection_name, increment_field=increment_field, query=document_query)


class ReplicaDocument:

    def __init__(self):
        # Read the config file objects
        data = read_setting()
        database: str = data.edgedevice.Service.MongoDB.DataBase
        connection = Databaseconfig()
        connection.connect()
        self.db = dbc.client[database]

    def insert(self, data, col):
        parameter = data
        parameter["ReferenceID"] = parameter["_id"]
        del parameter["_id"]
        collection = self.db[col]
        collection.insert_one(parameter)

    def update(self, col, query, update_data):
        collection = self.db[col]
        objects_found = collection.find_one_and_update(query, update_data)
        return objects_found

    def delete(self, col, query):
        collection = self.db[col]
        collection.delete_one(query)

    def collection_delete_many(self, col, query):
        collection = self.db[col]
        collection.delete_many(query)

    def collection_drop(self, col, machine_id):
        collection = self.db[col]
        collection.delete_many({"machineID": machine_id})

    def collection_increment(self, col, increment_field, query):
        collection = self.db[col]
        data = {'$inc': {increment_field: 1}}
        collection.find_one_and_update(query, data)
