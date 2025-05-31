from flask import Flask, render_template, request, redirect, session, url_for
import csv, os

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

user_path = 'data/usuarios.csv'
prod_path = 'data/produtos.csv'
os.makedirs('data', exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        with open(user_path, 'a', newline='') as f:
            csv.writer(f).writerow([nome, email, senha])
        return redirect(url_for('login'))
    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        if email == 'admin@loja.com' and senha == 'admin123':
            session['usuario'] = 'Admin'
            session['admin'] = True
            return redirect(url_for('produtos'))
        with open(user_path, 'r') as f:
            for row in csv.reader(f):
                if row[1] == email and row[2] == senha:
                    session['usuario'] = row[0]
                    session['admin'] = False
                    return redirect(url_for('produtos'))
        return render_template('login.html', erro='Login inválido')
    return render_template('login.html', erro=None)

@app.route('/produtos')
def produtos():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    produtos = []
    if os.path.exists(prod_path):
        with open(prod_path, 'r') as f:
            for row in csv.reader(f):
                produtos.append({'nome': row[0], 'preco': row[1], 'desc': row[2], 'imagem': row[3]})
    return render_template('produtos.html', usuario=session['usuario'], produtos=produtos)

@app.route('/adicionar_produto', methods=['GET', 'POST'])
def adicionar_produto():
    if not session.get('admin'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        nome = request.form['nome']
        preco = request.form['preco']
        desc = request.form['desc']
        imagem = request.form['imagem']
        with open(prod_path, 'a', newline='') as f:
            csv.writer(f).writerow([nome, preco, desc, imagem])
        return redirect(url_for('produtos'))
    return render_template('adicionar_produto.html')

@app.route('/adicionar_carrinho/<nome>')
def adicionar_carrinho(nome):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    carrinho = session.get('carrinho', [])
    carrinho.append(nome)
    session['carrinho'] = carrinho
    return redirect(url_for('carrinho'))

@app.route('/carrinho')
def carrinho():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    carrinho = session.get('carrinho', [])
    return render_template('carrinho.html', carrinho=carrinho)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)