from concurrent import futures
import grpc
import adservice_manager_pb2
import adservice_manager_pb2_grpc

def getSome():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = adservice_manager_pb2_grpc.AdserviceManagerStub(channel)
        response = stub.ExtractMicroserviceData(adservice_manager_pb2.MicroserviceDataRequest())
        print(response.microservice_name)
        print(response.scaling_action)
        print(response.desired_replicas)
        print(response.current_replicas)
        print(response.cpu_request)
        print(response.max_replicas)

if __name__ == '__main__':
    getSome()


