import subprocess
import shutil
import os
import glob
import logging
import socket
from PIL import ImageGrab
import webbrowser
import pyautogui


LONG_CMD = ("DIR", "DELETE", "COPY", "EXECUTE", "TAKE_SCREENSHOT")

COMMAND_SEPARATOR = '>'
PARAMETER_SEPARATOR = '<'

FORMAT: str = 'utf-8'

# REG>LOGIN<PASSWORD
def create_response_msg_27(cmd: str, args: list = []) -> str:
    response = ''
    if cmd == "DIR":
        response = get_dir_file_list(args[0])
    elif cmd == "DELETE":
        response = delete_file(args[0])
    elif cmd == "COPY":
        response = copy_file(args)
    elif cmd == "EXECUTE":
        response = execute(args[0])
    elif cmd == "TAKE_SCREENSHOT":
        response = take_screenshot(args[0])

    response = f"{len(response):04d}{response}"
    return response


def get_dir_file_list(args: list) -> str:
    curr_dir = str(args) + "/" + "*.*"
    dir_list = glob.glob(curr_dir)
    response = str(','.join(dir_list))

    logging.info(f"[Protocol_27] Prepare directory file list {curr_dir}")
    return response


def delete_file(file_path: str) -> str:
    res = ''
    if os.path.exists(file_path):
        os.remove(file_path)
        res = f'File {file_path} was successfully removed'
    else:
        res = f'File {file_path} was not removed'

    logging.info(f"[Protocol_27] {res}")
    return res


def copy_file(args: list) -> str:
    res = ''
    if os.path.exists(args[0]):
        shutil.copy(args[0], args[1])
        res = f'File {args[0]} was successfully copied to directory {args[1]}'
    else:
        res = f'File {args[0]} was not copied to {args[1]}'

    logging.info(f"[Protocol_27] {res}")
    return res


def execute(file_path: str) -> str:
    res = subprocess.call(file_path)
    if res == 0:
        response = file_path + " - successfully executed"
    else:
        response = file_path + " - was not executed"

    logging.info('[Protocol_27] EXECUTE command for {0} with response {1}'.format(file_path, res))
    return response


def take_screenshot(img_name: str) -> str:
    """
    takes a screenshot, saves it to a file
    :param img_name: the image file name
    :return: response
    """

    image = pyautogui.screenshot(img_name)

    # Use with context manger to handle file open
    # with open(img_name, 'rb') as img_file:
    #     img_data = img_file.read()

    response = ''
    bres = webbrowser.open(img_name)
    if bres:
        response = "Take screenshot - done"
    else:
        response = "Take screenshot - was not done"

    logging.info(f"[Protocol_27] {response}")
    return response


def send_big_image(my_socket: socket, file_name: str, chunk_size=1024) -> str:
    txt = ''
    try:
        with open(file_name, "rb") as file:
            while True:
                image_data = file.read(chunk_size)
                my_socket.send(f"{len(image_data):04d}".encode(FORMAT))
                my_socket.send(image_data)
                if not image_data:
                    break  # reached end of file
            txt = f'Send photo {file_name} - done'
    except FileNotFoundError:
        txt = f'Send photo {file_name} - failed file not found'

    logging.info(f"[Protocol_27] {txt}")
    return txt


def receive_big_image(my_socket: socket, file_name: str, chunk_size=1024):
    my_socket.settimeout(1)
    try:
        with open(file_name, "wb") as file:
            while True:
                length = int(my_socket.recv(4))
                if not length:
                    break  # reached end of file
                data = my_socket.recv(length)
                file.write(data)
    except Exception as e:
        logging.info(f"[Protocol_27] failed to receive image - {e}")
