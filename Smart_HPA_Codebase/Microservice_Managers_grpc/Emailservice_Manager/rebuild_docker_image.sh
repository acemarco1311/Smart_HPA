docker build -t emailservice-manager .
docker tag emailservice-manager acemarco/emailservice-manager
docker image push acemarco/emailservice-manager

dangling_id=$(docker images -f dangling=true | awk '{print $3}' | sed -n '2p')

docker rmi $dangling_id
