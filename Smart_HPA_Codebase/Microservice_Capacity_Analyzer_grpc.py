import os
import subprocess
from concurrent import futures

import grpc
from grpc_health.v1 import health
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc

import threading
import Microservice_Managers_grpc.Adservice_Manager.adservice_manager_pb2 as adservice_manager_pb2
import Microservice_Managers_grpc.Adservice_Manager.adservice_manager_pb2_grpc as adservice_manager_pb2_grpc

def serve_health(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    health_pb2_grpc.add_HealthServicer_to_server(health.HealthServicer(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Heartbeat server started, listening on port ", port)
    server.wait_for_termination()


# return the service address: cluster ip and port
# to connect to microservice manager via its service ip and port
def retrieve_service_address(microservice_name):
    return None

# connect to microservice manager using microservice name
# and get the microservice resource data for scaling
def get_microservice_data(microservice_name):
    return None

if __name__ == '__main__':
    health_port = "8080"
    health_server = threading.Thread(target=serve_health, args[health_port, ])
    health_server.start()

