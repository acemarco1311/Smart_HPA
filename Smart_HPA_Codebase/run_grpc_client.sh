#!/bin/bash
# recompile, avoid pb2 and pb2_grpc that was compiled inside for server
python3 -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. Microservice_Managers_grpc/Adservice_Manager/adservice_manager.proto

# run client
python3 ./Microservice_Capacity_Analyzer_grpc.py
