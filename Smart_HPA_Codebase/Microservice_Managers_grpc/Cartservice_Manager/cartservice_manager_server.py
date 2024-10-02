import grpc
from grpc_health.v1 import health
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc

from concurrent import futures
import sys
import os
import subprocess
import math
import statistics
import threading

import cartservice_manager_pb2
import cartservice_manager_pb2_grpc
import subroutine


def Monitor():
    microservice_name = "cartservice"
    # change kubectl to kubectl.exe if running locally
    Available_Replicas = "kubectl get deployment cartservice -o=jsonpath='{.status.availableReplicas}'"
    Available_Replicas = subroutine.command_error_check(Available_Replicas)
    if Available_Replicas is not None:
        Available_Replicas= int(Available_Replicas.strip("'"))

    Replicas_CPU_usage = "kubectl top pods -l app=cartservice"
    Replicas_CPU_usage = subroutine.command_error_check(Replicas_CPU_usage)

    Operational_Replicas = None
    if Replicas_CPU_usage is not None:
        Operational_Replicas = len(Replicas_CPU_usage.splitlines()) - 1

    current_replicas = Available_Replicas

    cpu_add = []
    if Replicas_CPU_usage is not None:
        for line in Replicas_CPU_usage.splitlines()[1:]:
            columns = line.split()
            cpu_usage = columns[1]
            cpu_usage = cpu_usage[:-1]
            cpu_add = cpu_add + [int(cpu_usage)]
    else:
        cpu_add = None


    current_cpu = None
    if cpu_add is not None:
        current_cpu = math.ceil(statistics.mean(cpu_add))


    Desired_Replicas = "kubectl get deployment cartservice -o=jsonpath='{.spec.replicas}'"
    Desired_Replicas = subroutine.command_error_check(Desired_Replicas)
    if Desired_Replicas is not None:
        Desired_Replicas = int(Desired_Replicas.strip("'"))


    cpu_request = "kubectl get deployment cartservice -o=jsonpath='{.spec.template.spec.containers[0].resources.requests.cpu}'"
    cpu_request = subroutine.command_error_check(cpu_request)
    if cpu_request is not None:
        cpu_request = cpu_request[:-2]
        cpu_request = int(cpu_request.strip("'"))


    target_cpu = 50 # user defined cpu limit, cannot get from .yaml file as pod needs to exceed limit resource for triggering scaling
    max_replica = 5 # user defined max replicas, not being handled by smarthpa yet
    min_replica = 1 # default

    return microservice_name, Desired_Replicas, current_replicas, current_cpu, target_cpu, cpu_request, max_replica, min_replica


def Analyse (Desired_Replicas, current_replicas, current_cpu, target_cpu, cpu_request, min_replica):
    try:
        cpu_percentage = (current_cpu / cpu_request) * 100
        previous_desired_replicas = Desired_Replicas
        desired_replica = math.ceil(int(current_replicas) * (int(cpu_percentage) / int(target_cpu)))

        if (previous_desired_replicas != desired_replica) and (desired_replica > current_replicas) and (desired_replica >= min_replica):
            scaling_action = "scale up"
        elif (previous_desired_replicas != desired_replica) and (desired_replica < current_replicas) and (desired_replica >= min_replica):
            scaling_action = "scale down"
        else:
            scaling_action = "no scale"
        return cpu_percentage, scaling_action, desired_replica
    except:
        return None, "ERROR", None





class CartserviceManagerServicer(cartservice_manager_pb2_grpc.CartserviceManagerServicer):
    def ExtractMicroserviceData(self, request, context):
        microservice_name, P_Desired_Replicas, current_replicas, current_cpu, target_cpu, cpu_request, max_replica, min_replica = Monitor()
        cpu_percentage, scaling_action, desired_replica = Analyse(P_Desired_Replicas, current_replicas, current_cpu, target_cpu, cpu_request, min_replica)
        cartservice_data = [microservice_name, scaling_action, desired_replica, current_replicas, cpu_request, max_replica, cpu_percentage]

        # example data
        # adservice_data = ["adservice", "no scale", 1, 1, 50, 5]
        # if error
        # adservice_data = ["adservice", "ERROR", 0, 0, 0, 0]

        return cartservice_manager_pb2.MicroserviceData(
            microservice_name = cartservice_data[0],
            scaling_action = cartservice_data[1],
            desired_replicas = cartservice_data[2],
            current_replicas = cartservice_data[3],
            cpu_request = cartservice_data[4],
            max_replicas = cartservice_data[5],
            cpu_percentage = cartservice_data[6]
        )

def serve(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    cartservice_manager_pb2_grpc.add_CartserviceManagerServicer_to_server(CartserviceManagerServicer(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Cartservice Manager server started, listening on port " + port)
    server.wait_for_termination()

def serve_health(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    health_pb2_grpc.add_HealthServicer_to_server(health.HealthServicer(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Heartbeat server for Cartservice Manager started, listening on port " + port)
    server.wait_for_termination()


if __name__ == '__main__':
    server_port = "50052"
    health_server_port = "8080"
    server_thread = threading.Thread(target=serve, args=[server_port, ])
    server_thread.start()
    health_server_thread = threading.Thread(target=serve_health, args=[health_server_port, ])
    health_server_thread.start()
    server_thread.join()
    health_server_thread.join()
