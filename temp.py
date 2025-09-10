import sqlite3
import json

def exist() -> bool:
    try:
        with sqlite3.connect("MyProject.db") as conn: # connecting to SQL
            cur = conn.cursor()

            # checking if user with username and password exist
            cur.execute("DELETE FROM users")
            conn.commit()
        return exist  #returning the result.
    except Exception as e: # handling errors.
        return False

exist()