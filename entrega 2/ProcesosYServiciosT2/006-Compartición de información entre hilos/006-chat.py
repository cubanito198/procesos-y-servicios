from flask import Flask, request, jsonify                            # Importamos la libreria Flask y requests para coger parametros de la url
from flask_cors import CORS

mensajes = []                                               # Creamos una lista que cuando arranca el servidor esta vacia

app = Flask(__name__)                                       # Creamos una nueva aplicación de servidor web
CORS(app)

@app.route('/')                                             # Cuando alguien llame a la raiz
def inicio():                                               # Creo una función
    return "Hola mundo"                                     # Devuelvo una cadena
    
@app.route('/dame')                                         # Cuando alguien llame a la ruta dame
def dame():                                                 # Defino una funcion
    global mensajes                                         # Meto en la funcion la variable mensajes
    return jsonify(mensajes)                                    # La convierto a string y la devuelvo por pantalla

@app.route('/toma')                                         # cuando alguien llame a la ruta toma
def toma():                                                 # Defino una funcion
    global mensajes                                         # Meto la variable global
    mensaje = request.args.get('mensaje')                   # atrapo el parametro de url llamado mensaje
    mensajes.append({'mensaje':mensaje})                                # Lo añado a la lista de mensajes
    return str({"mensaje":"ok"})                            # Devuelvo un json que dice ok

if __name__ == '__main__':                                  # Si esta es la clase principal
    app.run(debug=True, host='192.168.1.225')               # Ejecuta la aplicación y escucha en el puerto 5000, en la ip que indico
