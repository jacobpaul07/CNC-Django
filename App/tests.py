import unide
import threading
import paho.mqtt.client as mqtt
from unide.common import Device
from unide.measurement import Measurement
from unide.process import Process
import toml
import json
import os
import socket


def on_connect(client, userdata, flags, rc):
    print("Connected with code" + str(rc))
    client.subscribe("ppmp/1")
    client.subscribe("ppmp/topics")
    # subscribe Topic


# client.subscribe("topic/system")
# client.subscribe("topic/topthreememorycpunetspeed")


def on_message(client, userdata, msg):
    m_decode = str(msg.payload.decode("utf-8", "ignore"))
    # print("data Received type", type(m_decode))
    print("data Received", m_decode)
    jObject = m_decode
    print("Converting from Json to Object")
    m_in = json.loads(jObject)  # decode json data
    # print(m_in["0"])
    my_file = open(gatewayinfo, "r+")
    old = my_file.read()
    first_char = my_file.read(1)  # get the first character
    my_file.seek(0)
    topics = "[Topics]\n" + "measurement='" + m_in["measurement"] + "'\n" + "process='" + m_in["process"] + "'\n"
    my_file.write(topics)
    my_file = open(gatewayinfo)
    content = my_file.read()
    my_file.close()


client = mqtt.Client()
# client = mqtt.Client("clientId-r5aRBcaKqr")
client.connect("broker.mqttdashboard.com", 1883, 60)
client.username_pw_set("sankari", "admin")

client.on_connect = on_connect
client.on_message = on_message

gatewayinfo = './config.toml'
HOST = '0.0.0.0'  # Standard loopback interface address (localhost)
PORT = 8003  # Port to listen on (non-privileged ports are > 1023)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen()


def listen_sockets():
    threading.Timer(10.0, listen_sockets).start()

    # 14.142.211.110
    conn, addr = s.accept()
    with conn:
        # print('Connected by', addr)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall(data)
            encoding = 'utf-8'
            data2 = str(data)
            data1 = data2[30:-1]
            # b'POST /io_log HTTP/1.1\r\nHost: 192.168.0.10\r\nContent-type: application/json\r\nContent-Length: 181\r\n\r\n'
            data3 = data2.split("b'POST ")
            # data4=data3[0].split("b'")
            objGateways = json.dumps(data3[0])
            objGateways1 = json.loads(objGateways)
            objGateways2 = str(objGateways1)
            objGateways3 = objGateways2.split("b'")
            objGateways4 = objGateways2.split('"",')
            objGateways5 = json.dumps(objGateways4)
            # print(objGateways2[2:-1])
            obj5 = objGateways2[2:-1]
            obj5 = json.dumps(obj5, sort_keys=True)
            obj6 = json.loads(obj5)
            # obj7=obj6[27:20]
            # print(obj7)
            dicts_gateway = {
                obj6
            }
            dicts_4220 = {

            }
            for k in dicts_gateway:
                # print(str(k[44:61]))
                # print(str(k[102:113]))
                # print(str(k[150:157]))
                # print(str(k))
                dicts_items = {
                    "macid": str(k[44:61]),
                    "temprature": str(k[102:113]).strip(),
                    "humidity": str(k[150:157]).strip()
                }
                dicts_4220.update(dicts_items)
                stat = os.stat(gatewayinfo).st_size == 0
            if stat == True:
                print("File Empty")

            # my_file = open("./config.toml", "r+")
            # old = my_file.read()
            # first_char = my_file.read(1)  # get the first character
            # print(first_char)
            #
            # if not first_char:
            #
            #     print
            #     "file is empty"  # first character is the empty string..
            else:
                dicts_gateway = toml.load(gatewayinfo)

                # key_list = list(dicts_gateway.keys())
                val_list = list(dicts_gateway.values())

                # print(val_list[1])
                strGateway = val_list[0]
                # print(val_list[0])
                objGateway = json.dumps(strGateway)
                strgatewayinfo = '' + objGateway + ''
                objGateways = json.loads(strgatewayinfo)
                measurement_topic = objGateways["measurement"]
                process_topic = objGateways["process"]
                # print(measurement_topic)

                device = Device(dicts_4220["macid"])
                # device1 = Device("Device-002")

                # print(device)
                measurement_temp = device.measurement(temprature=dicts_4220["temprature"])
                measurement_hum = device.measurement(humidity=dicts_4220["humidity"])
                client.publish(measurement_topic, measurement_temp)
                client.publish(process_topic, measurement_hum)
                conn.close()
                # print(measurement)


# gatewayinfo='./gateway/config/config.toml'
#
#
#
#
#
# #print(content)
#
#
# #print(json.dumps(strGateway))
# objGateway=json.dumps(strGateway)
# print(objGateway)
# strgatewayinfo=''+objGateway+''
# objGateways=json.loads(strgatewayinfo)
#
# strGatewayId=objGateways["deviceid"]
# strAccessKey=objGateways["key"]
# strSecretKey=objGateways["secret"]
#
# print(strGatewayId)
# print(strAccessKey)
# print(strSecretKey)
#
#
# device = Device("Device-001")
# device1 = Device("Device-002")
#
# print(device)
# measurement = device.measurement(temperature=36.7)
# process=device.operationalStatus
# device.operationalStatus="Running"
# print(measurement)
# client.publish(topic="sample", measurement)
#
#
# print(device)
# client.publish(topic="ppmp/1","temperature=36.7")
#
# def push_topics():
#
#     threading.Timer(10.0, push_topics).start()
#     stat= os.stat(gatewayinfo).st_size == 0
#     if stat==True:
#      print("File Empty")
#
#     # my_file = open("./config.toml", "r+")
#     # old = my_file.read()
#     # first_char = my_file.read(1)  # get the first character
#     # print(first_char)
#     #
#     # if not first_char:
#     #
#     #     print
#     #     "file is empty"  # first character is the empty string..
#     else:
#         dicts_gateway = toml.load(gatewayinfo)
#
#         # key_list = list(dicts_gateway.keys())
#         val_list = list(dicts_gateway.values())
#
#         # #print(val_list[1])
#         strGateway=val_list[0]
#         print(val_list[0])
#         objGateway=json.dumps(strGateway)
#         strgatewayinfo=''+objGateway+''
#         objGateways=json.loads(strgatewayinfo)
#         measurement_topic=objGateways["measurement"]
#         process_topic=objGateways["process"]
#         print(measurement_topic)
#
#         client.publish(measurement_topic, measurement)
#         client.publish(process_topic, measurement)
#         print(measurement)

# push_topics()
listen_sockets()
client.loop_forever()
