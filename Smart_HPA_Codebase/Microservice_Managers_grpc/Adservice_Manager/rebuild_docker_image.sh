docker build -t adservice-manager .
docker tag adservice-manager acemarco/adservice-manager
docker image push acemarco/adservice-manager

dangling_id=$(docker images -f dangling=true | awk '{print $3}' | sed -n '2p')

docker rmi $dangling_id
