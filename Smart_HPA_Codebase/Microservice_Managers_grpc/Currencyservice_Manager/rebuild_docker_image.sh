docker build -t currencyservice-manager .
docker tag currencyservice-manager acemarco/currencyservice-manager
docker image push acemarco/currencyservice-manager

dangling_id=$(docker images -f dangling=true | awk '{print $3}' | sed -n '2p')

docker rmi $dangling_id
