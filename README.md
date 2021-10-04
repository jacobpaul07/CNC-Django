# Project-BoschMCM-API

Run Command: 

    pip install -r requirements.txt

    python manage.py runserver

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
