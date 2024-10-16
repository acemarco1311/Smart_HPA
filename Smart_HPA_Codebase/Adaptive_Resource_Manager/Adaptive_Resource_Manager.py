
# This file contains the resource-efficient heuristics of Smart HPA, outlining the functionality of Adaptive Resource Manager

# Perform resource exchanges between overprovisioned microservices and underprovisioned microservices

import sys
import os
import fnmatch
import glob, os
import subprocess
import math
import time
import statistics
#import openpyxl
#import numpy as np
#import psutil
#import matplotlib.pyplot as plt

import grpc
from grpc_health.v1 import health
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc
from concurrent import futures
import threading

import adaptive_resource_manager_pb2
import adaptive_resource_manager_pb2_grpc

class AdaptiveResourceManagerServicer(adaptive_resource_manager_pb2_grpc.AdaptiveResourceManagerServicer):
    def ResourceExchange(self, request, context):
        microservices_data = []
        for data in request.data:
            microservices_data.append([
                data.microservice_name,
                data.scaling_action,
                data.desired_replicas,
                data.current_replicas,
                data.cpu_request,
                data.max_replicas,
                data.cpu_percentage
            ])
        ARM_decision = Adaptive_Resource_Manager(microservices_data)
        decision_list = []
        for i in ARM_decision:
            decision_list.append(
                adaptive_resource_manager_pb2.ResourceExchangeDecision(
                    microservice_name = i[0],
                    scaling_action = i[1],
                    desired_replicas = i[2],
                    max_replicas = i[3],
                    cpu_request = i[4]
                )
            )
        response = adaptive_resource_manager_pb2.ResourceExchangeResponse()
        for i in range(len(decision_list)):
            response.decision.append(decision_list[i])

        return response

