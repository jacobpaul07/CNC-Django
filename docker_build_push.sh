#!/bin/bash

docker build -t siqsessedge/cnc-api:CNC-v9.0 . --no-cache
docker push siqsessedge/cnc-api:CNC-v9.0
