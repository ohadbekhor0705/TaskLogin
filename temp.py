import sqlite3
import json

def exist(client_data) -> bool:
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
            client_data) is not None
        return exist  #returning the result.
    except Exception as e: # handling errors.
        return False
    
print(exist({"login": " ohad", "password": " 1223"}))
