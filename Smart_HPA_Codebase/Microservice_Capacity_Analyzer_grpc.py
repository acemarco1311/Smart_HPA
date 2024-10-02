import os
import subprocess
from concurrent import futures
import subroutine
import importlib
import time
from subroutine import *
import multiprocessing
from multiprocessing import Pool
from Adaptive_Resource_Manager import *

import grpc
from grpc_health.v1 import health
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc

import threading


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
        return [microservice_name, channel, stub]
    except Exception as e:
        print("An error happened when connecting and retrieving stub from server.")
        print(e)
        return None


def connect_to_adaptive_resource_manager():
    service_endpoint = get_service_endpoint("adaptiveresource")
    proto_module_name = "Adaptive_Resource_Manager.adaptive_resource_manager_pb2_grpc"
    service_stub_name = "AdaptiveResourceManagerStub"
    try:
        # import module named adaptive_resource_manager_pb2_grpc
        grpc_module = importlib.import_module(proto_module_name)
        #  get adaptive_resource_manager.AdaptiveResourceManagerStub
        service_stub_class = getattr(grpc_module, service_stub_name)
        channel = grpc.insecure_channel(service_endpoint)
        # run adaptive_resource_manager_pb2_grpc.AdaptiveResourceManagerStub(channel)
        stub = service_stub_class(channel)
        return stub, channel
    except Exception as e:
        print("An error happened when connecting to Adaptive Resource Manager.")
        print(e)
        return None, None



# connect to microservice manager using microservice name
# and get the microservice resource data for scaling
def get_microservice_data(microservice_name, stub):
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
            response.max_replicas,
            response.cpu_percentage
        ]
        return microservice_data
    except Exception as e:
        print(e)
        return None

def get_resource_exchange(stub, microservice_data):
    proto_module_name = "Adaptive_Resource_Manager.adaptive_resource_manager_pb2"
    try:
        # import module adaptive_resource_manager_pb2
        grpc_module = importlib.import_module(proto_module_name)
        # get adaptive_resource_manager_pb2.ResourceExchangeRequest() to make request
        request_form = getattr(grpc_module, "ResourceExchangeRequest")
        request_list = []
        for microservice in microservice_data:
            form = getattr(grpc_module, "MicroserviceData")
            request_list.append(
                form(
                    microservice_name = microservice[0],
                    scaling_action = microservice[1],
                    desired_replicas = microservice[2],
                    current_replicas = microservice[3],
                    cpu_request = microservice[4],
                    max_replicas = microservice[5],
                    cpu_percentage = microservice[6]
                )
            )
        request = request_form()
        for i in range(len(request_list)):
            request.data.append(request_list[i])
        # get response
        response_form = getattr(stub, "ResourceExchange")
        response = response_form(request)
        ARM_decision = []
        for r in response.decision:
            ARM_decision.append([r.microservice_name, r.scaling_action, r.desired_replicas, r.max_replicas, r.cpu_request])

        return ARM_decision
    except Exception as e:
        print("Error happened during resource exchange")
        print(e)
        return None



def Execute(microservice_name, desired_replicas):
    execute_command = f"kubectl scale deployment {microservice_name} --replicas={desired_replicas}"
    os.system(execute_command)
    return

def connect_all(microservice_list):
    connection_list = []
    executor = futures.ThreadPoolExecutor(max_workers=len(microservice_list))
    future_list = []
    for name in microservice_list:
        future_list.append(executor.submit(connect_to_microservice_manager, name))
    for fut in futures.as_completed(future_list):
        connection_list.append(fut.result())
    executor.shutdown()
    return connection_list

def get_all(connection_list):
    microservice_data = []
    executor = futures.ThreadPoolExecutor(max_workers=len(connection_list))
    future_list = []
    for connection in connection_list:
        future_list.append(executor.submit(get_microservice_data, connection[0], connection[2]))
    for fut in futures.as_completed(future_list):
        microservice_data.append(fut.result())
    executor.shutdown()
    return microservice_data



