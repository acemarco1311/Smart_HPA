import grpc
from concurrent import futures
import sys
import os
import subprocess

sys.path.append('..')
import Microservice_Managers_grpc.Adservice_Manager.adservice_manager_pb2 as adservice_manager_pb2
import Microservice_Managers_grpc.Adservice_Manager.adservice_manager_pb2_grpc as adservice_manager_pb2_grpc

class AdserviceManagerServicer(adservice_manager_pb2_grpc.AdserviceManagerServicer):
    def ExtractMicroserviceData(self, request, context):
        microservice_name = "adservice"
        scaling_action = "no scale"
        desired_replicas = 1
        current_replicas = 1
        max_replicas = 5
        cpu_request = 10
        return adservice_manager_pb2.MicroserviceData(
            microservice_name = microservice_name,
            scaling_action = scaling_action,
            desired_replicas = desired_replicas,
            current_replicas = current_replicas,
            cpu_request = cpu_request,
            max_replicas = max_replicas
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    adservice_manager_pb2_grpc.add_AdserviceManagerServicer_to_server(AdserviceManagerServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
