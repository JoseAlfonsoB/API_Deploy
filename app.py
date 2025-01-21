from flask import Flask, render_template, abort, send_file
import os
import nbformat
from nbconvert import HTMLExporter
from io import StringIO
import base64

app = Flask(__name__)

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
        abort(404, description="Notebook no encontrado")

    # Si es el notebook específico, mostrar la métrica de exactitud y la matriz de confusión
    if filename == "Regresion_Logistica_50K.ipynb":
        try:
            with open(notebook_path, 'r', encoding='utf-8') as f:
                notebook_content = nbformat.read(f, as_version=4)

            exactitud_output = None
            matriz_confusion_img = None

            # Buscar la métrica de exactitud y la imagen de la matriz de confusión
            for cell in notebook_content['cells']:
                if cell.get('cell_type') == 'code':
                    for output in cell.get('outputs', []):
                        if 'text' in output:
                            for line in output['text'].split('\n'):
                                if line.startswith("Exactitud:"):
                                    exactitud_output = line
                        if 'data' in output and 'image/png' in output['data']:
                            matriz_confusion_img = output['data']['image/png']

            # Construir la respuesta HTML con estilo
            response = """<html>
            <head>
                <style>
                    body {
                        background-color: #bde0fe;
                        font-family: Arial, sans-serif;
                        text-align: center;
                        padding: 20px;
                    }
                    h1 {
                        color: #333;
                    }
                    h2 {
                        color: #555;
                    }
                    img {
                        max-width: 100%;
                        height: auto;
                        border: 2px solid #333;
                        border-radius: 10px;
                        margin-top: 20px;
                    }
                    pre {
                        background-color: #f0f0f0;
                        padding: 10px;
                        border-radius: 5px;
                        display: inline-block;
                        font-size: 18px;
                    }
                </style>
            </head>
            <body>
            """

            if exactitud_output:
                response += f"<h1>Valor de Predicción</h1><pre>{exactitud_output}</pre>"
            if matriz_confusion_img:
                response += f"<h2>Matriz de Confusión</h2><img src='data:image/png;base64,{matriz_confusion_img}' alt='Matriz de Confusión' />"

            response += """</body></html>"""

            if not exactitud_output and not matriz_confusion_img:
                response = "<p>No se encontró la métrica de exactitud ni la matriz de confusión.</p>"

            return response
        except Exception as e:
            abort(500, description=f"Error al procesar el notebook: {str(e)}")

    # Convierte el archivo a HTML mostrando solo las gráficas para otros notebooks
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook_content = nbformat.read(f, as_version=4)

        outputs = []
        for cell in notebook_content['cells']:
            if cell.get('cell_type') == 'code' and 'outputs' in cell:
                for output in cell['outputs']:
                    if 'data' in output and 'image/png' in output['data']:
                        image_data = output['data']['image/png']
                        img_tag = f'<img src="data:image/png;base64,{image_data}" alt="Graph" />'
                        outputs.append(img_tag)

        # Si es el notebook "3501ArboldeDesicion.ipynb", agregar la imagen del árbol de decisión
        if filename == "3501ArboldeDesicion.ipynb":
            decision_tree_img_path = os.path.join(os.getcwd(), "templates", "Arbol_de_decision.png")
            if os.path.exists(decision_tree_img_path):
                with open(decision_tree_img_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                    outputs.append(f'<img src="data:image/png;base64,{encoded_string}" alt="Decision Tree Graph" />')

        return "<br>".join(outputs)
    except Exception as e:
        abort(500, description=f"Error al procesar el notebook: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)
