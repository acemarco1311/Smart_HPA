docker build -t frontend-manager .
docker tag frontend-manager acemarco/frontend-manager
docker image push acemarco/frontend-manager

dangling_id=$(docker images -f dangling=true | awk '{print $3}' | sed -n '2p')

docker rmi $dangling_id
