#!/usr/bin/env python3

from os import getpid
import sqlite3
from typing import Optional

class Database:
    def __init__(self, db_name: str) -> None:
        """Initialize a new or existing database.
        
        Args:
            db_name (str): The name of the database file.
        """
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.pid = getpid()

    def __enter__(self) -> 'Database':
        """Open the database connection with the context manager."""
        try:
            self.conn = sqlite3.connect(self.db_name)
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
        self.conn.isolation_level = None
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Close the database connection with the context manager.
        
        Args:
            exc_type (type): The type of the exception.
            exc_val (Exception): The exception instance raised.
            exc_tb (traceback): The traceback object.
            
        Raises:
            sqlite3.Error: If there is an error committing changes to the database.
            
        Example:
            with Database('my_database.db') as db:
                db.create_table('my_table', {'id': 'INTEGER PRIMARY KEY', 'name': 'TEXT'})
                db.execute('INSERT INTO my_table (name) VALUES (?)', ('test',))
                print(db.fetchall())
        """
        try:
            if exc_type is not None:
                self.conn.rollback()
            else:
                self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error committing changes to database: {e}")
        finally:
            self.conn.close()
            if exc_type is not None:
                os.kill(self.pid, SIGKILL)


    def create_table(self, table_name: str, fields: dict) -> None:
        """Create a new table with the given name and fields.
        
        Args:
            table_name (str): The name of the table.
            fields (dict): The fields of the table, with the field name as the key and the field type as the value.
        """
        with self:
            fields_str = ', '.join(f'{name} {field}' for name, field in fields.items())
            sql = f'CREATE TABLE IF NOT EXISTS {table_name} ({fields_str})'
            self.cursor.execute(sql)

    def execute(self, sql: str, params: tuple = ()) -> None:
        """Execute a SQL command, with parameters to prevent SQL injection.
        
        Args:
            sql (str): The SQL command to execute.
            params (tuple, optional): The parameters to pass to the SQL command. Defaults to ().
        """
        self.cursor.execute(sql, params)
        self.conn.commit()

    def fetchall(self) -> list:
        """Fetch all rows from the last executed SQL command.
        
        Returns:
            list: The rows from the last executed SQL command.
        """
        return self.cursor.fetchall()

    def fetchone(self) -> dict:
        """Fetch one row from the last executed SQL command.
        
        Returns:
            dict: The row from the last executed SQL command.
        """
        return self.cursor.fetchone()
    
class SshServerTable:
    def __init__(self, db_name: str) -> None:
        self.__db = Database(db_name)
        self.__db.create_table('ssh_servers', {'id': 'INTEGER PRIMARY KEY',
                                             'hostname': 'TEXT NOT NULL',
                                             'port': 'INTEGER NOT NULL',
                                             'username': 'TEXT NOT NULL',
                                             'password': 'TEXT',
                                             'private_key_path': 'TEXT'})
        
    def insert_ssh_server(self, hostname: str, port: int, username: str, password: Optional[str] = None, private_key_path: Optional[str] = None) -> int:
        """Insert a new SSH server into the table
        
        Args:
            hostname (str): The hostname of the server.
            port (int): The port number of the server.
            username (str): The username to use when connecting to the server.
            password (str, optional): The password to use when connecting to the server. Defaults to None.
            private_key_path (str, optional): The path to the private key to use when connecting to the server. Defaults to None.
        
        Returns:
            int: The row ID of the new SSH server.
        """
        
        with self.__db as db:
            sql = 'INSERT INTO ssh_servers (hostname, port, username, password, private_key_path) VALUES (?, ?, ?, ?, ?)'
            params = (hostname, port, username, password, private_key_path)
            db.execute(sql, params)
            return db.cursor.lastrowid
        
    def update_ssh_server(self, server_id: int, **fields) -> None:
        """Update an existing SSH server in the table
        
        Args:
            server_id (int): The ID of the server to update.
            **fields: The fields to update, with the field name as the key and the new value as the value.
            
        Raises:
            ValueError: If no fields are provided to update.
            
        Example:
            update_ssh_server(1, hostname='example.com', port=22, username='user', password='pass')
        """
        
        if not fields:
            raise ValueError('No fields provided to update')
        if 'id' in fields:
            fields.pop('id')

        with self.__db as db:
            update_fields: str = ', '.join(f'{name} = ?' for name in fields.keys())
            values: tuple = tuple(fields.values()) + (server_id,)
            sql: str = f'UPDATE ssh_servers SET {update_fields} WHERE id = ?'
            db.execute(sql, values)
        
    def delete_ssh_server(self, server_id: int) -> None:
        """Delete an SSH server from the table
        
        Args:
            server_id (int): The ID of the server to delete
            
        Raises:
            sqlite3.IntegrityError: If the server ID does not exist in the table.
            
        Example:
            delete_ssh_server(1)
        """
        try:
            with self.__db as db:
                sql = 'DELETE FROM ssh_servers WHERE id = ?'
                db.execute(sql, (server_id,))
        except sqlite3.IntegrityError as e:
            raise sqlite3.IntegrityError(f"No SSH server with ID {server_id} exists")
            print(f"Error deleting SSH server: {e}")
   
    def select_ssh_servers(self, server_id: Optional[int] = None) -> list:
        """Select SSH servers from the table
        
        Args:
            server_id (int, optional): The ID of the server to select. Defaults to None.
            
        Returns:
            list: The selected SSH servers.
        
        Example:
            select_ssh_servers() -> select all SSH servers
            select_ssh_servers(1) -> select SSH server with ID 1
        """
        if server_id is None:
            with self.__db as db:
                sql = 'SELECT * FROM ssh_servers'
                db.execute(sql)
                return db.fetchall()
        else:
            with self.__db as db:
                sql = 'SELECT * FROM ssh_servers WHERE id = ?'
                db.execute(sql, (server_id,))
                return db.fetchone()