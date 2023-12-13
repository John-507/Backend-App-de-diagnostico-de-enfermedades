import json
from experta import Fact, KnowledgeEngine, Rule, MATCH 
from flask import Flask, request, jsonify
from flask_cors import CORS

# Se inicializa la aplicación Flask
app = Flask(__name__)
# Para permitir solicitudes de diferentes dominios
CORS(app)

#clase para representar un sintoma como un hecho
class Sintoma(Fact):
 pass

# clase para el motor que maneja el diagnóstico
class Diagnostico(KnowledgeEngine):
    # Este es el onstructor de la clase
    def __init__(self, enfermedades_data, sintomas_data):
        super().__init__()
        # Datos de enfermedades y síntomas
        self.enfermedades_data = enfermedades_data
        self.sintomas_data = sintomas_data
        # Se inicializa los puntajes de enfermedades
        self.enfermedades_puntaje = {enfermedad['nombre']: 0 for enfermedad in enfermedades_data['enfermedades']}
        # Informacion de enfermedades
        self.enfermedades_info = {enfermedad['nombre']: {'descripcion': enfermedad['descripcion'], 'precauciones': enfermedad['precauciones']} for enfermedad in enfermedades_data['enfermedades']}
        # Mapeo de ID de smntoma a nombre
        self.id_a_nombre_sintoma = {sintoma['id']: sintoma['nombre'] for sintoma in sintomas_data['sintomas']}

    # Regla para chequear un síntoma y actualizar el puntaje de enfermedades
    @Rule(Sintoma(nombre=MATCH.nombre))
    def chequear_sintoma(self, nombre):
        for enfermedad in self.enfermedades_data['enfermedades']:
            if nombre in [self.id_a_nombre_sintoma[sintoma_id] for sintoma_id in enfermedad['sintomas']]:
                self.enfermedades_puntaje[enfermedad['nombre']] += 1

    # Método para finalizar el diagnóstico y sugiere una enfermdad
    def finalizar_diagnostico(self):
        enfermedad_sugerida = max(self.enfermedades_puntaje, key=self.enfermedades_puntaje.get)
        info = self.enfermedades_info[enfermedad_sugerida]
        return {
            "enfermedad": enfermedad_sugerida,
            "descripcion": info['descripcion'],
            "precauciones": info['precauciones']
        }
# Ruta para hacer el diagnóstico  
@app.route('/diagnosticar', methods=['POST'])
def diagnosticar():
    # Obtiene los síntomas del usuario desde el frontend
    data = request.json
    sintomas_usuario = data['sintomas']

    # Cargar los datos de enfermedades y síntomas desde los JSON
    with open('enfermedades.json', 'r') as file:
        enfermedades_data = json.load(file)
    with open('sintomas.json', 'r') as file:
        sintomas_data = json.load(file)

    # Crea una instancia del motor de conocimiento
    engine = Diagnostico(enfermedades_data, sintomas_data)

    # Declaración de los síntomas seleccionados por el usuario
    engine.reset()
    for sintoma_nombre in sintomas_usuario:
        engine.declare(Sintoma(nombre=sintoma_nombre))

    # Ejecuta el motor de conocimiento
    engine.run()
    resultado = engine.finalizar_diagnostico()

    # Envia la respuesta en formato JSON al frontend
    return jsonify(resultado)

# Ruta para obtener la lista de síntomas
@app.route('/sintomas', methods=['GET'])
def obtener_sintomas():
    # Cargar y devuelve los síntomas en formato JSON al frontend
    with open('sintomas.json', 'r') as file:
        sintomas_data = json.load(file)
    return jsonify(sintomas_data['sintomas'])

# Ruta predeterminada que muestra un mensaje de bienvenida
@app.route('/')
def index():
    return "<h1 style='font-size:24px;'>Hola! La Aplicación Flask está en ejecución</h1>"

# Se inicia el servidor
if __name__ == '__main__':
    app.run(debug=True)

