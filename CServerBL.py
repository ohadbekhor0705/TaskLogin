import threading
from protocol import *
import sqlite3

class CServerBL:

    def __init__(self,host: str,port: str) -> None:

        # Open the log file in write mode, which truncates the file to zero length
        with open(LOG_FILE,'w'):
            pass  # This block is empty intentionally

        self._host = host
        self._port = port
        self._server_socket = None
        self._is_srv_running = True
        self._client_handlers = []
        with sqlite3.connect("MyProject.db") as conn:
            cur = conn.cursor()
            cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                login CHAR(255),
                password CHAR(255)
            )
            """
            )
            conn.commit()

    def stop_server(self) -> None:
        try:
            self._is_srv_running = False
            # Close server socket
            if self._server_socket is not None:
                self._server_socket.close()
                self._server_socket = None    

            if len(self._client_handlers) > 0:
                # Waiting to close all opened threads
                for client_thread in self._client_handlers:
                    client_thread.join()
                write_to_log(f"[SERVER_BL] All Client threads are closed")

        except Exception as e:
            write_to_log("[SERVER_BL] Exception in Stop_Server fn : {}".format(e))

    def start_server(self) -> None:
        try:
            self._server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self._server_socket.bind((self._host,self._port))
            self._server_socket.listen(5)
            write_to_log(f"[SERVER_BL] listening...")

            while self._is_srv_running and self._server_socket is not None:
                # Accept socket request for connection
                client_socket,address = self._server_socket.accept()
                write_to_log(f"[SERVER_BL] Client connected {client_socket}{address} ")

                # Start Thread
                cl_handler: CClientHandler = CClientHandler(client_socket,address)
                cl_handler.start()
                self._client_handlers.append(cl_handler)
                write_to_log(f"[SERVER_BL] ACTIVE CONNECTION {threading.active_count() - 1}")

        except Exception as e:
            write_to_log("[SERVER_BL] Exception in start_server fn : {}".format(e))
        finally:
            write_to_log(f"[SERVER_BL] Server thread is DONE")


class CClientHandler(threading.Thread):
    _client_socket = None
    _address = None

    def __init__(self,client_socket,address) -> None:
        super().__init__()

        self._client_socket = client_socket
        self._address = address
    def run(self) -> None:
        # This code run in separate thread for every client
        connected = True
        while connected:
            # 1. Get message from the socket and check it
            valid_msg, buf = receive_msg(self._client_socket)
            if valid_msg:
                cmd, args = get_cmd_and_args(buf)
                write_to_log(f"[SERVER_BL] received from {self._address}] - cmd: {cmd}, args: {args}")
                # 3. If valid command - create response
                if check_cmd(cmd) == 1:
                    response: str = create_response_msg(cmd)
                elif check_cmd(cmd) == 2:
                    response = create_response_msg_27(cmd, args)
                elif check_cmd(cmd) == 3:
                    response = create_response_msg_DB(cmd,args)
                else:
                    response = "Non-supported cmd"
                    response = f"{len(response):04d}{response}"

                # 5. Save to log
                write_to_log("[SERVER_BL] send - " + response)
                # 6. Send response to the client
                self._client_socket.send(response.encode(FORMAT))

                # Handle DISCONNECT command
                if cmd == DISCONNECT_MSG:
                    connected = False

            else:  # if the msg is not valid
                response = buf
                response = f"{len(response):04d}{response}"
                # 5. Save to log
                write_to_log("[SERVER_BL] send - " + response)
                # 6. Send response to the client
                self._client_socket.send(response.encode(FORMAT))

        self._client_socket.close()
        write_to_log(f"[SERVER_BL] Thread closed for : {self._address} ")


if __name__ == "__main__":
    server = CServerBL(SERVER_HOST,PORT)
    server.start_server()
