from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import io
import base64
import os
from BD import conexion, verificar_conexion
from routes.create import create_routes
from routes.read import read_routes
from routes.update import update_routes
from routes.delete import delete_routes
from routes.charts import charts_routes  # Importar el nuevo blueprint

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

# Registrar los blueprints
app.register_blueprint(create_routes)
app.register_blueprint(read_routes)
app.register_blueprint(update_routes)
app.register_blueprint(delete_routes)
app.register_blueprint(charts_routes)

# Crear la carpeta 'data' si no existe
if not os.path.exists('data'):
    os.makedirs('data')

csv_file = 'data/usuarios.csv'
excel_file = 'data/usuarios.xlsx'

# Asegurarse de que el archivo CSV tenga los encabezados adecuados
if not os.path.isfile(csv_file):
    df = pd.DataFrame(columns=['Nombre', 'Apellidos', 'Cedula', 'Edad', 'Email', 'Telefono', 'Mensaje'])
    df.to_csv(csv_file, index=False)
    df.to_excel(excel_file, index=False)

@app.route('/')
def base():
    return render_template('base.html')

@app.route('/soacha')
def soacha():
    return render_template('soacha.html')

@app.route('/galeria')
def galeria():
    return render_template('galeria.html')

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    df = pd.read_csv(csv_file)

    if request.method == 'POST':
        if 'eliminar' in request.form:
            id_eliminar = int(request.form['id_eliminar'])
            if 0 <= id_eliminar < len(df):
                df = df.drop(df.index[id_eliminar])
                df.to_csv(csv_file, index=False)
                df.to_excel(excel_file, index=False)
        elif 'buscar' in request.form:
            busqueda = request.form['busqueda'].lower()
            df = pd.read_csv(csv_file)
            df = df[df.apply(lambda row: busqueda in row.astype(str).str.lower().to_string(), axis=1)]
        else:
            nombre = request.form['nombre']
            apellidos = request.form['apellidos']
            cedula = int(request.form['num_identificacion'])
            edad = int(request.form['edad'])
            email = request.form['email']
            telefono = request.form['telefono']
            mensaje = request.form['mensaje']

            nuevo_usuario = pd.DataFrame([[nombre, apellidos, cedula, edad, email, telefono, mensaje]], 
                                         columns=['Nombre', 'Apellidos', 'Cedula', 'Edad', 'Email', 'Telefono', 'Mensaje'])
            df = pd.concat([df, nuevo_usuario], ignore_index=True)
            df.to_csv(csv_file, index=False)
            df.to_excel(excel_file, index=False)

            # Guardar en MySQL
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO usuarios (Nombre, Apellidos, Cedula, Edad, Email, Telefono, Mensaje)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (nombre, apellidos, cedula, edad, email, telefono, mensaje))
            conexion.commit()
            cursor.close()

        return redirect(url_for('contacto'))

    return render_template('contacto.html', df=df)

@app.route('/visualizacion')
def visualizacion():
    try:
        df = pd.read_csv('data/usuarios.csv')

        # Gráfico de distribución de edades
        plt.figure(figsize=(10, 6))
        sns.histplot(df['Edad'], bins=10, kde=True)
        plt.title('Distribución de Edades')
        plt.xlabel('Edad')
        plt.ylabel('Frecuencia')
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url1 = base64.b64encode(img.getvalue()).decode()

        # Gráfico de categorización de edades
        plt.figure(figsize=(10, 6))
        categorias = ['Menor', 'Mayor', 'Adulto Mayor']
        conteos = [df[df['Edad'] < 18].shape[0], df[(df['Edad'] >= 18) & (df['Edad'] < 60)].shape[0], df[df['Edad'] >= 60].shape[0]]
        plt.bar(categorias, conteos)
        plt.title('Categorización de Edades')
        plt.xlabel('Categoría de Edad')
        plt.ylabel('Cantidad')
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url2 = base64.b64encode(img.getvalue()).decode()

        return render_template('visualizacion.html', tables=[df.to_html(classes='data', index=False)], plot_url1=plot_url1, plot_url2=plot_url2)
    
    except Exception as e:
        return f"Error al procesar los datos para visualización: {str(e)}"

