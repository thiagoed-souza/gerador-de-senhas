import os
import secrets
import string
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # Limite de 2MB por foto

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Faça login para acessar esta página."

# --- MODELOS DO BANCO DE DADOS ---

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    foto_perfil = db.Column(db.String(255), default='default.png')
    senhas = db.relationship('SenhaSalva', backref='dono', lazy=True)

class SenhaSalva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    servico = db.Column(db.String(100), nullable=False)
    usuario_servico = db.Column(db.String(100), nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

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

# --- ROTAS DE AUTENTICAÇÃO ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        senha = request.form.get('senha', '')

        if Usuario.query.filter_by(username=username).first():
            flash('Nome de usuário já cadastrado.', 'danger')
            return redirect(url_for('register'))

        senha_hash = generate_password_hash(senha, method='scrypt')
        novo_usuario = Usuario(username=username, senha_hash=senha_hash)
        
        db.session.add(novo_usuario)
        db.session.commit()
        
        flash('Conta criada com sucesso! Faça login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        senha = request.form.get('senha', '')
        
        user = Usuario.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.senha_hash, senha):
            login_user(user)
            return redirect(url_for('dashboard'))
        
        flash('Usuário ou senha incorretos.', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sessão encerrada com sucesso.', 'info')
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
        # Alterar Senha
        if 'alterar_senha' in request.form:
            senha_atual = request.form.get('senha_atual')
            nova_senha = request.form.get('nova_senha')

            if not check_password_hash(current_user.senha_hash, senha_atual):
                flash('Senha atual incorreta.', 'danger')
            else:
                current_user.senha_hash = generate_password_hash(nova_senha, method='scrypt')
                db.session.commit()
                flash('Senha atualizada com sucesso!', 'success')

        # Alterar Foto de Perfil
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
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8000, debug=True)