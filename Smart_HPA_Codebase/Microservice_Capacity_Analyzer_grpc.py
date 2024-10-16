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
    service_endpoint = None
    service_name = microservice_name + "manager"
    # alternatively, search for port using port name "traffic", config dependent
    default_port = "5001"
    service_cluster_ip = "kubectl get service "
    service_cluster_ip += service_name
    service_cluster_ip += " -o=jsonpath='{.spec.clusterIP}'"
    # retry included in subroutine.command_error_check()
    service_cluster_ip = subroutine.command_error_check(service_cluster_ip)
    try:
        if service_cluster_ip is not None:
            service_cluster_ip = service_cluster_ip.strip("'")
            service_endpoint = service_cluster_ip + ":" + default_port
        else:
            print("Cannot get service endpoint for microservice ", microservice_name)
    except Exception as e:
        print("Error happened in constructing service endpoint")
        return None
    return service_endpoint

# connect to a microservice manager using the microservice's name
# input: str microservice name
# output: stub, channel of the connection
def connect_to_microservice_manager(microservice_name):
    current_retry = 0
    max_retry = 3
    while (current_retry < max_retry):
        try:
            # service_endpoint example: 10.1.1.1:5001
            service_endpoint = get_service_endpoint(microservice_name)
            if service_endpoint is None:
                raise Exception("Cannot get service endpoint")
            # proto_module_name = "Microservice_Managers_grpc.Adservice_Manager. adservice_manager_pb2_grpc"
            file_name = microservice_name + "_" + "manager_pb2_grpc"
            module_name = "Microservice_Managers_grpc." + microservice_name.capitalize() + "_Manager."
            proto_module_name = module_name + file_name
            # service_stub_name = AdserviceManagerStub
            service_stub_name = microservice_name.capitalize() + "ManagerStub"
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
            current_retry += 1
            if current_retry >= max_retry:
                print("Cannot make a connection to microservice manager ", microservice_name)
                return [microservice_name, None, None]
            else:
                print("Retry to connect to microservice manager ", microservice_name)




def connect_to_adaptive_resource_manager():
    current_retry = 0
    max_retry = 3
    while current_retry < max_retry:
        service_endpoint = get_service_endpoint("adaptiveresource")
        if service_endpoint is None:
            raise Exception("Cannot resolve service endpoint for Adaptive Resource Manager.")
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
            current_retry += 1
            if current_retry >= max_retry:
                print("Cannot make a connection to Adaptive Resource Manager.")
                return None, None
            else:
                print("Retrying to connect to Adaptive Resource Manager.")


def filter_microservice_data(response):
    has_error = False
    if len(response.microservice_name) == 0 or len(response.scaling_action) == 0:
        has_error = True
    if response.microservice_name == "''" or response.scaling_action == "''" or response.scaling_action == "ERROR":
        has_error = True
    if response.desired_replicas == 0 or response.current_replicas == 0 or response.cpu_request == 0 or response.max_replicas == 0 or response.cpu_percentage == 0:
        has_error = True
    if has_error == True:
        return [response.microservice_name, None, None, None, None, None, None]
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

