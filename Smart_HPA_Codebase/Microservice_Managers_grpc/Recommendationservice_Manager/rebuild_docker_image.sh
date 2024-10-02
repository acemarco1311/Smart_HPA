docker build -t recommendationservice-manager .
docker tag recommendationservice-manager acemarco/recommendationservice-manager
docker image push acemarco/recommendationservice-manager

dangling_id=$(docker images -f dangling=true | awk '{print $3}' | sed -n '2p')

docker rmi $dangling_id
