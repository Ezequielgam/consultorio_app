# database/connection.py
import mysql.connector
from mysql.connector import Error
import sys
import os

# Agregar la ruta del proyecto al path de Python
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

try:
    from config.config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
except ImportError:
    # Valores por defecto si no existe el archivo config
    DB_HOST = "localhost"
    DB_NAME = "consultorioMedico"
    DB_USER = "root"
    DB_PASSWORD = "root"


class DatabaseConnection:
    def __init__(self):
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                auth_plugin="mysql_native_password",  # Agregar esta línea
            )
            print("Conexión a la base de datos establecida correctamente")
            return self.connection
        except Error as e:
            print(f"Error conectando a MySQL: {e}")
            return None

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Conexión a la base de datos cerrada")
