import json
from experta import Fact, KnowledgeEngine, Rule, MATCH 

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