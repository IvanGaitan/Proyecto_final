import mysql.connector 
from flask import Flask
import base64

# Configuración de la conexión a la base de datos
conexion = mysql.connector.connect(   
  host="localhost",
  user="root",
  password="",
  database="bio_soacha" # nombre de la base de datos
) 

# Crear una instancia de Flask
app = Flask(__name__)



# Función para verificar la conexión a la base de datos
def verificar_conexion(): 
    try: 
        # Crear un cursor para realizar una operación simple de consulta y verificar la conexión
        cursor = conexion.cursor() 
        cursor.execute("SELECT Nombre FROM usuarios")  # Corregí la consulta
        rows = cursor.fetchall()  # Leer todos los resultados de la consulta
        cursor.close()
        return True
    except Exception as e:
        print("Error al verificar la conexión a la base de datos:", e) 
        return False

# Configurar b64encode para Jinja2
@app.template_filter('b64encode')
def b64encode_filter(data):
    return base64.b64encode(data).decode('utf-8')

if __name__ == '__main__':
    # Dejar de última para conexión
    if verificar_conexion(): 
        print("La conexión a la base de datos se estableció correctamente.") 
        app.run(debug=True)
    else: 
        print("Error: No se pudo establecer la conexión a la base de datos.")
