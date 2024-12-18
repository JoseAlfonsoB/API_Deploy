from flask import Flask, render_template, abort, send_file
import os
import nbformat
from nbconvert import HTMLExporter
from io import StringIO

app = Flask(__name__)
    # ----COMANDOS----
# Crear un ambiente virtual: python -m venv venv
# Inicializar el ambiente virtual: source venv/bin/activate 
# Desactivar el ambiente virtual. deactivate
# Arrancar el servicio: python app.py
# Detener el servicio. Ctrl + C

# Carpeta donde están los notebooks
NOTEBOOK_FOLDER = os.path.join(os.getcwd(), 'Notebooks')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/Notebooks/<path:filename>')
def view_notebook(filename):
    notebook_path = os.path.join(NOTEBOOK_FOLDER, filename)
    
    # Verifica si el archivo existe
    if not os.path.exists(notebook_path):
        abort(404, description="Notebzook no encontrado")
    
    # Convierte el archivo a HTML
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook_content = nbformat.read(f, as_version=4)
        html_exporter = HTMLExporter()
        body, _ = html_exporter.from_notebook_node(notebook_content)
        
        # Devuelve el HTML generado al navegador
        return body
    except Exception as e:
        abort(500, description=f"Error al procesar el notebook: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)
    