def serve(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    adaptive_resource_manager_pb2_grpc.add_AdaptiveResourceManagerServicer_to_server(AdaptiveResourceManagerServicer(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Adaptive Resource Manager server started, listening on port " + port)
    server.wait_for_termination()

def serve_health(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    health_pb2_grpc.add_HealthServicer_to_server(health.HealthServicer(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Heartbeat server for Adaptive Resource Manager started, listening on port " + port)
    server.wait_for_termination()


def Adaptive_Resource_Manager(microservices_data):

    # microservice_data = [microservice_name, SD, DR, CR, CPU request, maxR], ARM is getting this data for each microservice separately


    # ******************************************************************** Microservice Resource Inspector *************************************************************************************

    Underprovisoned_MS = []                         # Underprovisioned Microservices Details
    Overprovisioned_MS = []                         # Overprovisioned Microservices Details

    for i in range(len(microservices_data)):

        if (microservices_data[i][2] > microservices_data[i][5]):     #desired replica count > max replica count

            Required_Replicas = microservices_data[i][2] - microservices_data[i][5]       # desired - max
            Required_CPU = Required_Replicas * microservices_data[i][4]
            Underprovisoned_MS.append ([microservices_data[i][0], Required_Replicas, Required_CPU, microservices_data[i][4], microservices_data[i][3], microservices_data[i][5]])         #(microservive_name, required_replicas, required cpu, CPU request, CR, maxR)

        else:                                                         #max replica count >= desired replica count

            Residual_Replicas = microservices_data[i][5] - microservices_data[i][2]           # max - desired
            Residual_CPU = Residual_Replicas * microservices_data[i][4]
            Overprovisioned_MS.append([microservices_data[i][0], Residual_CPU, microservices_data[i][1], microservices_data[i][2], microservices_data[i][3], microservices_data[i][4], microservices_data[i][5]])     #(microservive_name, residual cpu, SD, DR, CR, CPU request)



    # ******************************************************************** Microservice Resource Balancer *************************************************************************************


    Total_Residual_CPU = 0                                      # Total_Residual_CPU for addressing the needs of underprovisioned microservices

    for i in range(len(Overprovisioned_MS)):
        Total_Residual_CPU = Total_Residual_CPU + Overprovisioned_MS[i][1]                #calculating Total_Residual_CPU possessed by overprovisioned microservices

    ARM_decision = []                                            # ARM current scaling decision details

    Underprovisoned_MS = sorted (Underprovisoned_MS, key=lambda x: x[2], reverse=True)               # Underprovisioned microservices Sorting in descending order based on required resource value (x[2]) to address heavily underprovisioned microservice first

    for i in range(len(Underprovisoned_MS)):
        possible_RR = Total_Residual_CPU / Underprovisoned_MS[i][3]                            #Total application's residual CPU divided by CPU request value for creating possible replicas for microservice i

        # can scale up to meet the resource command
        if possible_RR >= Underprovisoned_MS[i][1]:                   #possible replicas >= required replicas
            scaling_action = "scale up"
            # new_max_reps = desired_reps
            Feasible_Replicas = ARM_maxR = Underprovisoned_MS[i][1] + Underprovisoned_MS[i][5]           # required replicas + max replicas = desired replicas
            ARM_decision.append([Underprovisoned_MS[i][0], scaling_action, Feasible_Replicas, ARM_maxR, Underprovisoned_MS[i][3]])
            Total_Residual_CPU = Total_Residual_CPU - (Underprovisoned_MS[i][1] * Underprovisoned_MS[i][3])

        # can scale up but not 100% meet the resource command
        elif possible_RR >=  1 and possible_RR < Underprovisoned_MS[i][1]:     #if possible replicas are in between 1 and required replicas
            scaling_action = "scale up"
            Feasible_Replicas = ARM_maxR = math.floor (possible_RR) + Underprovisoned_MS[i][5]        # max replicas + possible RR
            ARM_decision.append([Underprovisoned_MS[i][0], scaling_action, Feasible_Replicas, ARM_maxR, Underprovisoned_MS[i][3]])
            Total_Residual_CPU = Total_Residual_CPU - (math.floor(possible_RR) * Underprovisoned_MS[i][3])

        # not enough residual cpu to scale up
        else:
            #
            if Underprovisoned_MS[i][4] < Underprovisoned_MS[i][5]:
                scaling_action = "scale up"
                Feasible_Replicas = possible_RR = Underprovisoned_MS[i][5]              #feasible replicas = max replicas
                ARM_maxR = Feasible_Replicas

            else:
                scaling_action = "no scale"
                Feasible_Replicas = possible_RR = Underprovisoned_MS[i][4]               #desired = current
                ARM_maxR = Feasible_Replicas
            ARM_decision.append([Underprovisoned_MS[i][0], scaling_action, Feasible_Replicas, ARM_maxR, Underprovisoned_MS[i][3]])  #  Adaptive Scaler


    # After addressing the needs of underprovisioned microservices, the remaining residual resource is now distributed back to the overprovisioned microservices


    Overprovisioned_MS = sorted (Overprovisioned_MS, key=lambda x: x[1], reverse=False)                  # Overprovisioned microservices Sorting in ascending order based on residual resource value (x[1]) to return resource back to less overprovisioned first


    for i in range(len(Overprovisioned_MS)):

        scaling_action = Overprovisioned_MS[i][2]
        Desired_Replicas = Overprovisioned_MS[i][3]

        Remaining_replicas = math.floor(Total_Residual_CPU / Overprovisioned_MS[i][5])        # Total_Residual_CPU divided by resource request value
        possible_RR = Desired_Replicas + Remaining_replicas

        # residual cpu can maintain user-defined max_reps
        if (possible_RR >= Overprovisioned_MS[i][6]):                                          # Overprovisioned_MS[i][6] = initial maxR (resource capacity) of microservice i
            ARM_maxR = Overprovisioned_MS[i][6]                                               # ARM_maxR is the updated capacity of the microservice i
        # can give back at least 1 more replicas but < user-defined max_reps
        # elif Remaining_replicas >= 1 and possible_RR < Overprovisioned_MS[i][6]
        elif Remaining_replicas >= 1 and ARM_maxR < Overprovisioned_MS[i][6]:
            ARM_maxR = possible_RR
        # no more residual cpu to give back, Desired_Replicas = max_reps
        else:
            ARM_maxR = Desired_Replicas

        Total_Residual_CPU = Total_Residual_CPU - ((ARM_maxR - Desired_Replicas) * Overprovisioned_MS[i][5])

        ARM_decision.append([Overprovisioned_MS[i][0], scaling_action, Desired_Replicas, ARM_maxR, Overprovisioned_MS[i][5]])  #  Adaptive Scaler

    return ARM_decision           #  Adaptive Scaler return the ARM decision to Execute component


if __name__ == '__main__':
    server_port = "50052"
    health_server_port = "8080"
    # start server
    server_thread = threading.Thread(target=serve, args=[server_port, ])
    server_thread.start()
    # start heartbeat server
    health_server_thread = threading.Thread(target=serve_health, args=[health_server_port, ])
    health_server_thread.start()
    server_thread.join()
    health_server_thread.join()
