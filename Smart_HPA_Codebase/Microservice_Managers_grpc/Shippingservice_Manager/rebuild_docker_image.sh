docker build -t shippingservice-manager .
docker tag shippingservice-manager acemarco/shippingservice-manager
docker image push acemarco/shippingservice-manager

dangling_id=$(docker images -f dangling=true | awk '{print $3}' | sed -n '2p')

docker rmi $dangling_id