def run(desired_time, microservice_list):

    ARM_saved_decision = []         # Adaptive Resource Manager scaling decision and updated maxR details of previous interation

    row_number = 2                    # for storing maximum replicas and desired replicas values in Knowledge Base

    start_time = time.time()


    connection_list = connect_all(microservice_list)

    adaptive_stub, adaptive_channel = connect_to_adaptive_resource_manager()

    while (time.time() - start_time) < desired_time:

        Test_Time = time.time() - start_time

        # ********************************************************************** Running Microservice Managers Parallely in fully Decentralized manner ************************************************************************

        microservices_data = get_all(connection_list)
        unavailable_microservices_data = []
        for i in microservices_data:
            print(i)
            microservice_name, cpu_percentage, current_replicas, desired_replicas = i[0], i[6], i[3], i[2]
            write_content(f"./Knowledge_Base/{microservice_name}.txt", Test_Time, cpu_percentage, current_replicas, desired_replicas)


        ARM_decision = []                 # ARM = Adaptive Resource Manager, ARM current scaling decision and maxR details will be saved here


        # **********************************************************************  Microservice Capacity Analyzer **********************************************************************

        for i in range(len(microservices_data)):
            if (microservices_data[i][2]>microservices_data[i][5]):        # desirsed replica count > max. replica count, for microservice i;  this represents Resource Constrained Situation

                for i in range(len(microservices_data)):
                    for j in range(len(ARM_saved_decision)):
                        if microservices_data[i][0] == ARM_saved_decision[j][0]:
                            microservices_data[i][5] = ARM_saved_decision[j][3]          # Changing SLA-defined maxR to the ResourceWise maxR of previous ARM decision for each microservice

                # ARM_decision = Adaptive_Resource_Manager(microservices_data)                     # Calling Adaptive Resource Manager
                ARM_decision = get_resource_exchange(adaptive_stub, microservices_data)

                ARM_saved_decision = ARM_decision

                break

        #When all microservices operate within their resource capacity (i.e., resource-rich environment) -> desirsed replica count < max. replica count

        processes = []
        if len(ARM_decision) == 0:

            ARM_saved_decision = microservices_data                          #to equalize the length
            for i in range(len(microservices_data)):
                for j in range(len(ARM_saved_decision)):
                    if microservices_data[i][0] == ARM_saved_decision[j][0]:
                        ARM_saved_decision[j][3] = microservices_data[i][5]


            for i in range(len(microservices_data)):
                filename = microservices_data[i][0]
                filepath = f'./Knowledge_Base/{filename}.txt'
                max_reps = microservices_data[i][5]
                scaling_decision = microservices_data[i][1]
                add_content(filepath, row_number, max_reps, scaling_decision)

                # ************************************************** Executing Scaling Decisions made by Microservice Managers **********************************************************************

                if microservices_data[i][1] != "no scale":
                    process = multiprocessing.Process(target=Execute, args=(microservices_data[i][0], microservices_data[i][2]))
                    processes.append(process)
                    process.start()
            for process in processes:            # Wait for all processes to finish
                process.join()

            # write to unavailable data as well
            for i in range(len(unavailable_microservices_data)):
                filename = unavailable_microservices_data[i][0]
                filepath = f'./Knowledge_Base/{filename}.txt'
                max_reps = unavailable_microservices_data[i][5]
                scaling_decision = unavailable_microservices_data[i][1]
                add_content(filepath, row_number, max_reps, scaling_decision)




        # for Resource Constrained Situation, when Adaptive Resource Manager makes changes to max_Replicas and desired replicas

        else:
            for i in range(len(ARM_decision)):
                filename = ARM_decision[i][0]
                filepath = f'./Knowledge_Base/{filename}.txt'
                updated_max_reps = ARM_decision[i][3]
                updated_scaling_decision = ARM_decision[i][1]
                add_content(filepath, row_number, updated_max_reps, updated_scaling_decision)



                # ************************************************** Executing ResourceWise Scaling Decisions made by Adaptive Resource Managers **********************************************************************

                if ARM_decision[i][1] != "no scale":
                    process = multiprocessing.Process(target=Execute, args=(ARM_decision[i][0], ARM_decision[i][2]))
                    processes.append(process)
                    process.start()
            for process in processes:            # Wait for all processes to finish
                process.join()

            # write for unavailable microservices
            for i in range(len(unavailable_microservices_data)):
                filename = unavailable_microservices_data[i][0]
                filepath = f'./Knowledge_Base/{filename}.txt'
                max_reps = unavailable_microservices_data[i][5]
                scaling_action = unavailable_microservices_data[i][1]
                add_content(filepath, row_number, max_reps, scaling_action)

        row_number = row_number+1


        print ("ARM_decision", ARM_decision)





microservice_list = [
    "adservice",
    "cartservice",
    "checkoutservice",
    "paymentservice",
    "currencyservice",
    "frontend",
    "rediscart",
    "productcatalogservice",
    "recommendationservice",
    "shippingservice",
    "emailservice",
]

if __name__ == '__main__':
    health_port = "8080"
    health_server = threading.Thread(target=serve_health, args=[health_port, ])
    health_server.start()
    run(600, microservice_list)
