import json
from cryptography.fernet import Fernet
import sqlite3

DB_NAME: str = "Users.db"
TABLE_USERS: str = "Users"

REG_LOGIN_CMD: tuple[str] = ("REG", "SIGNIN")


def create_response_msg_DB(cmd: str,args: list) -> str:
    """Creating response message from the DB

    Args:
        cmd (str): DB command
        args (list): Arguments

    Returns:
        str: DB response
    """

    json_data: dict = json.loads(args[0])
    if json_data["login"] == "" or json_data["password"] == "":
        return "LOGIN AND PASSWORD MUSTN'T BE EMPTY!"
    if cmd == "REG":
        if username_doesnt_exist(json_data):
            save_client_data(json_data)
            return "USER REGISTERED"
        else:
            return "THIS USERNAME IS ALREADY TAKEN"
    if cmd == "SIGNIN":
        return f"Welcome back {json_data["login"]}!" if exist(json_data) else "USERNAME OR PASSWORD ARE INVALID"
    return ""
    


def generate_key() -> bytes:
    return Fernet.generate_key()

def username_doesnt_exist(client_data: dict) -> bool:
    try:
        with sqlite3.connect("MyProject.db") as conn: # connecting to SQL
            cur = conn.cursor()

            # checking if user with username and password exist
            exist: bool = cur.execute( 
            "SELECT * FROM users WHERE login = :login AND password", 
            client_data).fetchone() is  None
        return exist  #returning the result.
    except Exception as e: # handling errors.
        return False
def save_client_data(client_data: json) -> None:
    # Here should be code to save data to DB
    try:
        with sqlite3.connect("MyProject.db") as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO  users (login, password) VALUES (?,?)",(client_data["login"],client_data["password"]))
            print("Client data saved:", client_data)
    except Exception as e:
        print(f"Couldn't save To DataBase {client_data}: {e}")
    
def exist(client_data: dict) -> bool:
    """this method handle user login via SQL (sqlite3)
    Args:
        client_data (json): client login and password data.
    Returns:
        bool: If user exists in the database.
    """
    try:
        with sqlite3.connect("MyProject.db") as conn: # connecting to SQL
            cur = conn.cursor()

            # checking if user with username and password exist
            exist: bool = cur.execute( 
            "SELECT * FROM users WHERE login = :login AND password = :password", 
            client_data).fetchone() is not None
        return exist  #returning the result.
    except Exception as e: # handling errors.
        return False

def handle_registration(client_socket) -> str:
    data = client_socket.recv(1024).decode()
    registration_data = json.loads(data)

    login = registration_data.get('login')
    password = registration_data.get('password')

    if is_valid(login, password):
        encryption_key = generate_key().decode()
        client_data = {'login': login, 'encryption_key': encryption_key}
        save_client_data(client_data)

        response = {'success': True, 'encryption_key': encryption_key}
    else:
        response = {'success': False, 'error': 'Invalid credentials'}

    client_socket.send(json.dumps(response).encode())


def is_valid(login, password) -> bool:
    return len(login) > 0 and len(password) > 0





