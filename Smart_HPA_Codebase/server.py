import grpc
from concurrent import futures
import grpc_test.adservice_manager_pb2
import grpc_test.adservice_manager_pb2_grpc

import subprocess

def Monitor():
    microservice_name = "adservice"
    Available_Replicas = "kubectl.exe get deployment adservice -o=jsonpath='{.status.availableReplicas}'"
    Available_Replicas = subprocess.check_output(Available_Replicas.split()).decode('utf-8')
    Available_Replicas = int(Available_Replicas.strip("'"))
    print(Available_Replicas) # print on server only
    Replicas_CPU_usage = "kubectl.exe top pods -l app=adservice"
    Replicas_CPU_usage = subprocess.check_output(Replicas_CPU_usage.split()).decode('utf-8')
    print(Replicas_CPU_usage) # print on server only
    return [Available_Replicas, Replicas_CPU_usage]




class AdserviceManagerServicer(grpc_test.adservice_manager_pb2_grpc.AdserviceManagerServicer):
    def ExtractMicroserviceData(self, request, context):
        microservice_name = "adservice"
        scaling_action = "no scale"
        desired_replicas = 1
        current_replicas = Monitor()[0]
        max_replicas = 5
        cpu_request = str(Monitor()[1])
        return grpc_test.adservice_manager_pb2.MicroserviceData(
            microservice_name = microservice_name,
            scaling_action = scaling_action,
            desired_replicas = desired_replicas,
            current_replicas = current_replicas,
            cpu_request = cpu_request,
            max_replicas = max_replicas
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpc_test.adservice_manager_pb2_grpc.add_AdserviceManagerServicer_to_server(AdserviceManagerServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()

