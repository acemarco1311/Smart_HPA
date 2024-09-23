import grpc
import calculator_pb2
import calculator_pb2_grpc

def getAdd(num1, num2):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub= calculator_pb2_grpc.CalculatorStub(channel)
        response = stub.Add(calculator_pb2.AddRequest(num1=num1, num2=num2))
    return response.result


if __name__ == '__main__':
    num1 = 10
    num2 = 20
    print(getAdd(num1, num2))
