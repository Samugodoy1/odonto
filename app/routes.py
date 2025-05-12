from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
import secrets
from app import db
from app.models import Usuario, Paciente, Evolucao, Radiografia, Agendamento, FormularioPreConsulta
from app.forms import (LoginForm, UsuarioForm, PacienteForm, EvolucaoForm, AgendamentoForm, 
                      FormularioPreConsultaForm, PreenchimentoFormularioForm, BuscaPacienteForm,
                      RadiografiaForm)

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
        
        return render_template('pacientes/detalhes.html', 
                              paciente=paciente, 
                              evolucoes=evolucoes,
                              proximos_agendamentos=proximos_agendamentos,
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
                data=form.data.data,
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
            
            flash('Consulta agendada com sucesso!', 'success')
            return redirect(url_for('listar_agendamentos'))
        
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
            form.populate_obj(agendamento)
            db.session.commit()
            
            flash('Agendamento atualizado com sucesso!', 'success')
            return redirect(url_for('listar_agendamentos'))
        
        return render_template('agendamentos/editar.html', 
                              form=form, 
                              agendamento=agendamento,
                              paciente=paciente,
                              title=f'Editar Agendamento - {paciente.nome}')

    @app.route('/agendamentos/<int:agendamento_id>/status/<status>')
    @login_required
    def alterar_status_agendamento(agendamento_id, status):
        agendamento = Agendamento.query.get_or_404(agendamento_id)
        
        if status in ['agendada', 'concluida', 'cancelada', 'faltou']:
            agendamento.status = status
            db.session.commit()
            flash('Status do agendamento atualizado.', 'success')
        
        return redirect(url_for('listar_agendamentos'))

    # Radiograph routes
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
            radiografia = Radiografia(
                paciente_id=paciente_id,
                nome_arquivo=form.nome_arquivo.data,
                descricao=form.descricao.data
            )
            
            db.session.add(radiografia)
            db.session.commit()
            
            flash('Radiografia registrada com sucesso!', 'success')
            return redirect(url_for('listar_radiografias', paciente_id=paciente_id))
        
        return render_template('radiografias/nova.html', 
                              form=form, 
                              paciente=paciente,
                              title=f'Nova Radiografia - {paciente.nome}')

    # Pre-consultation forms
    @app.route('/formularios')
    @login_required
    def listar_formularios():
        form = BuscaPacienteForm()
        status = request.args.get('status', 'pendente')
        
        # Filtrar por status se especificado
        if status in ['pendente', 'preenchido', 'expirado']:
            formularios = FormularioPreConsulta.query.filter_by(status=status).order_by(FormularioPreConsulta.data_envio.desc()).all()
        else:
            formularios = FormularioPreConsulta.query.order_by(FormularioPreConsulta.data_envio.desc()).all()
        
        return render_template('formularios/lista.html', 
                              formularios=formularios,
                              form=form,
                              status_atual=status,
                              title='Formulários de Pré-Consulta')

    @app.route('/pacientes/<int:paciente_id>/formularios/novo', methods=['GET', 'POST'])
    @login_required
    def novo_formulario(paciente_id):
        paciente = Paciente.query.get_or_404(paciente_id)
        form = FormularioPreConsultaForm()
        
        # Get patient's appointments for dropdown
        agendamentos = paciente.agendamentos.filter(
            Agendamento.data_consulta >= date.today(),
            Agendamento.status == 'agendada'
        ).order_by(Agendamento.data_consulta).all()
        
        # Prepare choices for form dropdown
        form.agendamento_id.choices = [(str(a.id), f'{a.data_consulta.strftime("%d/%m/%Y")} - {a.hora_consulta} - {a.tipo_consulta}') 
                                    for a in agendamentos]
        form.agendamento_id.choices.insert(0, ('0', 'Selecione um agendamento (opcional)'))
        
        if form.validate_on_submit():
            formulario = FormularioPreConsulta(
                paciente_id=paciente_id,
                agendamento_id=int(form.agendamento_id.data) if form.agendamento_id.data != '0' else None,
                token=secrets.token_urlsafe(32),
                status='pendente'
            )
            
            db.session.add(formulario)
            db.session.commit()
            
            flash('Formulário de pré-consulta criado com sucesso!', 'success')
            
            # Redirect to the send form page
            return redirect(url_for('enviar_formulario', formulario_id=formulario.id))
        
        return render_template('formularios/novo.html', 
                              form=form, 
                              paciente=paciente,
                              agendamentos=agendamentos,
                              title=f'Novo Formulário - {paciente.nome}')

    @app.route('/formularios/<int:formulario_id>/enviar', methods=['GET'])
    @login_required
    def enviar_formulario(formulario_id):
        formulario = FormularioPreConsulta.query.get_or_404(formulario_id)
        
        # Se o formulário já foi preenchido, redirecionar para a página de listagem
        if formulario.status == 'preenchido':
            flash('Este formulário já foi preenchido pelo paciente.', 'info')
            return redirect(url_for('listar_formularios'))
        
        return render_template('formularios/enviar.html', 
                              formulario=formulario,
                              title=f'Enviar Formulário - {formulario.paciente.nome}')
    
    @app.route('/formularios/<token>', methods=['GET', 'POST'])
    def preencher_formulario(token):
        formulario = FormularioPreConsulta.query.filter_by(token=token).first_or_404()
        
        # Check if already filled
        if formulario.status == 'preenchido':
            flash('Este formulário já foi preenchido.', 'info')
            return render_template('formularios/ja_preenchido.html', title='Formulário Preenchido')
        
        paciente = formulario.paciente
        form = PreenchimentoFormularioForm()
        
        # Pre-populate with patient information
        if request.method == 'GET':
            if paciente.doencas:
                form.historico_medico.data = paciente.doencas
            if paciente.medicamentos:
                form.medicamentos_atuais.data = paciente.medicamentos
            if paciente.alergias:
                form.alergias_novas.data = paciente.alergias
        
        if form.validate_on_submit():
            formulario.historico_medico = form.historico_medico.data
            formulario.queixas = form.queixas.data
            formulario.medicamentos_atuais = form.medicamentos_atuais.data
            formulario.alergias_novas = form.alergias_novas.data
            formulario.observacoes = form.observacoes.data
            formulario.data_preenchimento = datetime.now()
            formulario.status = 'preenchido'
            
            db.session.commit()
            
            flash('Formulário enviado com sucesso! Obrigado.', 'success')
            return render_template('formularios/confirmacao.html', title='Formulário Enviado')
        
        return render_template('formularios/preencher.html', 
                              form=form, 
                              paciente=paciente,
                              formulario=formulario,
                              title='Formulário de Pré-Consulta')

    # User management routes
    @app.route('/usuarios')
    @login_required
    def listar_usuarios():
        if current_user.tipo != 'admin':
            flash('Acesso restrito aos administradores.', 'danger')
            return redirect(url_for('dashboard'))
        
        usuarios = Usuario.query.all()
        return render_template('usuarios/lista.html', 
                              usuarios=usuarios,
                              title='Usuários do Sistema')

    @app.route('/usuarios/novo', methods=['GET', 'POST'])
    @login_required
    def novo_usuario():
        if current_user.tipo != 'admin':
            flash('Acesso restrito aos administradores.', 'danger')
            return redirect(url_for('dashboard'))
        
        form = UsuarioForm()
        
        if form.validate_on_submit():
            # Check if username or email already exists
            if Usuario.query.filter_by(username=form.username.data).first():
                flash('Nome de usuário já existe.', 'danger')
                return render_template('usuarios/novo.html', form=form, title='Novo Usuário')
            
            if Usuario.query.filter_by(email=form.email.data).first():
                flash('E-mail já cadastrado.', 'danger')
                return render_template('usuarios/novo.html', form=form, title='Novo Usuário')
            
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
            
            flash(f'Usuário {usuario.nome} cadastrado com sucesso!', 'success')
            return redirect(url_for('listar_usuarios'))
        
        return render_template('usuarios/novo.html', form=form, title='Novo Usuário')

    @app.route('/usuarios/<int:usuario_id>/alternar_status')
    @login_required
    def alternar_status_usuario(usuario_id):
        if current_user.tipo != 'admin':
            flash('Acesso restrito aos administradores.', 'danger')
            return redirect(url_for('dashboard'))
        
        usuario = Usuario.query.get_or_404(usuario_id)
        
        # Don't allow deactivating your own account
        if usuario.id == current_user.id:
            flash('Você não pode desativar seu próprio usuário.', 'danger')
            return redirect(url_for('listar_usuarios'))
        
        usuario.ativo = not usuario.ativo
        db.session.commit()
        
        status = 'ativado' if usuario.ativo else 'desativado'
        flash(f'Usuário {usuario.nome} {status} com sucesso.', 'success')
        
        return redirect(url_for('listar_usuarios'))

    # Error handlers
    # Página para enviar anamnese para pacientes
    @app.route('/formularios/enviar-anamnese', methods=['GET'])
    @login_required
    def listar_pacientes_anamnese():
        query = request.args.get('q', '')
        
        if query:
            # Busca por nome ou CPF
            pacientes = Paciente.query.filter(
                db.or_(
                    Paciente.nome.ilike(f'%{query}%'),
                    Paciente.cpf.ilike(f'%{query}%')
                )
            ).order_by(Paciente.nome).all()
        else:
            pacientes = Paciente.query.order_by(Paciente.nome).all()
        
        return render_template('formularios/pacientes_anamnese.html', 
                              pacientes=pacientes,
                              title='Enviar Anamnese')
    
    @app.route('/formularios/pacientes/<int:paciente_id>/enviar-anamnese', methods=['GET', 'POST'])
    @login_required
    def enviar_anamnese_paciente(paciente_id):
        paciente = Paciente.query.get_or_404(paciente_id)
        form = FormularioPreConsultaForm()
        
        # Get patient's appointments for dropdown
        agendamentos = paciente.agendamentos.filter(
            Agendamento.data_consulta >= date.today(),
            Agendamento.status == 'agendada'
        ).order_by(Agendamento.data_consulta).all()
        
        # Prepare choices for form dropdown
        form.agendamento_id.choices = [(str(a.id), f'{a.data_consulta.strftime("%d/%m/%Y")} - {a.hora_consulta} - {a.tipo_consulta}') 
                                    for a in agendamentos]
        form.agendamento_id.choices.insert(0, ('0', 'Selecione um agendamento (opcional)'))
        
        # Get pending forms
        formularios_pendentes = FormularioPreConsulta.query.filter_by(
            paciente_id=paciente_id,
            status='pendente'
        ).order_by(FormularioPreConsulta.data_envio.desc()).all()
        
        if form.validate_on_submit():
            formulario = FormularioPreConsulta(
                paciente_id=paciente_id,
                agendamento_id=int(form.agendamento_id.data) if form.agendamento_id.data != '0' else None,
                token=secrets.token_urlsafe(32),
                status='pendente'
            )
            
            db.session.add(formulario)
            db.session.commit()
            
            flash('Formulário de anamnese criado com sucesso!', 'success')
            
            # Redirect to the send form page
            return redirect(url_for('enviar_formulario', formulario_id=formulario.id))
        
        return render_template('formularios/enviar_anamnese.html', 
                              form=form, 
                              paciente=paciente,
                              agendamentos=agendamentos,
                              formularios_pendentes=formularios_pendentes,
                              title=f'Enviar Anamnese - {paciente.nome}')
        
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500