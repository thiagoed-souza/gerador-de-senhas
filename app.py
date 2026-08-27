import secrets
import string
from flask import Flask, render_template, request

app = Flask(__name__)

def gerar_senha(tamanho, incluir_maiusculas, incluir_numeros, incluir_simbolos):
    caracteres = string.ascii_lowercase

    if incluir_maiusculas:
        caracteres += string.ascii_uppercase
    if incluir_numeros:
        caracteres += string.digits
    if incluir_simbolos:
        caracteres += string.punctuation

    if not caracteres:
        return ""

    return ''.join(secrets.choice(caracteres) for _ in range (tamanho))

@app.route('/', methods=['GET', 'POST'])
def index():
    senha_gerada = ""
    tamanho = 12
    maiusculas = True
    numeros = True
    simbolos = True

    if request.method == 'POST':
        tamanho = int(request.form.get('tamanho', 12))
        maiusculas = 'maiusculas' in request.form
        numeros = 'numeros' in request.form
        simbolos = 'simbolos' in request.form
        
        senha_gerada = gerar_senha(tamanho, maiusculas, numeros, simbolos)

    return render_template(
        'index.html',
        senha=senha_gerada,
        tamanho=tamanho,
        maiusculas=maiusculas,
        numeros=numeros,
        simbolos=simbolos
    )

if __name__ == '__main__':
    app.run(debug=True)