import string
import subprocess
import time
import lib_zstack_constants as constant
import socket
import os
import sys
from mutation import helpers


def convert_hex_str(hex_str):
    """
    Convert received hex string to corresponding format for Z-Stack Execution.

    """
    seed = ""
    if hex_str not in string.printable or hex_str in string.whitespace:
        seed = seed + str(map(ord, hex_str)[0]) + ' '
    else:
        seed = seed + hex_str + ' '
    return seed


def convert_seed(message):
    seed = ""
    for char in message:
        seed += convert_hex_str(char)
    seed = seed.lstrip(' ').rstrip(' ') + '\n'
    seed_file = open(constant.seed_file, 'w')
    seed_file.write(seed)
    seed_file.close()
    return


def execute_zstack(message):
    """
    Execute Z-Stack and record its execution result
    :return: the status of execution.
             If success, it will return 0. Otherwise, it will return status codes between 1 - 9.
             Except there is execution exception, it will return a special message.
    """
    command = [constant.cmd, '/C', constant.zstack_execution]
    output = ""
    status = ""
    try:
        z_result = open(constant.zstack_log_dir+"zstack_result.txt", 'a')
        z_result.write("\n************* {0} *************\nReceived message:{1}"
                       .format(helpers.get_time_stamp(), message))
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        if "ERROR" in e.output:
            call_stack_num = e.output.find("Call Stack:")
            memory_error_num = e.output.find("User error: Memory access error:")
            call_stack = e.output[call_stack_num: memory_error_num]
            status = "Process Failed!\n" + call_stack
        else:
            status = e.returncode
    finally:
        success_pattern = "Test zcl_ProcessMessageMSG:"
        index = output.find(success_pattern)
        if index != -1:
            code = output[index + len(success_pattern):index + len(success_pattern) + 4]
            status = str(int(code, 0))
        elif "ERROR" in output:
            call_stack_num = output.find("Call Stack:")
            memory_error_num = output.find("User error: Memory access error:")
            call_stack = output[call_stack_num:memory_error_num]
            status = "Process Failed!\n" + call_stack
        elif "CSpyBat terminating." in output:
            status = "0"
        else:
            status = "Server Error!\n"
        z_result.write(output)
        z_result.write("\n************* {} *************\n".format(helpers.get_time_stamp()))
        z_result.close()
    return status


def main():
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 34567
    connection.bind(("127.0.0.1", port))
    connection.listen(5)
    connection.settimeout(60)
    msg_count = 0
    try:
        if os.path.exists(constant.zstack_log_dir+"zstack_result.txt"):
            os.rename(constant.zstack_log_dir+"zstack_result.txt", constant.zstack_log_dir+"zstack_result_" + str(helpers.get_milli_time()) + ".txt")
        while True:
            (client, address) = connection.accept()
            client.setblocking(1)
            
            message = client.recv(constant.buffer_size)
            if message is not None:
                msg_count+=1
                print "Receive from address:",address
                print "Message ", msg_count, ":", repr(message)
                convert_seed(message)
                status = execute_zstack(repr(message))
                print "Z-Stack Execution Status:", status
                client.send(str(status))
            else:
                time.sleep(0.5)
    except KeyboardInterrupt:
        connection.close()
        sys.exit("User Interrupt!")
    except socket.error, msg:
        connection.close()
        sys.exit("Socket Error:%s" % msg)
    except socket.timeout, msg:
        connection.close()
        sys.exit("Socket Timeout:%s" % msg)

    return


# -------------------------------------------------------------- #
if __name__ == '__main__':
    main()






