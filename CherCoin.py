# ----------------------------------
# |   BLOCKCHAIN Y CRIPTOMONEDAS   |
# ----------------------------------
# |  CRIPTOMONEDA PRIMITIVA  |
# ----------------------------

#Librerias para crear el Blockchain

import datetime
import hashlib
import json
from flask import flask, jsonfy, requests
import requests
from uuid import uuid4
from urllib.parse import urlparse

#Aqui es donde esta creado el Blockchain

class Blockchain:
    def __init__(self):
        self.cadena = []
        self.transaccion = []
        self.crear_bloque(proof=1, hash_anterior='0')
        self.nodos = set()

    def agregar_nodo(self, direccion):
        parsed_url = urlparse(direccion)
        self.nodos.add(parsed_url.netloc)

    def reemplazar_cadena(self):
        red = self.nodos
        cadena_mas_larga = None
        maxima_longitud = len(self.cadena)

        for nodo in red:
            respuesta = requests.get(f'http://{nodo}/conseguir_cadena')

            if (respuesta.status_code == 200):
                longitud = respuesta.json(['longitud'])
                cadena = respuesta.json(['cadena'])

                if (longitud > maxima_longitud and self.cadena_valida(cadena)):
                    maxima_longitud = longitud
                    cadena_mas_larga = cadena

            if (cadena_mas_larga):
                self.cadena = cadena_mas_larga
                return True
            return False

    def crear_bloque(self, prueba, hash_anterior):
        bloque = {
        'index':len(self.cadena)+1,
        'marcas_tiempo': str(datetime.datetime.now()),
        'prueba': prueba,
        'hash_anterior': hash_anterior,
        'transaccion': self.transaccion
        }

        self.transaccion = []
        self.cadena.append(bloque)
        return bloque

    def agregar_transaccion(self, remitente, recibio, cantidad):
        self.transaccion.append({
        'remitente': remitente,
        'recibio': recibio,
        'cantidad': cantidad
        })

    bloque_anterior = self.obtener_bloque_anterior()
    return self.bloque_anterior['index']+1

    def obtener_bloque_anterior(self):
        return self.cadena[-1]

    def prueba_trabajo(self, bloque_anterior):
        nueva_prueba = 1
        chequear_prueba = False

        while chequear_prueba is False:
            operacion_hash = hashlib.sha256(str(nueva_prueba**2 - bloque_anterior**2).encode()).hexdigest()

            if (operacion_hash[:4] == '0000'):
                chequear_prueba = True
            else:
                nueva_prueba += 1
            return nueva_prueba

    def hash(self, bloque):
        codificar_bloque = json.dumps(bloque, sort_keys = True).encode()
        return hashlib.sha256(codificar_bloque).hexdigest()

    def cadena_valida(self, cadena):
        bloque_anterior = cadena[0]
        bloque_index = 1

        while bloque_index < len(cadena):
            bloque = cadena[bloque_index]

            if (bloque['hash_anterior'] != self.hash(bloque_anterior)):
                return False

            prueba_anterior = bloque_anterior['prueba']
            prueba = bloque['prueba']
            operacion_hash = hashlib.sha256(str(nueva_prueba**2 - bloque_anterior**2).encode()).hexdigest()

            if (operacion_hash[:4] != '0000'):
                return False

            bloque_anterior = bloque
            bloque_index += 1
        return True

#Aqui es donde esta hecha el apartado de Minar el Blockchain

app = Flask(__name__)

#Creando una direccion para el nodo del puerto 5000
direccion_nodo = str(uuid4()).replace('-','')
blockchain = blockchain()

@app.route('/mina_bloque', methods=['GET'])

def mina_bloque():
    bloque_anterior = blockchain.obtener_bloque_anterior()
    prueba_anterior = bloque_anterior['prueba']
    prueba = blockchain.prueba_trabajo(prueba_anterior)
    hash_anterior = blockchain.hash(bloque_anterior)
    blockchain.agregar_transaccion(remitente = direccion_nodo, recibio = 'Cheremi', cantidad = 1)
    bloque = blockchain.crear_bloque(prueba, hash_anterior)
    respuesta = {
    'mensaje':'Felicidades, haz minado un bloque!',
    'index': bloque['index'],
    'timestamp': bloque['timestamp'],
    'prueba': bloque['prueba'],
    'hash_anterior': bloque['hash_anterior'],
    'transaccion': bloque['transaccion']
    }
    return jsonfy(respuesta), 200

@app.route('/conseguir_cadena', methods=['GET'])
def conseguir_cadena():
    respuesta = {
    'cadena': blockchain.cadena,
    'length': len(blockchain.cadena)
    }
    return jsonfy(respuesta), 200

#Aqui se chequea la validez del Blockchain

@app.route('/es_valido', methods=['GET'])
def es_valido():
    es_valido = blockchain.cadena_valida(blockchain.cadena)
    if (es_valido):
        responde = {'mensaje':'El Blockchain es valido'}
    else:
        responde = {'mensaje':'Hay problemas el Blockchain no es valido'}
    return jsonfy(responde), 200

# Agregando nueva transaccion

@app.route('/agregar_transaccion', methods=['POST'])
def agregar_transaccion():
    json = requests.get.json()
    claves_transaccion = ['remitente', 'recibio', 'cantidad']

    if not all (clave in json for clave in claves_transaccion):
        return 'Algun elemento faltante', 400

    index = blockchain.agregar_transaccion(json['remitente'], json['recibio'], json['cantidad'])
    responde = {'mensaje': f'La transaccion sera añadida al bloque {index}'}
    return jsonfy(responde), 201

# Desentralizando el Blockchain

@app.route('/conectar_nodo', methods=['POST'])
def conectar_nodo():
    json = request.get.json()
    nodos = json.get('nodos')

    if (nodos is None):
        return 'No nodo', 401

    for nodo in nodos:
        blockchain.agregar_nodos(nodo)
        responde = {
        'mensaje':'Todos los nodos estan conectados',
        'total_nodos': list(blockchain.nodos)
        }
        return jsonfy(responde), 201

# Remplazando la cadenas mas larga

@app.route('/remplazar_cadena', methods=['GET'])
def remplazar_cadena():
    remplazar_cadena = blockchain.remplazar_cadena()
    if (remplazar_cadena):
        responde = {
        'mensaje':'La cadena fue remplazada por la mas larga',
        'nueva_cadena': blockchain.cadena
        }
    else:
        responde = {
        'mensaje': 'La cadena es la mas larga',
        'Actual_cadena': blockchain.cadena
        }
    return jsonfy(responde), 200

#Ejecucion del Blockchain

app.run(host='0.0.0.0', port='5000')
