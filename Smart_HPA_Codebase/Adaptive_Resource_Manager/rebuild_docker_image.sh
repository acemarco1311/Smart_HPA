#!/bin/bash
docker build -t adaptive-resource-manager .
docker tag adaptive-resource-manager acemarco/adaptive-resource-manager
docker image push acemarco/adaptive-resource-manager

dangling_id=$(docker images -f dangling=true | awk '{print $3}' | sed -n '2p')

docker rmi $dangling_id
