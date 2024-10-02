docker build -t rediscart-manager .
docker tag rediscart-manager acemarco/rediscart-manager
docker image push acemarco/rediscart-manager

dangling_id=$(docker images -f dangling=true | awk '{print $3}' | sed -n '2p')

docker rmi $dangling_id
