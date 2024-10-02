#!/bin/bash
# recomplile inside so that the server can import pb2, pb2_grpc and then run successfully
echo "Recompiling..."
python3 -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. recommendationservice_manager.proto
echo "Recompiling DONE"


# install kubectl to run commands
echo "Installing kubectl..."
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
mv kubectl /usr/local/bin/kubectl
chmod +x /usr/local/bin/kubectl
echo "Installed kubectl DONE"

# create tcluster role binding for kubectl command
echo "Creating clusterrolebinding"
kubectl create clusterrolebinding serviceaccounts-cluster-admin --clusterrole=cluster-admin --group=system:serviceaccounts
echo "clusterrolebinding created"

# run the server
echo "Running server..."
python3 ./recommendationservice_manager_server.py
