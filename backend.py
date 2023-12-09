import json
# Cargar los datos de síntomas y enfermedades desde los archivos JSON
with open('sintomas.json', 'r') as file:
 sintomas_data = json.load(file)
with open('enfermedades.json', 'r') as file:
 enfermedades_data = json.load(file)
 