# connect to microservice manager using microservice name
# and get the microservice resource data for scaling
# input: microservice name and stub of connection
# output: list of microservice resource data
def get_microservice_data(microservice_name, stub):
    module_name = "Microservice_Managers_grpc."+ microservice_name.capitalize() + "_Manager."
    file_name = microservice_name + "_" + "manager_pb2"
    proto_module_name = module_name + file_name

    current_retry = 0
    max_retry = 3
    while current_retry < max_retry:
        try:
            # import module named adservice_manager_pb2 for creating request
            grpc_module = importlib.import_module(proto_module_name)
            # get adservice_manager_pb2.MicroserviceDataRequest
            request_form = getattr(grpc_module, "MicroserviceDataRequest")
            # run adservice_manager_pb2.MicroserviceDataRequest() to make request
            request = request_form()
            # get response
            response_form = getattr(stub, "ExtractMicroserviceData")
            # response= stub.ExtractMicroserviceData(request)
            response = response_form(request, timeout=5) # set timeout on gRPC function call
            microservice_data = filter_microservice_data(response)
            if None in microservice_data:
                raise ValueError("Invalid response from microservice manager server ", microservice_name)
            return microservice_data
        except ValueError as ve:
            current_retry += 1
            if current_retry >= max_retry:
                return microservice_data
            else:
                print("Retrying")
        except grpc.RpcError as re:
            if re.code() == grpc.StatusCode.UNAVAILABLE:
                # if the microservice Manager is down, skip this microservice for this exchange round by removing connection
                # the connection will be retry before the next round
                print(f"Microservice Manager {microservice_name} is unavailable during data retrieval. ")
                remove_from_connection(microservice_name)
                return [microservice_name, None, None, None, None, None, None]

        except Exception as e:
            print("An error occurred in getting data from ", microservice_name)
            print(e)
            current_retry += 1
            if current_retry >= max_retry:
                print("Cannot get data from ", microservice_name)
                return [microservice_name, None, None, None, None, None, None]
            else:
                print("Retrying to get data from ", microservice_name)


def get_resource_exchange(microservice_data):
    global adaptive_stub
    global adaptive_channel
    proto_module_name = "Adaptive_Resource_Manager.adaptive_resource_manager_pb2"
    current_retry = 0
    max_retry = 3
    while current_retry < max_retry:
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
            response_form = getattr(adaptive_stub, "ResourceExchange")
            response = response_form(request, timeout=5) # setting timeout
            ARM_decision = []

            # filter values representing None from server
            # this error occurs when the microservice itself is not available
            for r in response.decision:
                ARM_decision.append([r.microservice_name, r.scaling_action, r.desired_replicas, r.max_replicas, r.cpu_request])

            return ARM_decision

        except grpc.RpcError as re:
            if re.code() == grpc.StatusCode.UNAVAILABLE:
                # if pod of Adaptive Resource Manager is unavailable then try to reconnect
                print("Adaptive Resource Manager is not available for resource exchange")
                current_retry += 1
                if current_retry >= max_retry:
                    print("Cannot get ARM from Adaptive Resource Manager because it's not available")
                    return None
                print("Retrying to reconnect and retry...")
                adaptive_channel.close()
                adaptive_stub, adaptive_channel = connect_to_adaptive_resource_manager()

        except Exception as e:
            print("Error happened during resource exchange")
            print(e)
            current_retry += 1
            if current_retry >= max_retry:
                print("Cannot get ARM decision from Adaptive Resource Manager.")
                return None
            else:
                print("Retrying to get ARM decision. ")



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
        if None in fut.result():
            continue
        connection_list.append(fut.result())
    executor.shutdown()
    return connection_list

def get_all(connection_list):
    microservice_data = []
    if len(connection_list) == 0:
        print("No connection made, cannot get microservice data.")
        return microservice_data
    executor = futures.ThreadPoolExecutor(max_workers=len(connection_list))
    future_list = []
    for connection in connection_list:
        future_list.append(executor.submit(get_microservice_data, connection[0], connection[2]))
    for fut in futures.as_completed(future_list):
        if None in fut.result():
            continue
        microservice_data.append(fut.result())
    executor.shutdown()
    return microservice_data

def remove_from_connection(microservice_name):
    global connection_list

    new_connection_list = []
    for i in range(len(connection_list)):
        if connection_list[i][0] != microservice_name:
            new_connection_list.append(connection_list[i])
        else:
            connection_list[i][1].close()
    connection_list = new_connection_list
    return

def maintain_connection_list(connection_list, microservice_list):
    unavailable_list = []
    new_connection_list = connection_list
    for microservice in microservice_list:
        appear = False
        for connection in connection_list:
            if connection[0] == microservice:
                appear = True
                break
        if appear == False:
            unavailable_list.append(microservice)

    for microservice in unavailable_list:
        new_connection = connect_to_microservice_manager(microservice)
        if None not in new_connection:
            new_connection_list.append(new_connection)
    return new_connection_list



