from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Configuração do SQLite para desenvolvimento
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'tickets.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de Dados
class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_solicitante = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    prioridade = db.Column(db.String(10), nullable=False, default='Baixa')
    status = db.Column(db.String(20), nullable=False, default='Aberto')
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

# Inicializar Banco de Dados
with app.app_context():
    db.create_all()

# Rota para a página principal
@app.route('/')
def index():
    return render_template('index.html')

# Rota para criar um ticket
@app.route('/tickets', methods=['POST'])
def criar_ticket():
    dados = request.get_json()
    novo_ticket = Ticket(
        nome_solicitante=dados['nome_solicitante'],
        descricao=dados['descricao'],
        prioridade=dados.get('prioridade', 'Baixa'),
    )
    db.session.add(novo_ticket)
    db.session.commit()
    return jsonify({"mensagem": "Ticket criado com sucesso!", "ticket_id": novo_ticket.id}), 201

# Rota para listar todos os tickets
@app.route('/tickets', methods=['GET'])
def listar_tickets():
    tickets = Ticket.query.all()
    resultado = [
        {
            "id": ticket.id,
            "nome_solicitante": ticket.nome_solicitante,
            "descricao": ticket.descricao,
            "prioridade": ticket.prioridade,
            "status": ticket.status,
            "data_criacao": ticket.data_criacao.strftime('%Y-%m-%d %H:%M:%S')
        } for ticket in tickets
    ]
    return jsonify(resultado), 200

# Rota para atualizar o status de um ticket
@app.route('/tickets/<int:id>', methods=['PUT'])
def atualizar_ticket(id):
    ticket = Ticket.query.get_or_404(id)
    dados = request.get_json()
    ticket.status = dados.get('status', ticket.status)
    db.session.commit()
    return jsonify({"mensagem": "Ticket atualizado com sucesso!"}), 200

# Rota para deletar um ticket
@app.route('/tickets/<int:id>', methods=['DELETE'])
def deletar_ticket(id):
    ticket = Ticket.query.get_or_404(id)
    db.session.delete(ticket)
    db.session.commit()
    return jsonify({"mensagem": "Ticket deletado com sucesso!"}), 200

if __name__ == '__main__':
    app.run(debug=True)
