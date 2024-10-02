docker build -t paymentservice-manager .
docker tag paymentservice-manager acemarco/paymentservice-manager
docker image push acemarco/paymentservice-manager

dangling_id=$(docker images -f dangling=true | awk '{print $3}' | sed -n '2p')

docker rmi $dangling_id
