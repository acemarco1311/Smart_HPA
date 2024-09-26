#!/bin/bash
# recomplile inside so that the server can import pb2, pb2_grpc and then run successfully
python3 -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. adservice_manager.proto

# install kubectl to run commands
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
mv kubectl /usr/local/bin/kubectl
chmod +x /usr/local/bin/kubectl

# create tcluster role binding for kubectl command
kubectl create clusterrolebinding serviceaccounts-cluster-admin --clusterrole=cluster-admin --group=system:serviceaccounts

# run the server
python3 ./adservice_manager_server.py
