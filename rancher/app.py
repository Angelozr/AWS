import json
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DATA_FILE = '/app/data/productos.json'  # Directorio montado en el volumen persistente

# Crear el directorio si no existe
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

# Inicializar los datos
datos = []

# Guardar los datos en el archivo JSON
def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(datos, f)

# Leer los datos desde el archivo JSON
def load_data():
    global datos
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            datos = json.load(f)
    else:
        datos = []  # Si no existe el archivo, inicializamos los datos con una lista vacía

# Cargar los datos al iniciar la aplicación
load_data()
    

# Ruta principal para mostrar los productos
@app.route('/')
def index():
    query = request.args.get('search', '')
    
    # Filtrar productos según la búsqueda
    productos_filtrados = [p for p in datos if query.lower() in p['nombre'].lower()]

    # Total de productos
    total_productos = len(datos)
    
    # Calcular precio promedio
    precio_promedio = (
        sum(float(p['precio']) for p in datos) / total_productos 
        if total_productos > 0 else 0
    )

    # Contar productos en stock (suponiendo que un precio > 0 significa que está en stock)
    productos_en_stock = sum(1 for p in datos if float(p['precio']) > 0)

    return render_template('index.html',
                           productos=productos_filtrados,
                           search=query,
                           total_productos=total_productos,
                           precio_promedio=precio_promedio,
                           productos_en_stock=productos_en_stock)

# Ruta para agregar un nuevo producto
@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        nuevo_producto = {
            'id': len(datos) + 1,
            'nombre': request.form['nombre'],
            'precio': request.form['precio'],
            'descripcion': request.form['descripcion'],
        }
        datos.append(nuevo_producto)
        save_data()  # Guardamos los datos después de agregar un producto
        return redirect(url_for('index'))
    return render_template('add_product.html')

# Ruta para editar un producto existente
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    producto = next((p for p in datos if p['id'] == id), None)
    if request.method == 'POST':
        if producto:
            producto['nombre'] = request.form['nombre']
            producto['precio'] = request.form['precio']
            producto['descripcion'] = request.form['descripcion']
            save_data()  # Guardamos los datos después de editar el producto
            return redirect(url_for('index'))
    return render_template('edi_product.html', producto=producto)

# Ruta para eliminar productos
@app.route('/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    global datos
    # Encontrar el producto por su ID
    producto = next((p for p in datos if p['id'] == product_id), None)
    if producto:
        datos.remove(producto)  # Eliminar el producto de la lista
        save_data()  # Guardamos los datos después de eliminar un producto
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
