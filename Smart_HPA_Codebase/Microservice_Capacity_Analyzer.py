#*********************************************************** Importing Micorservice Managers and Adaptive Resource Manager ***********************************************************************

import time
import os
import subprocess
import multiprocessing
from multiprocessing import Pool
from functools import partial
from Microservice_Managers.adservice import *
from Microservice_Managers.frontend import *
from Microservice_Managers.checkoutservice import *
from Microservice_Managers.currencyservice import *
from Microservice_Managers.emailservice import *
from Microservice_Managers.paymentservice import *
from Microservice_Managers.productcatalogservice import *
from Microservice_Managers.cartservice import *
from Microservice_Managers.recommendationservice import *
from Microservice_Managers.shippingservice import *
from Microservice_Managers.rediscart import *
from Adaptive_Resource_Manager import *
from subroutine import *

# import grpc for kubernetes heartbeat
import grpc
from grpc_health.v1 import health
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc
from concurrent import futures
import threading




#***************************************************************************** Execute Component *****************************************************************************************

def Execute (microservice_name, desired_replicas):
    execute_command = f"kubectl scale deployment {microservice_name} --replicas={desired_replicas}"
    os.system(execute_command)
    return



def run_function(func):
    return func()


# *************************** Implement server for handling heartbeat ******************
def serve(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    # register HealthServicer
    health_pb2_grpc.add_HealthServicer_to_server(health.HealthServicer(), server)
    # set up port
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Heartbeat server started, listening on port " + port)
    server.wait_for_termination()


def filter_unavailable_microservice(microservices_data):
    available_microservice_data = []
    for i in range(len(microservices_data)):
        if None not in microservices_data[i]:
            available_microservice_data.append(microservices_data[i])
    return available_microservice_data

def get_unavailable_microservice(microservices_data):
    unavailable_microservices_data = []
    for i in range(len(microservices_data)):
        if None in microservices_data[i]:
            unavailable_microservices_data.append(microservices_data[i])
    return unavailable_microservices_data



def run(desire_time):

    ARM_saved_decision = [[]]         # Adaptive Resource Manager scaling decision and updated maxR details of previous interation

    row_number = 2                    # for storing maximum replicas and desired replicas values in Knowledge Base


    while (time.time() - start_time) < desired_time:

        Test_Time = time.time() - start_time

        # ********************************************************************** Running Microservice Managers Parallely in fully Decentralized manner ************************************************************************


        functions = [
            partial(frontend, Test_Time),
            partial(adservice, Test_Time),
            partial(cartservice, Test_Time),
            partial(currencyservice, Test_Time),
            partial(checkoutservice, Test_Time),
            partial(emailservice, Test_Time),
            partial(paymentservice, Test_Time),
            partial(shippingservice, Test_Time),
            partial(productcatalogservice, Test_Time),
            partial(recommendationservice, Test_Time),
            partial(rediscart, Test_Time)
        ]

        with multiprocessing.Pool(processes=len(functions)) as pool:
            microservices_data = pool.map(run_function, functions)              #Getting data from all microservice managers for Microservice Capacity Analyzer
        # filter unavailable services (containing None in data) before sending to Adaptive Resource Manager
        unavailable_microservices_data = get_unavailable_microservice(microservices_data)
        microservices_data = filter_unavailable_microservice(microservices_data)
        print(unavailable_microservices_data)
        print(microservices_data)


        ARM_decision = []                 # ARM = Adaptive Resource Manager, ARM current scaling decision and maxR details will be saved here



        # **********************************************************************  Microservice Capacity Analyzer **********************************************************************

        for i in range(len(microservices_data)):
            if (microservices_data[i][2]>microservices_data[i][5]):        # desirsed replica count > max. replica count, for microservice i;  this represents Resource Constrained Situation

                for i in range(len(microservices_data)):
                    for j in range(len(ARM_saved_decision)):
                        if microservices_data[i][0] == ARM_saved_decision[j][0]:
                            microservices_data[i][5] = ARM_saved_decision[j][3]          # Changing SLA-defined maxR to the ResourceWise maxR of previous ARM decision for each microservice

                ARM_decision = Adaptive_Resource_Manager(microservices_data)                     # Calling Adaptive Resource Manager
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
                #filename = microservices_data[i][0]
                #workbook = load_workbook(f'./Knowledge_Base/{filename}.xlsx')
                #sheet = workbook.active
                #sheet.cell(row=row_number, column=5, value=microservices_data[i][5])                            # storing maximum replicas
                #sheet.cell(row=row_number, column=6, value=microservices_data[i][1])                            # storing scaling decision
                #workbook.save(f'./Knowledge_Base/{filename}.xlsx')

                filename = microservices_data[i][0]
                filepath = f'./Knowledge_Base/{filename}.txt'
                max_reps = microservices_data[i][5]
                scaling_decision = microservices_data[i][1]
                add_content(filepath, row_number, max_reps, scaling_decision)

            # write to unavailable data as well
            for i in range(len(unavailable_microservices_data)):
                filename = unavailable_microservices_data[i][0]
                filepath = f'./Knowledge_Base/{filename}.txt'
                max_reps = unavailable_microservices_data[i][5]
                scaling_decision = unavailable_microservices_data[i][1]
                add_content(filepath, row_number, max_reps, scaling_decision)


                # ************************************************** Executing Scaling Decisions made by Microservice Managers **********************************************************************

                if microservices_data[i][1] != "no scale":
                    process = multiprocessing.Process(target=Execute, args=(microservices_data[i][0], microservices_data[i][2]))
                    processes.append(process)
                    process.start()
            for process in processes:            # Wait for all processes to finish
                process.join()


        # for Resource Constrained Situation, when Adaptive Resource Manager makes changes to max_Replicas and desired replicas

        else:
            for i in range(len(ARM_decision)):
                #filename = ARM_decision[i][0]
                #workbook = load_workbook(f'./Knowledge_Base/{filename}.xlsx')
                #sheet = workbook.active
                #sheet.cell(row=row_number, column=5, value=ARM_decision[i][3])                           #storing resource-wise updated maximum replicas in knowledge base
                #sheet.cell(row=row_number, column=6, value=ARM_decision[i][1])                           #storing resource-wise scaling decision in knowledge base
                #workbook.save(f'./Knowledge_Base/{filename}.xlsx')
                filename = ARM_decision[i][0]
                filepath = f'./Knowledge_Base/{filename}.txt'
                updated_max_reps = ARM_decision[i][3]
                updated_scaling_decision = ARM_decision[i][1]
                add_content(filepath, row_number, updated_max_reps, updated_scaling_decision)
            # write for unavailable microservices
            for i in range(len(unavailable_microservices_data)):
                filename = unavailable_microservices_data[i][0]
                filepath = f'./Knowledge_Base/{filename}.txt'
                max_reps = unavailable_microservices_data[i][5]
                scaling_action = unavailable_microservices_data[i][1]
                add_content(filepath, row_number, max_reps, scaling_action)



                # ************************************************** Executing ResourceWise Scaling Decisions made by Adaptive Resource Managers **********************************************************************

                if ARM_decision[i][1] != "no scale":
                    process = multiprocessing.Process(target=Execute, args=(ARM_decision[i][0], ARM_decision[i][2]))
                    processes.append(process)
                    process.start()
            for process in processes:            # Wait for all processes to finish
                process.join()

        row_number = row_number+1


        print ("ARM_decision", ARM_decision)



# ********************************************************************** Starting the Smart HPA operation ************************************************************************


#   Initializing Test Time

desired_time = 900 #Total_Test_Time (sec)
start_time = time.time()

if __name__ == '__main__':

    # run heartbeat server
    port = "8080"
    server_thread = threading.Thread(target=serve, args=[port,])
    server_thread.start()
    time.sleep(70)
    # run Smart HPA
    smart_hpa_thread = threading.Thread(target=run, args=[desired_time,])
    print("Smart HPA started, running for ", desired_time, " seconds.")
    smart_hpa_thread.start()
    server_thread.join()
    smart_hpa_thread.join()

