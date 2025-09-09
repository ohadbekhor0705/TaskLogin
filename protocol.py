import ipaddress
from datetime import datetime
import socket
import random
import logging

from protocol_27 import *
from protocol_DB import *

SERVER_HOST: str = "0.0.0.0"
CLIENT_HOST: str = "127.0.0.1"
PORT: int = 12345
BUFFER_SIZE: int = 1024
HEADER_LEN: int = 4
FORMAT: str = 'utf-8'

DISCONNECT_MSG: str = "EXIT"
STANDARD_CMD = ("TIME","NAME","RAND",DISCONNECT_MSG)

# prepare Log file
LOG_FILE = 'LOG.log'
logging.basicConfig(filename=LOG_FILE,level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')


def check_cmd(data) -> int:
    """Check if the command is defined in the protocol, protocol_27 or protocol_DB"""
    data = data.upper()
    if data in STANDARD_CMD:
        return 1
    if data in LONG_CMD:
        return 2
    if data in REG_LOGIN_CMD:
        return 3
    return -1


def create_request_msg(cmd: str,args: str) -> str:
    """Create a valid protocol message, will be sent by client, with length field"""
    if args is None:
        args = ""
    request: str = ""

    if check_cmd(cmd) == 1:  # commands "TIME"....
        request = cmd

    if check_cmd(cmd) == 2:  # command "SignIn"
        request += COMMAND_SEPARATOR + args
        if len(args) > 0:
            request += COMMAND_SEPARATOR + args
            # request += COMMAND_SEPARATOR + str(PARAMETER_SEPARATOR.join(args))

    if check_cmd(cmd) == 3:  # commands DB
        request = cmd + COMMAND_SEPARATOR + args

    return f"{len(request):04d}{request}"


def create_response_msg(cmd: str,args: list = []) -> str:
    """Create a valid protocol message, will be sent by server, with length field"""
    response = "Non-supported cmd"
    if cmd == "TIME":
        response = str(datetime.now())
    elif cmd == "NAME":
        response = socket.gethostname()
    elif cmd == "RAND":
        response = f"{random.randint(1,1000)}"
    elif cmd == DISCONNECT_MSG:
        response = "Exit request accepted"
    elif cmd in LONG_CMD:
        response = create_response_msg_27(cmd,args)
    elif cmd in REG_LOGIN_CMD:
        response = create_response_msg_DB(cmd,args)

    response = f"{len(response):04d}{response}"
    return response


def receive_msg(my_socket: socket.socket) -> tuple[bool, str]:
    
    """Extract message from protocol, without the length field
       If length field does not include a number, returns False, "Error" """
    str_header = my_socket.recv(HEADER_LEN).decode(FORMAT)
    length = int(str_header)
    if length > 0:
        buf = my_socket.recv(length).decode(FORMAT)
    else:
        return False, "Error"

    return True, buf


def get_cmd_and_args(buf: str) -> tuple[str, list[str]]:
    """Returns the command from buffer"""
    split_request: list[str] = buf.split(COMMAND_SEPARATOR)
    cmd = split_request[0]
    args = []
    if len(split_request) > 1:
        args: list[str] = split_request[1].split(PARAMETER_SEPARATOR)
    return cmd, args


def write_to_log(msg):
    logging.info(msg)
    print(msg)
