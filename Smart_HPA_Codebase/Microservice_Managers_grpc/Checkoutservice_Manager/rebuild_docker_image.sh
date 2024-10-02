docker build -t checkoutservice-manager .
docker tag checkoutservice-manager acemarco/checkoutservice-manager
docker image push acemarco/checkoutservice-manager

dangling_id=$(docker images -f dangling=true | awk '{print $3}' | sed -n '2p')

docker rmi $dangling_id