def run(desired_time, microservice_list):

    ARM_saved_decision = []         # Adaptive Resource Manager scaling decision and updated maxR details of previous interation

    row_number = 2                    # for storing maximum replicas and desired replicas values in Knowledge Base

    start_time = time.time()


    global connection_list
    global adaptive_stub
    global adaptive_channel

    while (time.time() - start_time) < desired_time:

        Test_Time = time.time() - start_time

        # ********************************************************************** Running Microservice Managers Parallely in fully Decentralized manner ************************************************************************

        # establish connection with microservice manager and retrieve all microservice resource data
        microservices_data = get_all(connection_list)

        # keep trying to connect if no connection established
        if len(microservices_data) == 0:
            connection_list = maintain_connection_list(connection_list, microservice_list)
            continue


        # separate available and unavailable data
        available_microservices_data = []
        unavailable_microservices_data = []
        for data in microservices_data:
            # microservice not available
            if None in data:
                unavailable_microservices_data.append(data)
            else:
                available_microservices_data.append(data)
        available_microservice_name = []
        unavailable_microservice_name = []
        for data in available_microservices_data:
            available_microservice_name.append(data[0])
        for data in unavailable_microservices_data:
            unavailable_microservice_name.append(data[0])
        for microservice in microservice_list:
            # resolve naming, rediscart is used for connecting to the manager, but the actual name of the microservice is redis-cart
            if microservice == "rediscart":
                microservice = "redis-cart"
            # microservice manager not available, have been removed from connection list
            # need to write data for them as well to maintain the valid row_number
            if microservice not in available_microservice_name and microservice not in unavailable_microservice_name:
                unavailable_microservices_data.append([microservice, None, None, None, None, None, None])

        print("Available microservice data: ", available_microservices_data)
        print("Unavailable microservice data: ", unavailable_microservices_data)


        # Smart HPA continue with available microservices only
        microservices_data = available_microservices_data

        ARM_decision = []                 # ARM = Adaptive Resource Manager, ARM current scaling decision and maxR details will be saved here


        # **********************************************************************  Microservice Capacity Analyzer **********************************************************************

        for i in range(len(microservices_data)):
            if (microservices_data[i][2]>microservices_data[i][5]):        # desirsed replica count > max. replica count, for microservice i;  this represents Resource Constrained Situation

                for i in range(len(microservices_data)):
                    for j in range(len(ARM_saved_decision)):
                        if microservices_data[i][0] == ARM_saved_decision[j][0]:
                            microservices_data[i][5] = ARM_saved_decision[j][3]          # Changing SLA-defined maxR to the ResourceWise maxR of previous ARM decision for each microservice

                # ARM_decision = Adaptive_Resource_Manager(microservices_data)                     # Calling Adaptive Resource Manager
                ARM_decision = get_resource_exchange(microservices_data)

                if ARM_decision is None:
                    break

                ARM_saved_decision = ARM_decision

                break

        if ARM_decision is None:
            continue


        # write to data only when ARM_decision can be made, avoid writing then Adaptive Resource Manager gets unavailable
        for i in available_microservices_data:
            microservice_name, cpu_percentage, current_replicas, desired_replicas = i[0], i[6], i[3], i[2]
            write_content(f"./Knowledge_Base/{microservice_name}.txt", Test_Time, cpu_percentage, current_replicas, desired_replicas)

        # write to maintain value of row number across microservices
        for i in unavailable_microservices_data:
            microservice_name = i[0]
            write_content(f"./Knowledge_Base/{microservice_name}.txt", Test_Time, None, None, None)

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

        connection_list = maintain_connection_list(connection_list, microservice_list)

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

    connection_list = connect_all(microservice_list)
    adaptive_stub, adaptive_channel = connect_to_adaptive_resource_manager()

    run(600, microservice_list)
    health_server.join()
