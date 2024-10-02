#!/bin/bash
# recompile
python3 -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. adaptive_resource_manager.proto

python3 ./Adaptive_Resource_Manager.py
