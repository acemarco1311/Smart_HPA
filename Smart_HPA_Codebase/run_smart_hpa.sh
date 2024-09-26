#!/bin/bash
# init Knowledge Base
cd Knowledge_Base
rm *.txt
cd ..
touch Knowledge_Base/adservice.txt
touch Knowledge_Base/cartservice.txt
touch Knowledge_Base/checkoutservice.txt
touch Knowledge_Base/currencyservice.txt
touch Knowledge_Base/emailservice.txt
touch Knowledge_Base/frontend.txt
touch Knowledge_Base/paymentservice.txt
touch Knowledge_Base/productcatalogservice.txt
touch Knowledge_Base/recommendationservice.txt
touch Knowledge_Base/redis-cart.txt
touch Knowledge_Base/shippingservice.txt
echo "Test_Time (sec), CPU Usage Percentage, Current Replicas, Desired Replicas, Max Replicas, Scaling Action \n" >> Knowledge_Base/adservice.txt
echo "Test_Time (sec), CPU Usage Percentage, Current Replicas, Desired Replicas, Max Replicas, Scaling Action \n" >> Knowledge_Base/cartservice.txt
echo "Test_Time (sec), CPU Usage Percentage, Current Replicas, Desired Replicas, Max Replicas, Scaling Action \n" >> Knowledge_Base/checkoutservice.txt
echo "Test_Time (sec), CPU Usage Percentage, Current Replicas, Desired Replicas, Max Replicas, Scaling Action \n" >> Knowledge_Base/currencyservice.txt
echo "Test_Time (sec), CPU Usage Percentage, Current Replicas, Desired Replicas, Max Replicas, Scaling Action \n" >> Knowledge_Base/emailservice.txt
echo "Test_Time (sec), CPU Usage Percentage, Current Replicas, Desired Replicas, Max Replicas, Scaling Action \n" >> Knowledge_Base/frontend.txt
echo "Test_Time (sec), CPU Usage Percentage, Current Replicas, Desired Replicas, Max Replicas, Scaling Action \n" >> Knowledge_Base/paymentservice.txt
echo "Test_Time (sec), CPU Usage Percentage, Current Replicas, Desired Replicas, Max Replicas, Scaling Action \n" >> Knowledge_Base/productcatalogservice.txt
echo "Test_Time (sec), CPU Usage Percentage, Current Replicas, Desired Replicas, Max Replicas, Scaling Action \n" >> Knowledge_Base/recommendationservice.txt
echo "Test_Time (sec), CPU Usage Percentage, Current Replicas, Desired Replicas, Max Replicas, Scaling Action \n" >> Knowledge_Base/redis-cart.txt
echo "Test_Time (sec), CPU Usage Percentage, Current Replicas, Desired Replicas, Max Replicas, Scaling Action \n" >> Knowledge_Base/shippingservice.txt
# install kubectl to run kubectl command as admin
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
mv kubectl /usr/local/bin/kubectl
chmod +x /usr/local/bin/kubectl
# create cluster role binding for kubectl command
kubectl create clusterrolebinding serviceaccounts-cluster-admin --clusterrole=cluster-admin --group=system:serviceaccounts
# recompile to run as client
python3 -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. Microservice_Managers_grpc/Adservice_Manager/adservice_manager.proto
# run smart hpa
# python3 ./Microservice_Capacity_Analyzer.py
python ./test.py
