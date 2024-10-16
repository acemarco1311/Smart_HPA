import subprocess
import time

def write_content(filename, test_time, cpu_usage, current_reps, desired_reps):
    file = open(filename, 'a')
    content = str(test_time) + ',' + str(cpu_usage) + ',' + str(current_reps)+ ',' + str(desired_reps) + '\n'
    file.write(content)
    file.close()

def add_content(filename, row_number, max_reps, scaling_action):
    with open(filename, 'r') as file:
        data = file.readlines()

    row_number = row_number - 1
    original_line = data[row_number]
    original_line = original_line.rstrip('\n')

    new_line = original_line + ',' + str(max_reps) + ',' + str(scaling_action) + '\n'

    data[row_number] = new_line

    with open(filename, 'w') as file:
        file.writelines(data)

def command_error_check(command):
    # set retry
    total_retry = 5
    current_retry = 0
    # set timeout on kubectl command
    # command += " --request-timeout 5s"

    # output from kubectl top pod for unavailable microservice, this might not raise an error (at least on experimental local machine Window)
    kubectl_top_pod_error = "No resources found in default namespace.\n"
    # output when the microservice is still initializing, this might not raise an error
    microservice_initializing_error = "''"

    while current_retry < total_retry:
        command_output = ""
        try:
            command_output = subprocess.check_output(command.split(), stderr=subprocess.STDOUT, timeout=5).decode('utf-8')
            # handle case when kubectl top pods doesn't raise an error even if the microservice cannot be found

            # received "No resources found in default namespace." from top pod command
            if isinstance(command_output, str) == True and command_output == kubectl_top_pod_error:
                print(f"Command '{command}' failed, microservice resources cannot be found, retrying...")
                command_output = None
            # received "''"
            elif isinstance(command_output, str) == True and command_output == microservice_initializing_error:
                print(f"Command '{command}' failed, reiceived an empty output, the target microservice might being initialized, retrying...")
                print("Waiting for microservice before retrying.")
                time.sleep(3)
                command_output = None
            # skeleton for handling unexpected cases
            elif isinstance(command_output, str) == True and len(command_output) == 0:
                print("Received an empty output, retrying...")
                command_output = None
            else:
                print(f"Command '{command}' succeeded.")
        except subprocess.CalledProcessError as err:
            error_message = str(err.stdout)
            # extract error type
            error_type = ""
            start_index = error_message.find('(')
            end_index = error_message.find(')')
            # check if start and end index is valid (ie both start and end != -1)
            valid_index = (start_index != -1) and (end_index != -1) and (start_index != end_index)
            # handling error message format: "Error from server (<error_type>) ..."
            if valid_index == True:
                error_type = error_message[start_index+1:end_index]
                if error_type == "NotFound":
                    print(f"Command '{command}' failed, microservice cannot be found, retrying...")
                elif error_type == "Timeout":
                    print(f"Command '{command}' failed, exceeded timeout, retrying...")
                # for other errors with the same error message format
                else:
                    print(f"Command '{command}' failed with error: ", error_message)
            # for other error message formats such as: "error: ..."
            else:
                    print(f"Command '{command}' failed with error: ", error_message)
            command_output = None
        # use Timeout handling by subprocess module, as localhost has a problem with
        # kubectl parameter --request-timeout
        except subprocess.TimeoutExpired as err_timeout:
            print(f"Command '{command}' failed, exceeded timeout, retrying...")
            command_output = None
        finally:
            current_retry += 1
            # handle error
            if command_output is None and current_retry < total_retry:
                continue
            # handle empty output from initializing microservices
            elif command_output is None and current_retry >= total_retry:
                print(f"Command '{command}' cannot be completed after retrying.")
            return command_output
