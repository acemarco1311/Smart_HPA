docker build -t productcatalogservice-manager .
docker tag productcatalogservice-manager acemarco/productcatalogservice-manager
docker image push acemarco/productcatalogservice-manager

dangling_id=$(docker images -f dangling=true | awk '{print $3}' | sed -n '2p')

docker rmi $dangling_id
