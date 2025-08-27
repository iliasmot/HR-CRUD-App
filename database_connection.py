# import mysql.connector
# from mysql.connector import Error
import pymysql

class Database:
    """
    Class that contains all the necessary functions for connecting to the database.
    """
    def __init__(self, host, user, password, database_name):
        self.host = host
        self.user = user
        self.password = password
        self.database_name = database_name
        self.connection = None

    def connect(self):
        """ establishing a connection with the database """
        try:
            # database connection
            self.connection = pymysql.connect(
            host = self.host,
            user = self.user,
            password = self.password,
            database = self.database_name,
            # ssl_disabled = True,  # Disable SSL temporarily
            port=3306
            )
            # check the connection
            if self.connection.open:
                print("Connected to database " + self.database_name + ".")

        except pymysql.Error as e:
            print(f"Error connecting to the database {self.database_name}: {str(e)}")

    def disconnect(self):
        """ Disconnect from the Database """
        if self.connection.is_connected():
            self.connection.close()
            print("Disconnected from " + self.database_name + ".")

    def get_connection(self):
        """ Return the current connection """
        if self.connection == None or not self.connection.open:
            self.connect()
        return self.connection