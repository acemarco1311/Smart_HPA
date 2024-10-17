#!/bin/bash
# run Adaptive Resource Manager
kubectl.exe apply -f adaptive_manifests.yaml
# run Microservice Managers
kubectl.exe apply -f adservice-manager-manifests.yaml
# run volume
kubectl.exe apply -f volume-manifests.yaml
# run microservice and Smart HPA
kubectl.exe apply -f test-manifests.yaml
