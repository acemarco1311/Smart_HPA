### SmartHPA

This repository contains implementation details of hierarchical architecture and resource-efficient heuristics of Smart HPA, which allows the exchange of resources among microservices, facilitating effective auto-scaling of microservices in resource-constrained environments.  

### Table of Contents

The package contains the following directories.

#### 1. Benchmark Application
This folder includes the source and deployment files for the microservice benchmark application and the load test script.

#### 2. SmartHPA Codebase
This folder contains the scripts for Microservice Managers dedicated to each microservice within the benchmark application. The scripts for the Adaptive Resource Manager and Microservice Capacity Analyzer components are also included as part of codebase.

#### 3. Results
This directory refers to the Knowledge Base of SmartHPA. The monitored metrics for both Smart HPA and Kubernetes HPA for every iteration conducted in the load test are recorded. The results include data from 10 experimental runs for both SmartHPA and Kubernetes HPA, along with workload data for each individual run.

#### 4. Results Analysis Script
The script used for determining and analyzing the evaluation metrics from the recorded data to assess the performance of Smart HPA is here in this folder. 

#### 5. Results Visualization Script
The script in this folder is used for data visualization and generating the bar and line graphs presented in the paper.


