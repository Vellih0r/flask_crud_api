import psycopg2
from db import db_config
from typing import Union
import psycopg2.extras
from functools import wraps

def open_db() -> object :
    """Connect to database using info from config"""
    conn=psycopg2.connect(dbname=db_config.dbname,
    user=db_config.user,
    password=db_config.password,
    host=db_config.host,
    port=db_config.port)
    conn.autocommit = True
    return conn

def exists(tb: str) -> bool:
    '''Checks if the table exists'''
    with open_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = %s
                );
            """, (tb,))
            exists = cursor.fetchone()[0]
            return exists 

def validate_table(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        tb = kwargs.get('tb') if 'tb' in kwargs else (args[0] if len(args) > 0 else None)
        if tb and exists(tb) and tb in ['books', 'ratings']:
            return func(*args, **kwargs)
        else:
            print(f"[validate_table] Invalid or non-existent table: {tb}")
            return False
    return wrapper

def create(tb: str) -> bool:
    """Create books or ratings table"""
    if exists(tb):
        return False
    with open_db() as conn:
        with conn.cursor() as cursor:
            if tb == 'books':
                cursor.execute(f"CREATE TABLE books (id int PRIMARY KEY, title varchar(20), rating decimal(2,1), price decimal(4,2))")
                return True
            if tb == 'ratings':
                cursor.execute(f"CREATE TABLE ratings (user varchar(20) PRIMARY KEY, rating int, b_title varchar(20) REFERENCES (books.title))")
                return True

def del_table(tb: str) -> bool:
    """Removes table by name"""
    if not exists(tb):
        return False
    if tb in ['books', 'ratings']:
        try:
            with open_db() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"DROP TABLE {tb}")
                    return True
        except Exception as e:
            print(f"Exception {e}")
            return False
    return False

@validate_table
def read(tb: str) -> Union[bool, list]:
    """Reads all data from table by name"""
    with open_db() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(f"SELECT * FROM {tb}")
            tmp = cursor.fetchall()       
            result = [dict(d) for d in tmp]
            return result
    
@validate_table
def read_one(tb: str, id: int) -> Union[str, tuple, bool]:
    """Returns one row by id from table by name"""
    with open_db() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(f"SELECT * FROM {tb} WHERE id = %s", (id,))
            result = cursor.fetchone()
            if result is not None:
                return dict(result)
            else:
                return {}

def insert(tb: str, data: Union[dict, list], id: int = 0) -> bool:
    """Insert json data into table"""
    try:
        with open_db() as conn:
            with conn.cursor() as cursor:
                if isinstance(data, dict):
                    cursor.execute(f"INSERT INTO {tb} values (%s, %s, %s)", (id, data['title'], data['rating'],))
                    return True
                if isinstance(data, list):
                    values = [(d['id'], d['title'], d['rating']) for d in data]
                    cursor.executemany(f"INSERT INTO {tb} values (%s, %s, %s)", values)
                    return True
    except Exception as e:
        print(f"Exception {e}")
        return False

@validate_table
def update_db(tb: str, data: Union[dict, list], id: int) -> bool:
    """Updates row[s] by id"""
    try:
        with open_db() as conn:
            with conn.cursor() as cursor:
                if isinstance(data, dict):
                    cursor.execute(f"UPDATE {tb} SET title = %s, rating = %s WHERE id = %s", (data['title'], data['rating'], id,))
                    return True
                if isinstance(data, list):
                    values = [(d['title'], d['rating'], d['id']) for d in data]
                    cursor.executemany(f"UPDATE {tb} SET title = %s, rating = %s WHERE id = %s", values)
                    return True
    except Exception as e:
        print(f"Exception {e}")
        return False

@validate_table
def del_one(tb: str, id : int) -> bool:
    """Deletes row[s] form table"""
    try:
        with open_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"DELETE FROM {tb} WHERE id = %s", (id,))
                return True
    except Exception as e:
        print(f"Exception {e}")
        return False