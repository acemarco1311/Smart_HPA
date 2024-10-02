import os
import subprocess
from concurrent import futures
import subroutine
import importlib

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
def get_service_endpoint(microservice_name):
    # alternatively, search service name by using microservice name as selector, config dependent
    service_name = microservice_name + "manager"
    # alternatively, search for port using port name "traffic", config dependent
    default_port = "5001"
    service_cluster_ip = "kubectl get service "
    service_cluster_ip += service_name
    service_cluster_ip += " -o=jsonpath='{.spec.clusterIP}'"
    service_cluster_ip = subroutine.command_error_check(service_cluster_ip)
    service_cluster_ip = service_cluster_ip.strip("'")
    service_endpoint = service_cluster_ip + ":" + default_port
    return service_endpoint

def connect_to_microservice_manager(microservice_name):
    # service_endpoint example: 10.1.1.1:5001
    service_endpoint = get_service_endpoint(microservice_name)
    # proto_module_name = "Microservice_Managers_grpc.Adservice_Manager. adservice_manager_pb2_grpc"
    file_name = microservice_name + "_" + "manager_pb2_grpc"
    module_name = "Microservice_Managers_grpc." + microservice_name.capitalize() + "_Manager."
    proto_module_name = module_name + file_name
    # service_stub_name = AdserviceManagerStub
    service_stub_name = microservice_name.capitalize() + "ManagerStub"
    try:
        # import module named adservice_manager_pb2_grpc
        grpc_module = importlib.import_module(proto_module_name)
        # get adservice_manager_pb2_grpc.AdserviceManagerStub
        service_stub_class = getattr(grpc_module, service_stub_name)
        channel = grpc.insecure_channel(service_endpoint)
        # run adservice_manager_pb2_grpc.AdserviceManagerStub(channel) to get stub
        stub = service_stub_class(channel)
        return channel, stub
    except Exception as e:
        print("An error happened when connecting and retrieving stub from server.")
        print(e)
        return None, None


# connect to microservice manager using microservice name
# and get the microservice resource data for scaling
def get_microservice_data(microservice_name):
    channel, stub = connect_to_microservice_manager(microservice_name)
    module_name = "Microservice_Managers_grpc."+ microservice_name.capitalize() + "_Manager."
    file_name = microservice_name + "_" + "manager_pb2"
    proto_module_name = module_name + file_name
    try:
        # import module named adservice_manager_pb2 for creating request
        grpc_module = importlib.import_module(proto_module_name)
        # get adservice_manager_pb2.MicroserviceDataRequest
        request_form = getattr(grpc_module, "MicroserviceDataRequest")
        # run adservice_manager_pb2.MicroserviceDataRequest() to make request
        request = request_form()
        # get response
        response_form = getattr(stub, "ExtractMicroserviceData")
        response = response_form(request)
        microservice_data = [
            response.microservice_name,
            response.scaling_action,
            response.desired_replicas,
            response.current_replicas,
            response.cpu_request,
            response.max_replicas
        ]
        return microservice_data
    except Exception as e:
        print(e)
        return None




if __name__ == '__main__':
    #health_port = "8080"
    #health_server = threading.Thread(target=serve_health, args[health_port, ])
    #health_server.start()
    print(get_microservice_data("adservice"))

