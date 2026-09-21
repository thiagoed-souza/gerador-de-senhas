import os
import secrets
import string
import traceback
from datetime import datetime
from dotenv import load_dotenv  # Importa a biblioteca para ler o .env

# Carrega as variáveis de ambiente do arquivo .env (rodando localmente)
load_dotenv()

from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # Limite de 2MB

# --- CONFIGURAÇÕES DE ENVIO DE E-MAIL (SMTP) ---
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', '1']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']

mail = Mail(app)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# --- MODELOS DO BANCO DE DADOS ---

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    data_nascimento = db.Column(db.String(10), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    foto_perfil = db.Column(db.String(255), default='default.png')
    
    # Controle de Verificação de E-mail
    verificado = db.Column(db.Boolean, default=False)
    codigo_verificacao = db.Column(db.String(6), nullable=True)

    senhas = db.relationship('SenhaSalva', backref='dono', lazy=True)

class SenhaSalva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    servico = db.Column(db.String(100), nullable=False)
    usuario_servico = db.Column(db.String(100), nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

# Força a remoção do banco SQLite antigo se as colunas estiverem desatualizadas no Render
with app.app_context():
    caminhos_db = [
        os.path.join(app.root_path, 'database.db'),
        os.path.join(app.root_path, 'instance', 'database.db')
    ]
    
    for db_file in caminhos_db:
        if os.path.exists(db_file):
            try:
                os.remove(db_file)
                print(f"[BANCO DE DADOS] Arquivo antigo {db_file} removido.")
            except Exception as e:
                print(f"[BANCO DE DADOS] Aviso ao tentar remover: {e}")

    db.create_all()
    print("[BANCO DE DADOS] Tabelas recriadas com sucesso com a nova estrutura!")

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Faça login para acessar esta página."

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# --- FUNÇÕES AUXILIARES ---

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def gerar_senha(tamanho=12, maiusculas=True, numeros=True, simbolos=True):
    caracteres = string.ascii_lowercase
    if maiusculas:
        caracteres += string.ascii_uppercase
    if numeros:
        caracteres += string.digits
    if simbolos:
        caracteres += string.punctuation
    
    if not caracteres:
        return ""
    
    return ''.join(secrets.choice(caracteres) for _ in range(tamanho))

def enviar_codigo_email(destinatario_email, codigo):
    if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
        print("[ERRO SMTP] MAIL_USERNAME ou MAIL_PASSWORD não foram configurados nas variáveis de ambiente.")
        return False

    try:
        msg = Message(
            subject="Código de Verificação de Conta - PassGuard",
            sender=app.config['MAIL_USERNAME'],
            recipients=[destinatario_email],
            body=f"Olá!\n\nSeu código de verificação é: {codigo}\n\nSe você não solicitou este cadastro, ignore esta mensagem."
        )
        mail.send(msg)
        return True
    except Exception as e:
        print("[ERRO NO ENVIO DE E-MAIL]:")
        traceback.print_exc()
        return False

# --- ROTAS DE AUTENTICAÇÃO ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            nome = request.form.get('nome', '').strip()
            email = request.form.get('email', '').strip().lower()
            data_nascimento = request.form.get('data_nascimento', '').strip()
            username = request.form.get('username', '').strip()
            senha = request.form.get('senha', '')

            if Usuario.query.filter_by(username=username).first():
                flash('Nome de usuário já cadastrado.', 'danger')
                return redirect(url_for('register'))

            if Usuario.query.filter_by(email=email).first():
                flash('Este e-mail já está sendo utilizado.', 'danger')
                return redirect(url_for('register'))

            codigo = f"{secrets.randbelow(1000000):06d}"
            senha_hash = generate_password_hash(senha, method='scrypt')

            novo_usuario = Usuario(
                nome=nome,
                email=email,
                data_nascimento=data_nascimento,
                username=username,
                senha_hash=senha_hash,
                codigo_verificacao=codigo,
                verificado=False
            )
            
            db.session.add(novo_usuario)
            db.session.commit()

            # Tenta enviar o e-mail
            if enviar_codigo_email(email, codigo):
                session['email_pendente'] = email
                flash('Cadastro realizado! Verifique seu e-mail para obter o código.', 'info')
                return redirect(url_for('verificar'))
            else:
                db.session.delete(novo_usuario)
                db.session.commit()
                flash('Não foi possível enviar o e-mail de verificação. Verifique as credenciais de e-mail no servidor.', 'danger')
                return redirect(url_for('register'))

        except Exception as e:
            db.session.rollback()
            print("[ERRO NA ROTA DE REGISTRO]:")
            traceback.print_exc()
            flash('Ocorreu um erro interno ao processar o cadastro. Tente novamente.', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/verificar', methods=['GET', 'POST'])
def verificar():
    email = session.get('email_pendente')
    if not email:
        return redirect(url_for('login'))

    if request.method == 'POST':
        codigo_digitado = request.form.get('codigo', '').strip()
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and usuario.codigo_verificacao == codigo_digitado:
            usuario.verificado = True
            usuario.codigo_verificacao = None
            db.session.commit()
            
            session.pop('email_pendente', None)
            flash('E-mail verificado com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Código incorreto. Tente novamente.', 'danger')

    return render_template('verificar.html', email=email)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        senha = request.form.get('senha', '')
        
        user = Usuario.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.senha_hash, senha):
            if not user.verificado:
                session['email_pendente'] = user.email
                flash('Sua conta ainda não foi verificada. Digite o código enviado ao seu e-mail.', 'warning')
                return redirect(url_for('verificar'))

            login_user(user)
            return redirect(url_for('dashboard'))
        
        flash('Usuário ou senha incorretos.', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sessão encerrada.', 'info')
    return redirect(url_for('login'))

# --- ROTAS PRINCIPAIS ---

@app.route('/', methods=['GET', 'POST'])
@login_required
def dashboard():
    senha_gerada = ""
    tamanho = 12
    maiusculas = True
    numeros = True
    simbolos = True

    if request.method == 'POST':
        if 'gerar' in request.form:
            tamanho = int(request.form.get('tamanho', 12))
            maiusculas = 'maiusculas' in request.form
            numeros = 'numeros' in request.form
            simbolos = 'simbolos' in request.form
            senha_gerada = gerar_senha(tamanho, maiusculas, numeros, simbolos)
            
        elif 'salvar' in request.form:
            servico = request.form.get('servico')
            usuario_servico = request.form.get('usuario_servico')
            senha = request.form.get('senha_para_salvar')
            
            if servico and senha:
                nova_senha = SenhaSalva(
                    servico=servico,
                    usuario_servico=usuario_servico,
                    senha=senha,
                    user_id=current_user.id
                )
                db.session.add(nova_senha)
                db.session.commit()
                flash('Credencial salva no cofre!', 'success')
                return redirect(url_for('dashboard'))

    minhas_senhas = SenhaSalva.query.filter_by(user_id=current_user.id).all()

    return render_template(
        'dashboard.html',
        senha=senha_gerada,
        tamanho=tamanho,
        maiusculas=maiusculas,
        numeros=numeros,
        simbolos=simbolos,
        minhas_senhas=minhas_senhas
    )

@app.route('/deletar_senha/<int:id>')
@login_required
def deletar_senha(id):
    item = SenhaSalva.query.get_or_404(id)
    if item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
        flash('Item removido do cofre.', 'info')
    return redirect(url_for('dashboard'))

@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    if request.method == 'POST':
        if 'alterar_senha' in request.form:
            senha_atual = request.form.get('senha_atual')
            nova_senha = request.form.get('nova_senha')

            if not check_password_hash(current_user.senha_hash, senha_atual):
                flash('Senha atual incorreta.', 'danger')
            else:
                current_user.senha_hash = generate_password_hash(nova_senha, method='scrypt')
                db.session.commit()
                flash('Senha atualizada com sucesso!', 'success')

        elif 'alterar_foto' in request.form:
            if 'foto' not in request.files:
                flash('Nenhum arquivo enviado.', 'danger')
                return redirect(url_for('perfil'))
            
            file = request.files['foto']
            if file.filename == '':
                flash('Nenhum arquivo selecionado.', 'danger')
                return redirect(url_for('perfil'))

            if file and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                nome_foto = f"user_{current_user.id}_{secrets.token_hex(4)}.{ext}"
                caminho = os.path.join(app.config['UPLOAD_FOLDER'], nome_foto)
                file.save(caminho)

                current_user.foto_perfil = nome_foto
                db.session.commit()
                flash('Foto de perfil atualizada!', 'success')
            else:
                flash('Formato não permitido. Use JPG, PNG ou GIF.', 'danger')

    return render_template('perfil.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
