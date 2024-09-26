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

def getSome():
    with grpc.insecure_channel('10.1.6.91:50051') as channel:
        stub = adservice_manager_pb2_grpc.AdserviceManagerStub(channel)
        response = stub.ExtractMicroserviceData(adservice_manager_pb2.MicroserviceDataRequest())
        adservice_data = [
            response.microservice_name,
            response.scaling_action,
            response.desired_replicas,
            response.current_replicas,
            response.cpu_request,
            response.max_replicas
        ]
        print(adservice_data)
        return adservice_data
if __name__ == '__main__':
    # run heartbeat
    port = "8080"
    health_server = threading.Thread(target=serve_health, args=[port, ])
    health_server.start()
    for i in range(10):
        getSome()


