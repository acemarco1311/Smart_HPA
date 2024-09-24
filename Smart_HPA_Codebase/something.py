from concurrent import futures
import grpc
import grpc_test.adservice_manager_pb2
import grpc_test.adservice_manager_pb2_grpc

def getSome():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = grpc_test.adservice_manager_pb2_grpc.AdserviceManagerStub(channel)
        response = stub.ExtractMicroserviceData(grpc_test.adservice_manager_pb2.MicroserviceDataRequest())
        print(response.microservice_name)
        print(response.current_replicas)
        print(response.desired_replicas)
        print(response.cpu_request)
        print(response.scaling_decision)
        return response

if __name__ == '__main__':
    getSome()
