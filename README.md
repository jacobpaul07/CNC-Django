# Project-BoschMCM-API

Run Command: 

    pip install -r requirements.txt

    python manage.py runserver

### API POST commands:
  1. To change IP and Port

    API: $ curl --data "{"ip" : "192.168.1.40","port" : "502","deviceName" : "TCPdevice01"}" http://127.0.0.1:8000/api/changetcpip
  2. To START ModbusTCP

    API: $ curl --data "" http://127.0.0.1:8000/api/starttcp
  3. To STOP ModbusTCP

    API: $ curl --data "" http://127.0.0.1:8000/api/stoptcp
  4. To START PPMP Service

    API: $ curl --data "" http://127.0.0.1:8000/api/startppmp
  5. To STOP PPMP Service

    API: $ curl --data "" http://127.0.0.1:8000/api/stopppmp
  6. To START ModbusRTU

    API: $ curl --data "" http://127.0.0.1:8000/api/startrtu
  7. To STOP ModbusRTU

    API: $ curl --data "" http://127.0.0.1:8000/api/stoprtu
  8. To read the Device Settings
    
    API: $ curl --data "" http://127.0.0.1:8000/api/ReadDeviceSettings
  9. To change the EdgeGateway Properties
     
    API: http://localhost:8000/api/changeDataCenterProperties
    BODY:
    {
    "Name": "Edge Device",
    "Mode1": "UNO-2271 Linux",
    "Password": "123456",
    "Identity": "S3-0001",
    "IP Address": "192.168.1.15",
    "Time Zone": "+05:30",
    "Description": "Siqsess Edge gateway Integrate with Bosch Nexeed Platform "
    }

  9. To Change the DataCenter-Port Properties

    API: http://localhost:8000/api/changeDataCenterProperties
    BODY:
    {
    "mode": "update",
    "deviceType": "COM2",
    "data": {
        "Enable": "False",
        "Type": "Serial",
        "Name": "Selec Twix 2",
        "Description": "Built in Serial port RS232/rs422/rs485",
        "Scan Time(ms)": "11000",
        "Time Out(ms)": "13000",
        "Retry Count": "13",
        "Auto Recover Time(s)": "10",
        "SerialPort Setting": {
            "Method": "rtu",
            "Port": "COM",
            "Baud Rate": "9600",
            "Data Bit": "8",
            "Stop Bit": "11",
            "Timeout": "1",
            "Parity": "N",
            "RTS": "False",
            "DTR": "False"
            }
        }
    }
  10. To Change DataCenter-Device Properties

    API: http://localhost:8000/api/changeDataCenterDeviceProperties
    BODY:
    {
    "mode": "update",
    "deviceType": "COM2",
    "deviceName":"COM2-Device-02",
    "data": {
        "Enable": "True",
        "Name": "COM2-Device-02",
        "Device Type": "Modbus RTU",
        "Device Model": "ADAM",
        "Unit Number": "2",
        "Description": "Slave 1",
        "Add device name as prefix to IO Tag": "Enable",
        "Extention Properties": {
            "CheckSum": "Enable",
            "Protocol": "Modbus",
            "ModbusDigital block size": "16",
            "Modbus Analog block Size": "16"
        }
      }
    }

  11. To change DataCenter-Device IOTags  (Sensor Properties)
     
    API: http://localhost:8000/api/changeDataCenterDeviceIOTags
    BODY:
    {
    "mode": "update",
    "deviceType": "COM2",
    "deviceName":"COM2-Device-01",
    "data": [
            {
                "Name": "Temperature",
                "Signal Type": "AI Signal",
                "Conversion": "IEEE Float Point",
                "Address": "6",
                "Span High": "1000",
                "Span Low": "0",
                "Unit High": "0",
                "Unit Low": "10",
                "Initial Value": "0.0",
                "Scan Rate": "1",
                "Read Write": "Read Only",
                "initvalue": "10",
                "Description": "Temperature Sensor"
            },
            {
                "Name": "Pressure",
                "Signal Type": "AI",
                "Conversion": "IEEE Float Point",
                "Address": "1",
                "Span High": "65535",
                "Span Low": "0",
                "Unit High": "10",
                "Unit Low": "0",
                "Initial Value": "0.0",
                "Scan Rate": "1",
                "Read Write": "Read Only",
                "initvalue": "10",
                "Description": "Level 1"
            },
            {
                "Name": "Flow",
                "Signal Type": "AI ",
                "Conversion": "IEEE Float Point",
                "Address": "2",
                "Span High": "65535",
                "Span Low": "0",
                "Unit High": "10",
                "Unit Low": "0",
                "Initial Value": "0.0",
                "Scan Rate": "1",
                "Read Write": "Read Only",
                "initvalue": "10",
                "Description": "Flow 2"
            }
        ]
    }

  12. To Change PPMP Properties 

    API: http://localhost:8000/api/changeDataServiceProperties
    BODY:
    {
    "mode": "update",
    "deviceType": "PPMP",
    "data": {
        "Enable": "True",
        "contentspec": "urn:spec://eclipse.org/unide/measurement-message#v3",
        "timestamp": "2021-07-06T10:53:01.545Z"
        }
    }

  13. To Change the PPM Station Settings:
    
    API: http://localhost:8000/api/changePpmpStations
    BODY:
    {
    "service":"changePpmpStations",
    "mode": "update",
    "deviceType": "PPMP",
    "StationID": "ST10",
    "data": [
        {
        "Enable": "True",
        "API": "https://demo.bosch-nexeed.com/cpm/ppm/v3/measurement",
        "UpdateTime": "10",
        "MeasurementTag": [
            {
                "TagName": "Temperature",
                "TagValue": "10.0",
                "Status": "updated",
                "Device Name": "TCPdevice01",
                "Device-Type": "TCP"
            },
            {
                "TagName": "Pressure",
                "TagValue": "11.0",
                "Status": "ideal",
                "Device Name": "TCPdevice01",
                "Device-Type": "TCP"
            }
        ],
        "StationID": "ST10",
        "DeviceID": null
        }
    ]
}
  15. To Start WebSocket 
  
    API: $ curl --data "" http://127.0.0.1:8000/api/startWebSocket
    
  13. To Stop WebSocket 

    API: $ curl --data "" http://127.0.0.1:8000/api/stopWebSocket

