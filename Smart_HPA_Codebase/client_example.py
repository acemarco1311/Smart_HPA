from concurrent import futures
import grpc
import Microservice_Managers_grpc.Adservice_Manager.adservice_manager_pb2 as adservice_manager_pb2
import Microservice_Managers_grpc.Adservice_Manager.adservice_manager_pb2_grpc as adservice_manager_pb2_grpc

def getSome():
    with grpc.insecure_channel('localhost:50052') as channel:
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
    getSome()
