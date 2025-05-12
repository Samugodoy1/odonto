from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, SelectField
from wtforms import TextAreaField, TimeField, HiddenField, RadioField, ValidationError
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional
from email_validator import validate_email
from datetime import date
import re

class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired(message='Campo obrigatório')])
    password = PasswordField('Senha', validators=[DataRequired(message='Campo obrigatório')])
    remember = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')

class UsuarioForm(FlaskForm):
    nome = StringField('Nome Completo', validators=[DataRequired(message='Campo obrigatório')])
    username = StringField('Nome de Usuário', validators=[DataRequired(message='Campo obrigatório')])
    email = StringField('E-mail', validators=[DataRequired(message='Campo obrigatório'), Email(message='E-mail inválido')])
    password = PasswordField('Senha', validators=[DataRequired(message='Campo obrigatório')])
    confirm_password = PasswordField('Confirmar Senha', validators=[DataRequired(message='Campo obrigatório'), 
                                     EqualTo('password', message='As senhas não coincidem')])
    tipo = SelectField('Tipo de Usuário', choices=[('dentista', 'Dentista'), ('admin', 'Administrador')])
    ativo = BooleanField('Ativo', default=True)
    submit = SubmitField('Cadastrar')

class PacienteForm(FlaskForm):
    nome = StringField('Nome Completo', validators=[DataRequired(message='Campo obrigatório')])
    nascimento = DateField('Data de Nascimento', format='%Y-%m-%d', validators=[Optional()])
    telefone = StringField('Telefone', validators=[Optional()])
    endereco = StringField('Endereço', validators=[Optional()])
    cpf = StringField('CPF', validators=[Optional()])
    genero = SelectField('Gênero', choices=[
        ('', 'Selecione'),
        ('masculino', 'Masculino'),
        ('feminino', 'Feminino'),
        ('outro', 'Outro'),
        ('prefiro_nao_dizer', 'Prefiro não dizer')
    ], validators=[Optional()])
    doencas = TextAreaField('Doenças Preexistentes', validators=[Optional()])
    medicamentos = TextAreaField('Medicamentos em Uso', validators=[Optional()])
    alergias = TextAreaField('Alergias', validators=[Optional()])
    cirurgias = TextAreaField('Histórico de Cirurgias', validators=[Optional()])
    habitos = TextAreaField('Hábitos Relevantes', validators=[Optional()])
    observacoes = TextAreaField('Observações Adicionais', validators=[Optional()])
    submit = SubmitField('Salvar')
    
    def validate_cpf(self, field):
        if field.data:
            # Remove non-numeric characters
            cpf = re.sub(r'[^0-9]', '', field.data)
            
            # Check length
            if len(cpf) != 11:
                raise ValidationError('CPF deve conter 11 dígitos.')
            
            # Basic validation for CPF
            if cpf == cpf[0] * 11:
                raise ValidationError('CPF inválido.')
            
            # Format CPF with proper separators
            field.data = f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'

class EvolucaoForm(FlaskForm):
    paciente_id = HiddenField('ID do Paciente')
    data = DateField('Data', validators=[DataRequired(message='Campo obrigatório')], default=date.today)
    procedimento = StringField('Procedimento', validators=[DataRequired(message='Campo obrigatório')])
    supervisor = StringField('Supervisor/Dentista', validators=[Optional()])
    observacao = TextAreaField('Observação', validators=[Optional()])
    detalhes = TextAreaField('Detalhes do Procedimento', validators=[Optional()])
    submit = SubmitField('Salvar')

class AgendamentoForm(FlaskForm):
    paciente_id = HiddenField('ID do Paciente')
    data_consulta = DateField('Data da Consulta', validators=[DataRequired(message='Campo obrigatório')], default=date.today)
    hora_consulta = StringField('Hora da Consulta', validators=[DataRequired(message='Campo obrigatório')])
    tipo_consulta = StringField('Tipo de Consulta', validators=[DataRequired(message='Campo obrigatório')])
    observacao = TextAreaField('Observação', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('agendada', 'Agendada'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
        ('faltou', 'Faltou')
    ], default='agendada')
    submit = SubmitField('Salvar')

class FormularioPreConsultaForm(FlaskForm):
    paciente_id = HiddenField('ID do Paciente')
    agendamento_id = HiddenField('ID do Agendamento')
    historico_medico = TextAreaField('Histórico Médico', validators=[Optional()])
    queixas = TextAreaField('Queixas Principais', validators=[Optional()])
    medicamentos_atuais = TextAreaField('Medicamentos Atuais', validators=[Optional()])
    alergias_novas = TextAreaField('Alergias', validators=[Optional()])
    observacoes = TextAreaField('Observações Adicionais', validators=[Optional()])
    submit = SubmitField('Salvar')

class PreenchimentoFormularioForm(FlaskForm):
    historico_medico = TextAreaField('Histórico Médico', validators=[Optional()])
    queixas = TextAreaField('Queixas Principais', validators=[Optional()])
    medicamentos_atuais = TextAreaField('Medicamentos Atuais', validators=[Optional()])
    alergias_novas = TextAreaField('Alergias', validators=[Optional()])
    observacoes = TextAreaField('Observações Adicionais', validators=[Optional()])
    submit = SubmitField('Enviar')

class BuscaPacienteForm(FlaskForm):
    termo = StringField('Buscar Paciente (nome ou CPF)', validators=[DataRequired(message='Campo obrigatório')])
    submit = SubmitField('Buscar')

class RadiografiaForm(FlaskForm):
    paciente_id = HiddenField('ID do Paciente')
    nome_arquivo = StringField('Nome/Identificação da Radiografia', validators=[DataRequired(message='Campo obrigatório')])
    descricao = TextAreaField('Descrição', validators=[Optional()])
    submit = SubmitField('Salvar')
