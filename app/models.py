from datetime import datetime
from flask_login import UserMixin
from app import db
import uuid
import secrets

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    nome = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True)
    tipo = db.Column(db.String(20), default='dentista')
    ativo = db.Column(db.Boolean, default=True)
    ultimo_acesso = db.Column(db.DateTime)
    data_cadastro = db.Column(db.DateTime, default=datetime.now)

class Paciente(db.Model):
    __tablename__ = 'pacientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(128), nullable=False)
    nascimento = db.Column(db.Date)
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.String(256))
    cpf = db.Column(db.String(14), unique=True)
    genero = db.Column(db.String(20))
    doencas = db.Column(db.Text)
    medicamentos = db.Column(db.Text)
    alergias = db.Column(db.Text)
    cirurgias = db.Column(db.Text)
    habitos = db.Column(db.Text)
    observacoes = db.Column(db.Text)
    data_cadastro = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    evolucoes = db.relationship('Evolucao', backref='paciente', lazy='dynamic', cascade='all, delete-orphan')
    radiografias = db.relationship('Radiografia', backref='paciente', lazy='dynamic', cascade='all, delete-orphan')
    agendamentos = db.relationship('Agendamento', backref='paciente', lazy='dynamic', cascade='all, delete-orphan')
    formularios = db.relationship('FormularioPreConsulta', backref='paciente', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Paciente {self.nome}>'
    
    @property
    def idade(self):
        if not self.nascimento:
            return None
        hoje = datetime.now().date()
        return hoje.year - self.nascimento.year - ((hoje.month, hoje.day) < (self.nascimento.month, self.nascimento.day))

class Evolucao(db.Model):
    __tablename__ = 'evolucoes'
    
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    procedimento = db.Column(db.String(256), nullable=False)
    supervisor = db.Column(db.String(128))
    observacao = db.Column(db.Text)
    detalhes = db.Column(db.Text)
    data_registro = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<Evolucao {self.id} - Paciente {self.paciente_id}>'

class Radiografia(db.Model):
    __tablename__ = 'radiografias'
    
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    nome_arquivo = db.Column(db.String(256), nullable=False)
    descricao = db.Column(db.Text)
    data_upload = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<Radiografia {self.id} - Paciente {self.paciente_id}>'

class Agendamento(db.Model):
    __tablename__ = 'agendamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    data_consulta = db.Column(db.Date, nullable=False)
    hora_consulta = db.Column(db.String(5), nullable=False)  # Format: HH:MM
    tipo_consulta = db.Column(db.String(128), nullable=False)
    observacao = db.Column(db.Text)
    status = db.Column(db.String(20), default='agendada')  # agendada, concluida, cancelada, faltou
    data_registro = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<Agendamento {self.id} - Paciente {self.paciente_id}>'

class FormularioPreConsulta(db.Model):
    __tablename__ = 'formularios_pre_consulta'
    
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    agendamento_id = db.Column(db.Integer, db.ForeignKey('agendamentos.id'))
    token = db.Column(db.String(64), unique=True, default=lambda: secrets.token_urlsafe(32))
    data_envio = db.Column(db.DateTime, default=datetime.now)
    data_preenchimento = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pendente')  # pendente, preenchido, expirado
    historico_medico = db.Column(db.Text)
    queixas = db.Column(db.Text)
    medicamentos_atuais = db.Column(db.Text)
    alergias_novas = db.Column(db.Text)
    observacoes = db.Column(db.Text)
    
    # Relationship with Agendamento
    agendamento = db.relationship('Agendamento', backref='formulario')
    
    def __repr__(self):
        return f'<Formulario {self.id} - Paciente {self.paciente_id}>'
