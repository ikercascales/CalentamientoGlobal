import os
import io
import json
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types
from PIL import Image

app = Flask(__name__)

api_key = os.environ.get("GEMINI_API_KEY", "API_KEY_AQUI")
client = genai.Client(api_key=api_key)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analizar", methods=["POST"])
def analizar():
    if "imagen" not in request.files:
        return jsonify({"error": "No se ha subido ninguna imagen"}), 400

    archivo = request.files["imagen"]
    if archivo.filename == "":
        return jsonify({"error": "Archivo no seleccionado"}), 400

    try:
        imagen = Image.open(io.BytesIO(archivo.read()))

        prompt = """
        Analiza el objeto principal de esta imagen para un sistema de reciclaje y combate contra el calentamiento global.
        Responde EXCLUSIVAMENTE en formato JSON válido con la siguiente estructura exacta:
        {
            "objeto": "Nombre del objeto identificado",
            "contenedor": "Color y tipo de contenedor (ej. Amarillo - Plásticos y Latas, Azul - Papel y Cartón, Verde - Vidrio, Gris/Marrón - Orgánico/Resto)",
            "instrucciones_reciclaje": "Paso a paso de cómo prepararlo antes de tirarlo (ej. enjuagar, quitar la tapa)",
            "informacion_ambiental": "Información educativa sobre el impacto de este material en el calentamiento global y tiempo de degradación",
            "puede_reutilizarse": true,
            "ideas_reutilizacion": [
                "Idea creativa 1 para darle una segunda vida",
                "Idea creativa 2 para darle una segunda vida"
            ]
        }
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[imagen, prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        datos = json.loads(response.text)
        return jsonify(datos)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
