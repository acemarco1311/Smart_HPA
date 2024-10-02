docker build -t cartservice-manager .
docker tag cartservice-manager acemarco/cartservice-manager
docker image push acemarco/cartservice-manager

dangling_id=$(docker images -f dangling=true | awk '{print $3}' | sed -n '2p')

docker rmi $dangling_id