@app.route('/limpiar', methods=['POST'])
def limpiar():
    df = pd.DataFrame(columns=['Nombre', 'Apellidos', 'Cedula', 'Edad', 'Email', 'Telefono', 'Mensaje'])
    df.to_csv(csv_file, index=False)
    df.to_excel(excel_file, index=False)
    return redirect(url_for('visualizacion'))

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        cedula = int(request.form['num_identificacion'])
        edad = int(request.form['edad'])
        email = request.form['email']
        telefono = request.form['telefono']
        mensaje = request.form['mensaje']

        nuevo_usuario = pd.DataFrame([[nombre, apellidos, cedula, edad, email, telefono, mensaje]], 
                                     columns=['Nombre', 'Apellidos', 'Cedula', 'Edad', 'Email', 'Telefono', 'Mensaje'])
        df = pd.read_csv(csv_file)
        df = pd.concat([df, nuevo_usuario], ignore_index=True)
        df.to_csv(csv_file, index=False)
        df.to_excel(excel_file, index=False)

        # Guardar en MySQL
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO usuarios (Nombre, Apellidos, Cedula, Edad, Email, Telefono, Mensaje)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (nombre, apellidos, cedula, edad, email, telefono, mensaje))
        conexion.commit()
        cursor.close()

        return redirect(url_for('visualizacion'))
    
    return render_template('agregar.html')

@app.route('/exportar', methods=['GET'])
def exportar():
    try:
        # Ruta del archivo CSV
        csv_file = 'data/usuarios.csv'

        # Verificar si el archivo existe
        if os.path.exists(csv_file):
            return send_file(csv_file, as_attachment=True, attachment_filename='usuarios.csv')
        else:
            return "El archivo CSV no existe."
    except Exception as e:
        return str(e)

@app.route('/importar', methods=['POST'])
def importar():
    file = request.files['file']
    if file and file.filename.endswith('.csv'):
        df = pd.read_csv(file)
        df.to_csv(csv_file, index=False)
        df.to_excel(excel_file, index=False)
    elif file and file.filename.endswith('.xlsx'):
        df = pd.read_excel(file)
        df.to_csv(csv_file, index=False)
        df.to_excel(excel_file, index=False)
    return redirect(url_for('visualizacion'))

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    df = pd.read_csv(csv_file)

    if request.method == 'POST':
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        cedula = int(request.form['num_identificacion'])
        edad = int(request.form['edad'])
        email = request.form['email']
        telefono = request.form['telefono']
        mensaje = request.form['mensaje']

        df.loc[id] = [nombre, apellidos, cedula, edad, email, telefono, mensaje]
        df.to_csv(csv_file, index=False)
        df.to_excel(excel_file, index=False)

        # Actualizar en MySQL
        cursor = conexion.cursor()
        cursor.execute("""
            UPDATE usuarios
            SET Nombre = %s, Apellidos = %s, Cedula = %s, Edad = %s, Email = %s, Telefono = %s, Mensaje = %s
            WHERE id = %s
        """, (nombre, apellidos, cedula, edad, email, telefono, mensaje, id + 1))  # Asumiendo que id de CSV y MySQL están sincronizados
        conexion.commit()
        cursor.close()

        return redirect(url_for('visualizacion'))

    usuario = df.iloc[id]
    return render_template('editar.html', id=id, usuario=usuario)

@app.route('/corregir_datos', methods=['POST'])
def corregir_datos():
    datos = request.get_json()
    datos_corregidos = datos  # Por ahora, simplemente devolvemos los mismos datos
    
    # Convertir los datos corregidos a un formato adecuado para la tabla
    datos_corregidos_formateados = [
        [{'valor': celda, 'estilo': ''} for celda in fila] for fila in datos_corregidos
    ]
    return jsonify(datos_corregidos_formateados)

@app.route('/buscar', methods=['GET', 'POST'])
def buscar():
    resultados = []
    if request.method == 'POST':
        busqueda = request.form['busqueda']
        df = pd.read_csv(csv_file)
        resultados = df[df.apply(lambda row: busqueda.lower() in row.astype(str).str.lower().to_string(), axis=1)]
    return render_template('buscar.html', resultados=resultados)

# Configurar b64encode para Jinja2
@app.template_filter('b64encode')
def b64encode_filter(data):
    return base64.b64encode(data).decode('utf-8')

if __name__ == '__main__':
    if verificar_conexion():
        print("La conexión a la base de datos se estableció correctamente.")
        app.run(debug=True)
    else:
        print("Error: No se pudo establecer la conexión a la base de datos.")
