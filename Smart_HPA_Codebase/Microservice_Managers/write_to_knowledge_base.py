def write_content(filename, test_time, cpu_usage, current_reps, desired_reps, max_reps, scaling_action):
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



