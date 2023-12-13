import json
from experta import Fact, KnowledgeEngine, Rule, MATCH 
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Crear una clase para los síntomas como hechos
class Sintoma(Fact):
 pass

# Definir una clase para el diagnóstico
class Diagnostico(KnowledgeEngine):
    def __init__(self, enfermedades_data, sintomas_data):
        super().__init__()
        self.enfermedades_data = enfermedades_data
        self.sintomas_data = sintomas_data
        self.enfermedades_puntaje = {enfermedad['nombre']: 0 for enfermedad in enfermedades_data['enfermedades']}
        self.enfermedades_info = {enfermedad['nombre']: {'descripcion': enfermedad['descripcion'], 'precauciones': enfermedad['precauciones']} for enfermedad in enfermedades_data['enfermedades']}
        self.id_a_nombre_sintoma = {sintoma['id']: sintoma['nombre'] for sintoma in sintomas_data['sintomas']}

    @Rule(Sintoma(nombre=MATCH.nombre))
    def chequear_sintoma(self, nombre):
        for enfermedad in self.enfermedades_data['enfermedades']:
            if nombre in [self.id_a_nombre_sintoma[sintoma_id] for sintoma_id in enfermedad['sintomas']]:
                self.enfermedades_puntaje[enfermedad['nombre']] += 1

    def finalizar_diagnostico(self):
        enfermedad_sugerida = max(self.enfermedades_puntaje, key=self.enfermedades_puntaje.get)
        info = self.enfermedades_info[enfermedad_sugerida]
        return {
            "enfermedad": enfermedad_sugerida,
            "descripcion": info['descripcion'],
            "precauciones": info['precauciones']
        }
    
@app.route('/diagnosticar', methods=['POST'])
def diagnosticar():
    data = request.json
    sintomas_usuario = data['sintomas']

    # Cargar los datos de enfermedades y síntomas desde los archivos JSON
    with open('enfermedades.json', 'r') as file:
        enfermedades_data = json.load(file)
    with open('sintomas.json', 'r') as file:
        sintomas_data = json.load(file)

    # Crear una instancia del motor de conocimiento
    engine = Diagnostico(enfermedades_data, sintomas_data)

    # Declarar los síntomas seleccionados por el usuario
    engine.reset()
    for sintoma_nombre in sintomas_usuario:
        engine.declare(Sintoma(nombre=sintoma_nombre))

    # Ejecutar el motor de conocimiento
    engine.run()
    resultado = engine.finalizar_diagnostico()

    # Enviar la respuesta en formato JSON
    return jsonify(resultado)

@app.route('/sintomas', methods=['GET'])
def obtener_sintomas():
    with open('sintomas.json', 'r') as file:
        sintomas_data = json.load(file)
    return jsonify(sintomas_data['sintomas'])


@app.route('/')
def index():
    return "<h1 style='font-size:24px;'>Hola! La Aplicación Flask está en ejecución</h1>"

if __name__ == '__main__':
    app.run(debug=True)

