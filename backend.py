import json
from experta import Fact, KnowledgeEngine, Rule, MATCH 
from flask import Flask, request, jsonify

app = Flask(__name__)

# Cargar los datos de síntomas y enfermedades desde los archivos JSON
with open('sintomas.json', 'r') as file:
 sintomas_data = json.load(file)
with open('enfermedades.json', 'r') as file:
 enfermedades_data = json.load(file)

# Crear una clase para los síntomas como hechos
class Sintoma(Fact):
 pass
# Crear un diccionario para mapear IDs de síntomas a nombres
id_a_nombre_sintoma = {sintoma['id']: sintoma['nombre'] for sintoma in sintomas_data['sintomas']}
# Crear un diccionario para mapear nombres de enfermedades a su descripción y precauciones
enfermedades_info = {enfermedad['nombre']: {'descripcion': enfermedad['descripcion'], 'precauciones': enfermedad['precauciones']} for enfermedad in enfermedades_data['enfermedades']}

# Crear una instancia de Sintoma para cada síntoma
sintomas_dict = {sintoma['nombre']: Sintoma(nombre=sintoma['nombre']) for sintoma in sintomas_data['sintomas']}

# Definir una clase para el diagnóstico
class Diagnostico(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.enfermedades_puntaje = {enfermedad['nombre']: 0 for enfermedad in enfermedades_data['enfermedades']}

    @Rule(Sintoma(nombre=MATCH.nombre))
    def chequear_sintoma(self, nombre):
        for enfermedad in enfermedades_data['enfermedades']:
            if nombre in [id_a_nombre_sintoma[sintoma_id] for sintoma_id in enfermedad['sintomas']]:
                self.enfermedades_puntaje[enfermedad['nombre']] += 1

    def finalizar_diagnostico(self):
        enfermedad_sugerida = max(self.enfermedades_puntaje, key=self.enfermedades_puntaje.get)
        info = enfermedades_info[enfermedad_sugerida]
        return {
            "enfermedad": enfermedad_sugerida,
            "descripcion": info['descripcion'],
            "precauciones": info['precauciones']
        }
    
@app.route('/diagnosticar', methods=['POST'])
def diagnosticar():
    data = request.json
    sintomas_usuario = data['sintomas']

    # Crear una instancia del motor de conocimiento
    engine = Diagnostico()

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
    # Devuelve la lista de síntomas
    return jsonify(sintomas_data['sintomas'])

if __name__ == '__main__':
    app.run(debug=True)

