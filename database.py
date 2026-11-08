import mysql.connector
from mysql.connector import Error

class GestorBD:
    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super(GestorBD, cls).__new__(cls)
            cls._instancia.conexion = None
            cls._instancia.conectar()
        return cls._instancia

    def conectar(self):
        """Establece la conexión única con XAMPP (MySQL)"""
        try:
            if not self.conexion or not self.conexion.is_connected():
                self.conexion = mysql.connector.connect(
                    host="localhost",
                    database="inces",  # Nombre de tu base de datos local
                    user="root",
                    password=""        # Por defecto en XAMPP va vacío
                )
        except Error as e:
            print(f"Error al conectar a la base de datos: {e}")

    def obtener_conexion(self):
        """Devuelve la conexión activa, reconectando si se interrumpió"""
        try:
            if self.conexion is None or not self.conexion.is_connected():
                self.conectar()
        except Error:
            self.conectar()
        return self.conexion

    def cerrar(self):
        """Cierra la conexión global"""
        if self.conexion and self.conexion.is_connected():
            self.conexion.close()