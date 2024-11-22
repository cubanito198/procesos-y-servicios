from flask import Flask

app = Flask(__name__)

@app.route('/')
def inicio():
    return "Hola mundo!"

if __name__ == '__main__':
    app.run(debug=True, host='192.168.1.225')
