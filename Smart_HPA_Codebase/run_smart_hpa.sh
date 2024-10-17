#!/bin/bash
# install kubectl to run kubectl command as admin
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
mv kubectl /usr/local/bin/kubectl
chmod +x /usr/local/bin/kubectl
# create cluster role binding for kubectl command
kubectl create clusterrolebinding serviceaccounts-cluster-admin --clusterrole=cluster-admin --group=system:serviceaccounts
# recompile to run as client
python3 -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. Microservice_Managers_grpc/Adservice_Manager/adservice_manager.proto
python3 -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. Microservice_Managers_grpc/Cartservice_Manager/cartservice_manager.proto
python3 -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. Microservice_Managers_grpc/Checkoutservice_Manager/checkoutservice_manager.proto
python3 -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. Microservice_Managers_grpc/Currencyservice_Manager/currencyservice_manager.proto
python3 -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. Microservice_Managers_grpc/Emailservice_Manager/emailservice_manager.proto
python3 -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. Microservice_Managers_grpc/Frontend_Manager/frontend_manager.proto
python3 -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. Microservice_Managers_grpc/Paymentservice_Manager/paymentservice_manager.proto
python3 -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. Microservice_Managers_grpc/Productcatalogservice_Manager/productcatalogservice_manager.proto
python3 -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. Microservice_Managers_grpc/Recommendationservice_Manager/recommendationservice_manager.proto
python3 -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. Microservice_Managers_grpc/Rediscart_Manager/rediscart_manager.proto
python3 -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. Microservice_Managers_grpc/Shippingservice_Manager/shippingservice_manager.proto

python3 -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. Adaptive_Resource_Manager/adaptive_resource_manager.proto

# run smart hpa
# python3 ./Microservice_Capacity_Analyzer.py
python ./Microservice_Capacity_Analyzer_grpc.py
