from flask import Flask

inventario = 10

app = Flask(__name__)

@app.route('/')
def inicio():
    global inventario
    inventario -= 1
    return "Te quedan "+str(inventario)+" elementos en el inventario"

if __name__ == '__main__':
    app.run(debug=True, host='192.168.1.225')
