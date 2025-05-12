from flask import render_template, redirect, url_for, flash, request, abort, jsonify, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, date, timedelta
import secrets
import re
import os
import uuid
from app import db
from app.models import Usuario, Paciente, Evolucao, Radiografia, Agendamento, FormularioPreConsulta, FormularioPrimeiraConsulta
from app.forms import (LoginForm, UsuarioForm, PacienteForm, EvolucaoForm, AgendamentoForm, 
                      FormularioPreConsultaForm, PreenchimentoFormularioForm, BuscaPacienteForm,
                      RadiografiaForm, FormularioPrimeiraConsultaForm)
from app.notifications import send_formulario_email, send_lembrete_consulta_sms

# Configuração para uploads de arquivos
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads/radiografias')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_radiografia_file(file):
    """Salva o arquivo de radiografia e retorna o caminho relativo"""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
    # Gera um nome único para o arquivo para evitar conflitos
    original_filename = secure_filename(file.filename)
    file_extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
    
    # Caminho completo do arquivo no servidor
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    
    # Salva o arquivo
    file.save(file_path)
    
    # Retorna o caminho relativo para armazenar no banco de dados
    return f"uploads/radiografias/{unique_filename}"

def register_routes(app):
    
    @app.context_processor
    def utility_processor():
        def format_date(dt):
            if not dt:
                return ""
            if isinstance(dt, str):
                try:
                    dt = datetime.strptime(dt, '%Y-%m-%d').date()
                except ValueError:
                    return dt
            return dt.strftime('%d/%m/%Y') if dt else ""
        
        def format_datetime(dt):
            if not dt:
                return ""
            return dt.strftime('%d/%m/%Y %H:%M') if dt else ""
        
        def date_offset(dt, days=0):
            if isinstance(dt, date):
                return dt + timedelta(days=days)
            return dt
        
        def nl2br(text):
            if not text:
                return ""
            return text.replace('\n', '<br>')
            
        return dict(
            format_date=format_date, 
            format_datetime=format_datetime,
            date_offset=date_offset,
            nl2br=nl2br
        )

    # Index/Login route
    @app.route('/', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = LoginForm()
        if form.validate_on_submit():
            user = Usuario.query.filter_by(username=form.username.data).first()
            if user and check_password_hash(user.password_hash, form.password.data):
                login_user(user, remember=form.remember.data)
                user.ultimo_acesso = datetime.now()
                db.session.commit()
                
                next_page = request.args.get('next')
                return redirect(next_page or url_for('dashboard'))
            else:
                flash('Login inválido. Verifique seu usuário e senha.', 'danger')
    
        return render_template('login.html', form=form, title='Login')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Você foi desconectado com sucesso.', 'info')
        return redirect(url_for('login'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        # Count stats for dashboard
        total_pacientes = Paciente.query.count()
        agendamentos_hoje = Agendamento.query.filter(
            Agendamento.data_consulta == date.today(),
            Agendamento.status == 'agendada'
        ).count()
        agendamentos_pendentes = Agendamento.query.filter(
            Agendamento.data_consulta >= date.today(),
            Agendamento.status == 'agendada'
        ).count()
        
        # Recent appointments
        proximos_agendamentos = Agendamento.query.filter(
            Agendamento.data_consulta >= date.today(),
            Agendamento.status == 'agendada'
        ).order_by(Agendamento.data_consulta, Agendamento.hora_consulta).limit(5).all()
        
        # Recent patients
        pacientes_recentes = Paciente.query.order_by(Paciente.data_cadastro.desc()).limit(5).all()
        
        return render_template('dashboard.html', 
                              title='Dashboard',
                              total_pacientes=total_pacientes,
                              agendamentos_hoje=agendamentos_hoje,
                              agendamentos_pendentes=agendamentos_pendentes,
                              proximos_agendamentos=proximos_agendamentos,
                              pacientes_recentes=pacientes_recentes)

    # Patients Routes
    @app.route('/pacientes')
    @login_required
    def listar_pacientes():
        page = request.args.get('page', 1, type=int)
        busca = request.args.get('busca', '')
        
        form = BuscaPacienteForm()
        
        if busca:
            # Search by name or CPF
            pacientes = Paciente.query.filter(
                (Paciente.nome.ilike(f'%{busca}%') | 
                 Paciente.cpf.ilike(f'%{busca}%'))
            ).order_by(Paciente.nome).paginate(page=page, per_page=10)
        else:
            pacientes = Paciente.query.order_by(Paciente.nome).paginate(page=page, per_page=10)
        
        return render_template('pacientes/lista.html', 
                              pacientes=pacientes, 
                              form=form, 
                              busca=busca,
                              title='Pacientes')

    @app.route('/pacientes/cadastro', methods=['GET', 'POST'])
    @login_required
    def cadastrar_paciente():
        form = PacienteForm()
        
        if form.validate_on_submit():
            # Check if CPF is already registered
            if form.cpf.data and Paciente.query.filter_by(cpf=form.cpf.data).first():
                flash('CPF já cadastrado no sistema.', 'danger')
                return render_template('pacientes/cadastro.html', form=form, title='Novo Paciente')
            
            paciente = Paciente(
                nome=form.nome.data,
                nascimento=form.nascimento.data,
                telefone=form.telefone.data,
                endereco=form.endereco.data,
                cpf=form.cpf.data,
                genero=form.genero.data,
                doencas=form.doencas.data,
                medicamentos=form.medicamentos.data,
                alergias=form.alergias.data,
                cirurgias=form.cirurgias.data,
                habitos=form.habitos.data,
                observacoes=form.observacoes.data
            )
            
            db.session.add(paciente)
            db.session.commit()
            
            flash(f'Paciente {paciente.nome} cadastrado com sucesso!', 'success')
            return redirect(url_for('detalhe_paciente', paciente_id=paciente.id))
        
        return render_template('pacientes/cadastro.html', form=form, title='Novo Paciente')

    @app.route('/pacientes/<int:paciente_id>')
    @login_required
    def detalhe_paciente(paciente_id):
        paciente = Paciente.query.get_or_404(paciente_id)
        
        # Get latest 5 evolutions
        evolucoes = paciente.evolucoes.order_by(Evolucao.data.desc()).limit(5).all()
        
        # Get future appointments
        proximos_agendamentos = paciente.agendamentos.filter(
            Agendamento.data_consulta >= date.today(),
            Agendamento.status == 'agendada'
        ).order_by(Agendamento.data_consulta).all()
        
        # Get radiographs
        radiografias = paciente.radiografias.order_by(Radiografia.data_upload.desc()).all()
        
        return render_template('pacientes/detalhes.html', 
                              paciente=paciente, 
                              evolucoes=evolucoes,
                              proximos_agendamentos=proximos_agendamentos,
                              radiografias=radiografias,
                              title=f'Paciente - {paciente.nome}')

    @app.route('/pacientes/<int:paciente_id>/editar', methods=['GET', 'POST'])
    @login_required
    def editar_paciente(paciente_id):
        paciente = Paciente.query.get_or_404(paciente_id)
        form = PacienteForm(obj=paciente)
        
        if form.validate_on_submit():
            # Check if CPF exists but is not from this patient
            if form.cpf.data and form.cpf.data != paciente.cpf:
                existing = Paciente.query.filter_by(cpf=form.cpf.data).first()
                if existing and existing.id != paciente_id:
                    flash('CPF já cadastrado para outro paciente.', 'danger')
                    return render_template('pacientes/editar.html', 
                                          form=form, 
                                          paciente=paciente,
                                          title=f'Editar Paciente - {paciente.nome}')
            
            # Update patient data
            form.populate_obj(paciente)
            db.session.commit()
            
            flash('Dados do paciente atualizados com sucesso!', 'success')
            return redirect(url_for('detalhe_paciente', paciente_id=paciente.id))
        
        return render_template('pacientes/editar.html', 
                              form=form, 
                              paciente=paciente,
                              title=f'Editar Paciente - {paciente.nome}')

    # Evolution routes
    @app.route('/pacientes/<int:paciente_id>/evolucoes')
    @login_required
    def listar_evolucoes(paciente_id):
        paciente = Paciente.query.get_or_404(paciente_id)
        evolucoes = paciente.evolucoes.order_by(Evolucao.data.desc()).all()
        
        return render_template('evolucoes/lista.html', 
                              paciente=paciente, 
                              evolucoes=evolucoes,
                              title=f'Evolução - {paciente.nome}')

    @app.route('/pacientes/<int:paciente_id>/evolucoes/nova', methods=['GET', 'POST'])
    @login_required
    def nova_evolucao(paciente_id):
        paciente = Paciente.query.get_or_404(paciente_id)
        form = EvolucaoForm()
        
        if form.validate_on_submit():
            evolucao = Evolucao(
                paciente_id=paciente_id,
                data=form.data_evolucao.data,
                procedimento=form.procedimento.data,
                supervisor=form.supervisor.data,
                observacao=form.observacao.data,
                detalhes=form.detalhes.data
            )
            
            db.session.add(evolucao)
            db.session.commit()
            
            flash('Evolução registrada com sucesso!', 'success')
            return redirect(url_for('listar_evolucoes', paciente_id=paciente_id))
        
        return render_template('evolucoes/nova.html', 
                              form=form, 
                              paciente=paciente,
                              title=f'Nova Evolução - {paciente.nome}')

    @app.route('/evolucoes/<int:evolucao_id>/editar', methods=['GET', 'POST'])
    @login_required
    def editar_evolucao(evolucao_id):
        evolucao = Evolucao.query.get_or_404(evolucao_id)
        paciente = evolucao.paciente
        form = EvolucaoForm(obj=evolucao)
        
        if form.validate_on_submit():
            form.populate_obj(evolucao)
            db.session.commit()
            
            flash('Evolução atualizada com sucesso!', 'success')
            return redirect(url_for('listar_evolucoes', paciente_id=paciente.id))
        
        return render_template('evolucoes/editar.html', 
                              form=form, 
                              evolucao=evolucao,
                              paciente=paciente,
                              title=f'Editar Evolução - {paciente.nome}')

    # Appointments routes
    @app.route('/agendamentos')
    @login_required
    def listar_agendamentos():
        data_filtro = request.args.get('data')
        if data_filtro:
            try:
                data_filtro = datetime.strptime(data_filtro, '%Y-%m-%d').date()
            except ValueError:
                data_filtro = date.today()
        else:
            data_filtro = date.today()
        
        # Get appointments for the selected date
        agendamentos = Agendamento.query.filter(
            Agendamento.data_consulta == data_filtro
        ).order_by(Agendamento.hora_consulta).all()
        
        return render_template('agendamentos/lista.html', 
                              agendamentos=agendamentos,
                              data_atual=data_filtro,
                              title='Agenda')

    @app.route('/pacientes/<int:paciente_id>/agendamentos/novo', methods=['GET', 'POST'])
    @login_required
    def novo_agendamento(paciente_id):
        paciente = Paciente.query.get_or_404(paciente_id)
        form = AgendamentoForm()
        
        if form.validate_on_submit():
            agendamento = Agendamento(
                paciente_id=paciente_id,
                data_consulta=form.data_consulta.data,
                hora_consulta=form.hora_consulta.data,
                tipo_consulta=form.tipo_consulta.data,
                observacao=form.observacao.data,
                status=form.status.data
            )
            
            db.session.add(agendamento)
            db.session.commit()
            
            # Send SMS notification if phone number is available
            if paciente.telefone:
                data_formatada = agendamento.data_consulta.strftime('%d/%m/%Y')
                send_lembrete_consulta_sms(
                    paciente.telefone, 
                    paciente.nome.split()[0],  # First name
                    data_formatada, 
                    agendamento.hora_consulta
                )
            
            flash('Agendamento criado com sucesso!', 'success')
            return redirect(url_for('detalhe_paciente', paciente_id=paciente_id))
        
        return render_template('agendamentos/novo.html', 
                              form=form, 
                              paciente=paciente,
                              title=f'Novo Agendamento - {paciente.nome}')

    @app.route('/agendamentos/<int:agendamento_id>/editar', methods=['GET', 'POST'])
    @login_required
    def editar_agendamento(agendamento_id):
        agendamento = Agendamento.query.get_or_404(agendamento_id)
        paciente = agendamento.paciente
        form = AgendamentoForm(obj=agendamento)
        
        if form.validate_on_submit():
            old_status = agendamento.status
            form.populate_obj(agendamento)
            db.session.commit()
            
            # If status changed to concluded
            if old_status != 'concluida' and agendamento.status == 'concluida':
                flash('Agendamento marcado como concluído!', 'success')
            else:
                flash('Agendamento atualizado com sucesso!', 'success')
            
            # Send SMS reminder if date changed and status is still scheduled
            if agendamento.status == 'agendada' and paciente.telefone:
                data_formatada = agendamento.data_consulta.strftime('%d/%m/%Y')
                send_lembrete_consulta_sms(
                    paciente.telefone, 
                    paciente.nome.split()[0],  # First name
                    data_formatada, 
                    agendamento.hora_consulta
                )
            
            return redirect(url_for('listar_agendamentos', data=agendamento.data_consulta.strftime('%Y-%m-%d')))
        
        return render_template('agendamentos/editar.html', 
                              form=form, 
                              agendamento=agendamento,
                              paciente=paciente,
                              title=f'Editar Agendamento - {paciente.nome}')

    # Pre-consultation form routes
    @app.route('/formularios')
    @login_required
    def listar_formularios():
        page = request.args.get('page', 1, type=int)
        tipo = request.args.get('tipo', 'pendente')
        
        if tipo == 'pendente':
            formularios = FormularioPreConsulta.query.filter_by(status='pendente').order_by(FormularioPreConsulta.data_envio.desc())
        elif tipo == 'preenchido':
            formularios = FormularioPreConsulta.query.filter_by(status='preenchido').order_by(FormularioPreConsulta.data_preenchimento.desc())
        else:
            formularios = FormularioPreConsulta.query.order_by(FormularioPreConsulta.data_envio.desc())
        
        formularios = formularios.paginate(page=page, per_page=10)
        
        return render_template('formularios/lista.html', 
                              formularios=formularios,
                              tipo=tipo,
                              title='Formulários de Pré-Consulta')

    @app.route('/formularios/<int:formulario_id>')
    @login_required
    def detalhe_formulario(formulario_id):
        formulario = FormularioPreConsulta.query.get_or_404(formulario_id)
        return render_template('formularios/detalhe.html', 
                              formulario=formulario,
                              title='Detalhes do Formulário')

    @app.route('/pacientes/anamnese')
    @login_required
    def listar_pacientes_anamnese():
        page = request.args.get('page', 1, type=int)
        busca = request.args.get('busca', '')
        
        form = BuscaPacienteForm()
        
        if busca:
            # Search by name or CPF
            pacientes = Paciente.query.filter(
                (Paciente.nome.ilike(f'%{busca}%') | 
                 Paciente.cpf.ilike(f'%{busca}%'))
            ).order_by(Paciente.nome).paginate(page=page, per_page=10)
        else:
            pacientes = Paciente.query.order_by(Paciente.nome).paginate(page=page, per_page=10)
        
        return render_template('formularios/enviar.html', 
                              pacientes=pacientes, 
                              form=form, 
                              busca=busca,
                              title='Enviar Formulário de Anamnese')

    @app.route('/pacientes/<int:paciente_id>/enviar-anamnese', methods=['GET', 'POST'])
    @login_required
    def enviar_anamnese(paciente_id):
        paciente = Paciente.query.get_or_404(paciente_id)
        
        # Check if patient has email
        if not paciente.email:
            flash('Este paciente não possui e-mail cadastrado.', 'danger')
            return redirect(url_for('listar_pacientes_anamnese'))
        
        # Get upcoming appointments for this patient
        proximos_agendamentos = paciente.agendamentos.filter(
            Agendamento.data_consulta >= date.today(),
            Agendamento.status == 'agendada'
        ).order_by(Agendamento.data_consulta).all()
        
        if request.method == 'POST':
            agendamento_id = request.form.get('agendamento_id', None)
            
            # Create form record
            formulario = FormularioPreConsulta(
                paciente_id=paciente_id,
                agendamento_id=agendamento_id if agendamento_id else None,
                status='pendente'
            )
            
            db.session.add(formulario)
            db.session.commit()
            
            # Generate token URL
            token_url = url_for('preencher_formulario', token=formulario.token, _external=True)
            
            # Send email
            if send_formulario_email(paciente.nome, paciente.email, token_url):
                flash('Formulário enviado com sucesso para o e-mail do paciente!', 'success')
            else:
                flash('Erro ao enviar e-mail. Formulário criado, mas o paciente não foi notificado.', 'warning')
            
            return redirect(url_for('listar_formularios'))
        
        return render_template('formularios/confirmar_envio.html',
                              paciente=paciente,
                              proximos_agendamentos=proximos_agendamentos,
                              title=f'Enviar Anamnese - {paciente.nome}')

    @app.route('/formulario/<token>', methods=['GET', 'POST'])
    def preencher_formulario(token):
        formulario = FormularioPreConsulta.query.filter_by(token=token).first_or_404()
        
        # Check if form is already filled
        if formulario.status == 'preenchido':
            flash('Este formulário já foi preenchido.', 'info')
            return render_template('formularios/ja_preenchido.html', title='Formulário Já Preenchido')
        
        # Check if form is expired (7 days after sending)
        if formulario.data_envio < datetime.now() - timedelta(days=7):
            formulario.status = 'expirado'
            db.session.commit()
            flash('Este formulário expirou. Por favor, entre em contato com a clínica.', 'warning')
            return render_template('formularios/expirado.html', title='Formulário Expirado')
        
        paciente = formulario.paciente
        form = PreenchimentoFormularioForm()
        
        # Pre-fill form with existing patient data
        if request.method == 'GET':
            form.historico_medico.data = paciente.doencas
            form.medicamentos_atuais.data = paciente.medicamentos
            form.alergias_novas.data = paciente.alergias
        
        if form.validate_on_submit():
            formulario.historico_medico = form.historico_medico.data
            formulario.queixas = form.queixas.data
            formulario.medicamentos_atuais = form.medicamentos_atuais.data
            formulario.alergias_novas = form.alergias_novas.data
            formulario.observacoes = form.observacoes.data
            formulario.status = 'preenchido'
            formulario.data_preenchimento = datetime.now()
            
            # Update patient data
            paciente.doencas = form.historico_medico.data
            paciente.medicamentos = form.medicamentos_atuais.data
            paciente.alergias = form.alergias_novas.data
            
            db.session.commit()
            
            flash('Formulário preenchido com sucesso! Obrigado.', 'success')
            return render_template('formularios/sucesso.html', title='Formulário Enviado')
        
        return render_template('formularios/preencher.html',
                              form=form,
                              paciente=paciente,
                              formulario=formulario,
                              title='Formulário de Pré-Consulta')

    # Radiography routes
    @app.route('/pacientes/<int:paciente_id>/radiografias')
    @login_required
    def listar_radiografias(paciente_id):
        paciente = Paciente.query.get_or_404(paciente_id)
        radiografias = paciente.radiografias.order_by(Radiografia.data_upload.desc()).all()
        
        return render_template('radiografias/lista.html',
                              paciente=paciente,
                              radiografias=radiografias,
                              title=f'Radiografias - {paciente.nome}')

    @app.route('/pacientes/<int:paciente_id>/radiografias/nova', methods=['GET', 'POST'])
    @login_required
    def nova_radiografia(paciente_id):
        paciente = Paciente.query.get_or_404(paciente_id)
        form = RadiografiaForm()
        
        if form.validate_on_submit():
            arquivo = form.arquivo.data
            
            if arquivo and allowed_file(arquivo.filename):
                # Processar o upload do arquivo
                arquivo_caminho = save_radiografia_file(arquivo)
                
                radiografia = Radiografia(
                    paciente_id=paciente_id,
                    nome_arquivo=form.nome_arquivo.data,
                    descricao=form.descricao.data,
                    arquivo_caminho=arquivo_caminho,
                    arquivo_nome_original=secure_filename(arquivo.filename),
                    arquivo_tipo=arquivo.content_type,
                    arquivo_tamanho=arquivo.content_length if hasattr(arquivo, 'content_length') else 0
                )
                
                db.session.add(radiografia)
                db.session.commit()
                
                flash('Radiografia registrada com sucesso!', 'success')
                return redirect(url_for('listar_radiografias', paciente_id=paciente_id))
            else:
                flash('O tipo de arquivo não é permitido. Use uma imagem ou PDF.', 'danger')
        
        return render_template('radiografias/nova.html',
                              form=form,
                              paciente=paciente,
                              allowed_extensions=", ".join(ALLOWED_EXTENSIONS),
                              title=f'Nova Radiografia - {paciente.nome}')

    @app.route('/radiografias/<int:radiografia_id>/editar', methods=['GET', 'POST'])
    @login_required
    def editar_radiografia(radiografia_id):
        radiografia = Radiografia.query.get_or_404(radiografia_id)
        paciente = radiografia.paciente
        form = RadiografiaForm(obj=radiografia)
        
        if form.validate_on_submit():
            # Atualizar campos básicos
            radiografia.nome_arquivo = form.nome_arquivo.data
            radiografia.descricao = form.descricao.data
            
            # Verificar se um novo arquivo foi enviado
            if form.arquivo.data:
                arquivo = form.arquivo.data
                if allowed_file(arquivo.filename):
                    # Processar o upload do novo arquivo
                    arquivo_caminho = save_radiografia_file(arquivo)
                    
                    radiografia.arquivo_caminho = arquivo_caminho
                    radiografia.arquivo_nome_original = secure_filename(arquivo.filename)
                    radiografia.arquivo_tipo = arquivo.content_type
                    radiografia.arquivo_tamanho = arquivo.content_length if hasattr(arquivo, 'content_length') else 0
                else:
                    flash('O tipo de arquivo não é permitido. Use uma imagem ou PDF.', 'danger')
                    return render_template('radiografias/editar.html',
                                        form=form,
                                        radiografia=radiografia,
                                        paciente=paciente,
                                        allowed_extensions=", ".join(ALLOWED_EXTENSIONS),
                                        title=f'Editar Radiografia - {paciente.nome}')
            
            db.session.commit()
            
            flash('Radiografia atualizada com sucesso!', 'success')
            return redirect(url_for('listar_radiografias', paciente_id=paciente.id))
        
        return render_template('radiografias/editar.html',
                              form=form,
                              radiografia=radiografia,
                              paciente=paciente,
                              allowed_extensions=", ".join(ALLOWED_EXTENSIONS),
                              title=f'Editar Radiografia - {paciente.nome}')
    
    @app.route('/radiografias/<int:radiografia_id>/visualizar')
    @login_required
    def visualizar_radiografia(radiografia_id):
        """Rota para visualizar/exibir a radiografia"""
        radiografia = Radiografia.query.get_or_404(radiografia_id)
        
        if not radiografia.arquivo_caminho:
            flash('Esta radiografia não possui arquivo associado.', 'warning')
            return redirect(url_for('listar_radiografias', paciente_id=radiografia.paciente_id))
        
        # Caminho completo para o arquivo
        caminho_completo = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', radiografia.arquivo_caminho)
        
        # Verificar se o arquivo existe
        if not os.path.exists(caminho_completo):
            flash('O arquivo desta radiografia não foi encontrado.', 'danger')
            return redirect(url_for('listar_radiografias', paciente_id=radiografia.paciente_id))
        
        return render_template('radiografias/visualizar.html',
                              radiografia=radiografia,
                              paciente=radiografia.paciente,
                              title=f'Visualizar Radiografia - {radiografia.nome_arquivo}')
    
    @app.route('/radiografias/<int:radiografia_id>/download')
    @login_required
    def download_radiografia(radiografia_id):
        """Rota para download da radiografia"""
        radiografia = Radiografia.query.get_or_404(radiografia_id)
        
        if not radiografia.arquivo_caminho:
            flash('Esta radiografia não possui arquivo associado.', 'warning')
            return redirect(url_for('listar_radiografias', paciente_id=radiografia.paciente_id))
        
        # Extrair diretório e nome do arquivo
        diretorio = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 
                               os.path.dirname(radiografia.arquivo_caminho))
        nome_arquivo = os.path.basename(radiografia.arquivo_caminho)
        
        # Verificar se o arquivo existe
        caminho_completo = os.path.join(diretorio, nome_arquivo)
        if not os.path.exists(caminho_completo):
            flash('O arquivo desta radiografia não foi encontrado.', 'danger')
            return redirect(url_for('listar_radiografias', paciente_id=radiografia.paciente_id))
        
        # Nome para download (pode usar o nome original ou outro de sua escolha)
        nome_download = radiografia.arquivo_nome_original or f"radiografia_{radiografia.id}{os.path.splitext(nome_arquivo)[1]}"
        
        return send_from_directory(
            directory=diretorio,
            path=nome_arquivo,
            download_name=nome_download,
            as_attachment=True
        )

    # Formulário de Primeira Consulta
    @app.route('/primeira-consulta', methods=['GET', 'POST'])
    def criar_formulario_primeira_consulta():
        """Cria um novo formulário de primeira consulta e retorna o token/link"""
        # Criando um novo formulário
        formulario = FormularioPrimeiraConsulta(
            status='pendente'
        )
        
        db.session.add(formulario)
        db.session.commit()
        
        # Gerando o URL para preenchimento
        token_url = url_for('preencher_formulario_primeira_consulta', token=formulario.token, _external=True)
        
        return render_template('formularios/primeira_consulta_criado.html',
                              token_url=token_url,
                              title='Formulário de Primeira Consulta')
    
    @app.route('/primeira-consulta/<token>', methods=['GET', 'POST'])
    def preencher_formulario_primeira_consulta(token):
        """Permite ao paciente preencher um formulário de primeira consulta através de um token"""
        # Buscar o formulário pelo token
        formulario = FormularioPrimeiraConsulta.query.filter_by(token=token).first_or_404()
        
        # Verificar se já foi preenchido
        if formulario.status == 'preenchido':
            flash('Este formulário já foi preenchido. Obrigado!', 'info')
            return render_template('formularios/formulario_ja_preenchido.html', title='Formulário já preenchido')
        
        form = FormularioPrimeiraConsultaForm()
        
        if form.validate_on_submit():
            # Atualizar os dados do formulário
            form.populate_obj(formulario)
            formulario.status = 'preenchido'
            formulario.data_preenchimento = datetime.now()
            
            db.session.commit()
            
            flash('Formulário preenchido com sucesso! Em breve entraremos em contato.', 'success')
            return render_template('formularios/primeira_consulta_concluido.html', title='Formulário Enviado')
            
        return render_template('formularios/preencher_primeira_consulta.html',
                              form=form,
                              title='Formulário de Primeira Consulta')
    
    @app.route('/admin/formularios-primeira-consulta')
    @login_required
    def listar_formularios_primeira_consulta():
        """Lista todos os formulários de primeira consulta"""
        if current_user.tipo != 'admin' and current_user.tipo != 'dentista':
            flash('Acesso restrito.', 'danger')
            return redirect(url_for('dashboard'))
            
        # Paginação
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        # Filtro por status
        status_filtro = request.args.get('status', '')
        
        # Query base
        query = FormularioPrimeiraConsulta.query
        
        # Aplicar filtro se existir
        if status_filtro:
            query = query.filter_by(status=status_filtro)
            
        # Ordenar por data de preenchimento (mais recentes primeiro)
        formularios = query.order_by(FormularioPrimeiraConsulta.data_criacao.desc()).paginate(page=page, per_page=per_page)
        
        return render_template('formularios/listar_primeira_consulta.html',
                              formularios=formularios,
                              status_filtro=status_filtro,
                              title='Formulários de Primeira Consulta')
    
    @app.route('/admin/formularios-primeira-consulta/<int:formulario_id>')
    @login_required
    def detalhe_formulario_primeira_consulta(formulario_id):
        """Exibe os detalhes de um formulário de primeira consulta"""
        if current_user.tipo != 'admin' and current_user.tipo != 'dentista':
            flash('Acesso restrito.', 'danger')
            return redirect(url_for('dashboard'))
            
        formulario = FormularioPrimeiraConsulta.query.get_or_404(formulario_id)
        
        return render_template('formularios/detalhe_primeira_consulta.html',
                              formulario=formulario,
                              title=f'Formulário - {formulario.nome or "Sem nome"}')
    
    @app.route('/admin/formularios-primeira-consulta/<int:formulario_id>/criar-paciente', methods=['GET', 'POST'])
    @login_required
    def criar_paciente_de_formulario(formulario_id):
        """Cria um novo paciente a partir de um formulário de primeira consulta"""
        if current_user.tipo != 'admin' and current_user.tipo != 'dentista':
            flash('Acesso restrito.', 'danger')
            return redirect(url_for('dashboard'))
            
        formulario = FormularioPrimeiraConsulta.query.get_or_404(formulario_id)
        
        # Verificar se o formulário foi preenchido
        if formulario.status != 'preenchido':
            flash('Este formulário ainda não foi preenchido pelo paciente.', 'warning')
            return redirect(url_for('detalhe_formulario_primeira_consulta', formulario_id=formulario_id))
        
        # Pré-preencher o formulário de paciente com os dados do formulário de primeira consulta
        form = PacienteForm(obj=formulario)
        
        if form.validate_on_submit():
            # Criar o novo paciente
            paciente = Paciente(
                nome=form.nome.data,
                nascimento=form.nascimento.data,
                telefone=form.telefone.data,
                email=form.email.data,
                endereco=form.endereco.data,
                cpf=form.cpf.data,
                genero=form.genero.data,
                doencas=form.doencas.data,
                medicamentos=form.medicamentos.data,
                alergias=form.alergias.data,
                cirurgias=form.cirurgias.data,
                habitos=form.habitos.data,
                observacoes=form.observacoes.data
            )
            
            db.session.add(paciente)
            db.session.commit()
            
            flash(f'Paciente {paciente.nome} criado com sucesso!', 'success')
            return redirect(url_for('detalhe_paciente', paciente_id=paciente.id))
        
        return render_template('formularios/criar_paciente_de_formulario.html',
                              form=form,
                              formulario=formulario,
                              title='Criar Paciente')
    
    # Admin routes
    @app.route('/admin/usuarios')
    @login_required
    def listar_usuarios():
        if current_user.tipo != 'admin':
            flash('Acesso restrito para administradores.', 'danger')
            return redirect(url_for('dashboard'))
        
        usuarios = Usuario.query.order_by(Usuario.nome).all()
        
        return render_template('admin/usuarios.html',
                              usuarios=usuarios,
                              title='Gerenciar Usuários')

    @app.route('/admin/usuarios/novo', methods=['GET', 'POST'])
    @login_required
    def novo_usuario():
        if current_user.tipo != 'admin':
            flash('Acesso restrito para administradores.', 'danger')
            return redirect(url_for('dashboard'))
        
        form = UsuarioForm()
        
        if form.validate_on_submit():
            # Check if username or email already exists
            if Usuario.query.filter_by(username=form.username.data).first():
                flash('Nome de usuário já existe.', 'danger')
                return render_template('admin/novo_usuario.html', form=form, title='Novo Usuário')
            
            if Usuario.query.filter_by(email=form.email.data).first():
                flash('E-mail já cadastrado.', 'danger')
                return render_template('admin/novo_usuario.html', form=form, title='Novo Usuário')
            
            usuario = Usuario(
                nome=form.nome.data,
                username=form.username.data,
                email=form.email.data,
                password_hash=generate_password_hash(form.password.data),
                tipo=form.tipo.data,
                ativo=form.ativo.data
            )
            
            db.session.add(usuario)
            db.session.commit()
            
            flash(f'Usuário {usuario.nome} criado com sucesso!', 'success')
            return redirect(url_for('listar_usuarios'))
        
        return render_template('admin/novo_usuario.html',
                              form=form,
                              title='Novo Usuário')

    @app.route('/admin/usuarios/<int:usuario_id>/editar', methods=['GET', 'POST'])
    @login_required
    def editar_usuario(usuario_id):
        if current_user.tipo != 'admin':
            flash('Acesso restrito para administradores.', 'danger')
            return redirect(url_for('dashboard'))
        
        usuario = Usuario.query.get_or_404(usuario_id)
        
        # Cannot edit own account type (to prevent locking self out of admin)
        if usuario.id == current_user.id:
            flash('Você não pode editar seu próprio tipo de conta.', 'warning')
            return redirect(url_for('listar_usuarios'))
        
        form = UsuarioForm(obj=usuario)
        
        # Remove password requirement for editing
        form.password.validators = []
        form.confirm_password.validators = []
        
        if form.validate_on_submit():
            # Check if username exists but is not for this user
            if form.username.data != usuario.username:
                existing = Usuario.query.filter_by(username=form.username.data).first()
                if existing:
                    flash('Nome de usuário já existe.', 'danger')
                    return render_template('admin/editar_usuario.html', form=form, usuario=usuario, title='Editar Usuário')
            
            # Check if email exists but is not for this user
            if form.email.data != usuario.email:
                existing = Usuario.query.filter_by(email=form.email.data).first()
                if existing:
                    flash('E-mail já cadastrado.', 'danger')
                    return render_template('admin/editar_usuario.html', form=form, usuario=usuario, title='Editar Usuário')
            
            usuario.nome = form.nome.data
            usuario.username = form.username.data
            usuario.email = form.email.data
            usuario.tipo = form.tipo.data
            usuario.ativo = form.ativo.data
            
            # Update password only if provided
            if form.password.data:
                usuario.password_hash = generate_password_hash(form.password.data)
            
            db.session.commit()
            
            flash(f'Usuário {usuario.nome} atualizado com sucesso!', 'success')
            return redirect(url_for('listar_usuarios'))
        
        return render_template('admin/editar_usuario.html',
                              form=form,
                              usuario=usuario,
                              title='Editar Usuário')
