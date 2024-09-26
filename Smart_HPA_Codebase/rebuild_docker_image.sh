#!/bin/bash
docker build -t smart-hpa .
docker tag smart-hpa acemarco/smart-hpa
docker image push acemarco/smart-hpa

dangling_id=$(docker images -f dangling=true | awk '{print $3}' | sed -n '2p')

docker rmi $dangling_id
