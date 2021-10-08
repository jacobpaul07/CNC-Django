# Project-BoschCNC-API

Run Command: 

    pip install -r requirements.txt

    python manage.py runserver

### API POST commands:
  1. To START OPCUA-Client

    API: $ curl --data "" http://127.0.0.1:8000/api/startopc
  2. To STOP OPCUA-Client

    API: $ curl --data "" http://127.0.0.1:8000/api/stopopc

  3. To change the EdgeGateway Properties
     
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
  4. To Change DataService-OPCUA-Properties

    API: http://localhost:8000/api/changeDataService
    BODY:
    {
    "mode": "update",
    "Type": "OPCUAProperties",
    "data": {
        "Enable": "True",
        "ClientName": "OPC_SIMULATION_CLIENT",
        "url": "opc.tcp://DESKTOP-Q78JC4A.mshome.net:53530/OPCUA/SimulationServer",
        "UpdateTime": "5",
        "Param": "Parameters",
        "RetryCount": "3",
        "RecoveryTime": "10"
        }
    }

  5. To **Change** DataService-OPCUA-Parameter-MeasurementTags

    API: http://localhost:8000/api/changeDataService
    BODY:
    {
    "mode": "update",
    "Type": "OPCUAParameterMeasurementTags",
    "data":{
    "MeasurementTag": [
        {
            "NameSpace": "3",
            "Identifier": "1001",
            "DisplayName": "Temperature",
            "InitialValue": "0"
        },
        {
            "NameSpace": "3",
            "Identifier": "1002",
            "DisplayName": "Pressure",
            "InitialValue": "0"
        },
        {
            "NameSpace": "3",
            "Identifier": "1003",
            "DisplayName": "Flow",
            "InitialValue": "0"
        }
    ]
    }  
    }
  6. To **Create** DataService-OPCUA-Parameter-MeasurementTags

    API: http://localhost:8000/api/changeDataService
    BODY:
    {
    "mode": "create",
    "Type": "OPCUAParameterMeasurementTags",
    "data":{
    "MeasurementTag": [
        {
            "NameSpace": "3",
            "Identifier": "1001",
            "DisplayName": "Temperature",
            "InitialValue": "0"
        },
        {
            "NameSpace": "3",
            "Identifier": "1002",
            "DisplayName": "Pressure",
            "InitialValue": "0"
        },
        {
            "NameSpace": "3",
            "Identifier": "1003",
            "DisplayName": "Flow",
            "InitialValue": "0"
        }
    ]
    }  
    }
  7. To **Delete** DataService-OPCUA-Parameter-MeasurementTags

    API: http://localhost:8000/api/changeDataService
    BODY:
    {
    "mode": "delete",
    "Type": "OPCUAParameterMeasurementTags",
    "data":{
    "MeasurementTag": [
        {
            "NameSpace": "3",
            "Identifier": "1001",
            "DisplayName": "Temperature",
            "InitialValue": "0"
        },
        {
            "NameSpace": "3",
            "Identifier": "1002",
            "DisplayName": "Pressure",
            "InitialValue": "0"
        },
        {
            "NameSpace": "3",
            "Identifier": "1003",
            "DisplayName": "Flow",
            "InitialValue": "0"
        }
    ]
    }  
    }
  8. To change DataService-MQTT-Properties
     
    API: http://localhost:8000/api/changeDataService
    BODY:
    {
    "mode": "update",
    "Type": "OPCUAProperties",
    "data": {
        "Enable": "true",
        "subscriptionTopic": "IOTC3WSX0001/Event",
        "serverIpAddress": "54.160.238.163",
        "serverPort": "1883"
        }
    }
  9. To Change Services - Redis 

    API: http://localhost:8000/api/changeDataService
    BODY:
    {
    "mode": "update",
    "Type": "Redis",
    "data": {
        "IpAddress": "127.0.0.1",
         "Port": "6379"
        }
    }

  10. To Change Services - MongoDB:
    
    API: http://localhost:8000/api/changeDataService
    BODY:
    {
    "mode": "update",
    "Type": "MongoDB",
    "data": {
        "connectionString": "127.0.0.1:27017",
        "DataBase": "CNC"
        }
    }
    
  11. To Start WebSocket 
  
    API: $ curl --data "" http://127.0.0.1:8000/api/startWebSocket
    
  12. To Stop WebSocket 

    API: $ curl --data "" http://127.0.0.1:8000/api/stopWebSocket

### To Activate Redis 5
    docker run -p 6379:6379 -d redis:5

### To Activate MongoDB
    docker run -p 27016:27017 -d mongo:latest

### API Data format:

    {
        "ip" : "192.168.1.40",
        "port" : "502",
        "deviceName" : "TCPdevice01" 
    }

### Docker Image:
    
    1. linux/arm64 -->  siqsessedge/cnc-api:v2  
    2. linux/amd64 -->  siqsessedge/cnc-api:linux-arm

    Eg: docker pull siqsessedge/cnc-api:v2

### Docker Run:

    docker run -t -p 8000:8000 siqsessedge/cnc-api:v2

### Docker container ls:

    Format:
    docker exec -it (CONTAINER ID) /bin/bash  
    Example:
    docker exec -it c2c727b2624e /bin/bash


### Docker commands:

    docker run --name cncapi --net projectnetwork --ip 172.18.0.5 -p 8000:8000 siqsessedge/cnc-api:v2
    docker run --net projectnetwork --ip 172.18.0.3 mongo:latest
    docker run --net projectnetwork --ip 172.18.0.4 redis:5
    
    docker network inspect bosch-mcm-overall_static-network

    docker network create --subnet=172.18.0.0/16 mynet123
    docker run --net mynet123 --ip 172.18.0.22 -it ubuntu bash
    docker network ls

### Docker Build with different architecture:

    docker build -t siqsessedge/cnc-api:linux-arm --push --platform linux/arm64 .


### Docker Compose Example

    version: '3'
    services:
    
      backend:
        image: "siqsessedge/cnc-api:v2"
        ports:
          - "8000:8000"
        depends_on: 
          - redis
          - mongo
        networks:
          cnc-network:
            ipv4_address: 174.22.0.3
        restart: always
    
      redis:
        image: "redis:5"
        ports:
          - "6379:6379"
        networks:
          cnc-network:
            ipv4_address: 174.22.0.4
        restart: always
    
      mongo:
        image: "mongo:latest"
        ports:
          - "27016:27017"
        networks:
          cnc-network:
            ipv4_address: 174.22.0.2
        restart: always
    
    networks:
      cnc-network:
        ipam:
          config:
            - subnet: 174.22.0.0/16