### To Activate Redis 5
    docker run -p 6379:6379 -d redis:5
### API Data format:

    {
        "ip" : "192.168.1.40",
        "port" : "502",
        "deviceName" : "TCPdevice01" 
    }

### Docker Image:
  
    docker pull siqsessjacob/boschmcm_api

### Docker Run:

    docker run -t -p 8000:8000 siqsessjacob/boschmcm_api

### Docker container ls:

    Format:
    docker exec -it (CONTAINER ID) /bin/bash  
    Example:
    docker exec -it c2c727b2624e /bin/bash


### Docker commands:

    docker run --name mcmapi --net projectnetwork --ip 172.18.0.5 -p 8000:8000 mcm-api:dev3
    docker run --net projectnetwork --ip 172.18.0.22 mongo:latest
    docker run --net projectnetwork --ip 172.18.0.4 redis:5
    
    docker network inspect bosch-mcm-overall_static-network

    docker network create --subnet=172.18.0.0/16 mynet123
    docker run --net mynet123 --ip 172.18.0.22 -it ubuntu bash
    docker network ls

### Docker Compose Example

    version: '3'

    services:
    
      backend:
        image: "mcm-api:dev3"
        ports:
          - "8000:8000"
        depends_on: 
          - redis
        networks:
          static-network:
            ipv4_address: 172.20.0.3
        restart: always
    
      frontend:
        image: "siqsessjacob/mcm-ui:latest"
        ports:
          - "3000:3000"
        depends_on: 
          - backend
        networks:
          static-network:
            ipv4_address: 172.20.0.5
        restart: always
    
      redis:
        image: "redis:5"
        ports:
          - "6379:6379"
        networks:
          static-network:
            ipv4_address: 172.20.0.4
        restart: always
    
    networks:
      static-network:
        ipam:
          config:
            - subnet: 172.20.0.0/16
