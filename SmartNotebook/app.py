from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
import logging
from datetime import datetime

# Add a global context processor to provide the current year for templates
def get_current_year():
    return datetime.now().year

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")

# Register context processor to provide current year and date functions to all templates
@app.context_processor
def inject_datetime_functions():
    return {
        'current_year': get_current_year(),
        'now': datetime.now,
        'today': lambda: datetime.now().strftime('%Y-%m-%d')
    }

# Ensure the radiografias directory exists
os.makedirs(os.path.join('static', 'radiografias'), exist_ok=True)

# Database configuration
DB_NAME = "pacientes.db"

def init_db():
    """Initialize the database with schema if it doesn't exist"""
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        with open('schema.sql', 'r') as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()
        logging.info("Database initialized with schema")

def get_db():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database
init_db()

# Route principal
@app.route('/')
def index():
    """Display main page with list of patients"""
    conn = get_db()
    pacientes = conn.execute("SELECT * FROM pacientes ORDER BY nome").fetchall()
    conn.close()
    return render_template('index.html', pacientes=pacientes)

# Search route
@app.route('/search', methods=['GET'])
def search():
    """Search patients by name or CPF"""
    query = request.args.get('query', '')
    if not query:
        return redirect(url_for('index'))
    
    conn = get_db()
    pacientes = conn.execute(
        "SELECT * FROM pacientes WHERE nome LIKE ? OR cpf LIKE ?", 
        (f'%{query}%', f'%{query}%')
    ).fetchall()
    conn.close()
    return render_template('index.html', pacientes=pacientes, query=query)

# Rota para cadastrar paciente
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    """Register a new patient"""
    if request.method == 'POST':
        try:
            nome = request.form['nome']
            nascimento = request.form['nascimento']
            telefone = request.form['telefone']
            endereco = request.form['endereco']
            cpf = request.form['cpf']
            genero = request.form['genero']
            doencas = request.form['doencas']
            medicamentos = request.form['medicamentos']
            alergias = request.form['alergias']
            cirurgias = request.form['cirurgias']
            habitos = request.form['habitos']
            observacoes = request.form['observacoes']
            
            # Validate required fields
            if not nome or not cpf:
                flash('Nome e CPF são campos obrigatórios', 'danger')
                return render_template('cadastro.html')
            
            conn = get_db()
            
            # Check if CPF already exists
            existing = conn.execute("SELECT id FROM pacientes WHERE cpf = ?", (cpf,)).fetchone()
            if existing:
                flash('CPF já cadastrado no sistema', 'danger')
                conn.close()
                return render_template('cadastro.html')
            
            conn.execute('''
                INSERT INTO pacientes (nome, nascimento, telefone, endereco, cpf, genero, doencas, medicamentos, alergias, cirurgias, habitos, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (nome, nascimento, telefone, endereco, cpf, genero, doencas, medicamentos, alergias, cirurgias, habitos, observacoes))
            conn.commit()
            conn.close()
            flash('Paciente cadastrado com sucesso!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Erro ao cadastrar paciente: {str(e)}', 'danger')
            logging.error(f"Error registering patient: {str(e)}")
            return render_template('cadastro.html')
    
    return render_template('cadastro.html')

# Rota para visualizar um paciente
@app.route('/paciente/<int:id>', methods=['GET'])
def paciente(id):
    """Show patient details and records"""
    conn = get_db()
    paciente = conn.execute("SELECT * FROM pacientes WHERE id = ?", (id,)).fetchone()
    if not paciente:
        conn.close()
        flash('Paciente não encontrado', 'danger')
        return redirect(url_for('index'))
    
    evolucoes = conn.execute("SELECT * FROM evolucoes WHERE paciente_id = ? ORDER BY data DESC", (id,)).fetchall()
    radios = conn.execute("SELECT * FROM radiografias WHERE paciente_id = ? ORDER BY data_upload DESC", (id,)).fetchall()
    conn.close()
    return render_template('paciente.html', paciente=paciente, evolucoes=evolucoes, radios=radios)

# Rota para editar paciente
@app.route('/editar/<int:id>', methods=['POST'])
def editar(id):
    """Edit patient information"""
    try:
        nome = request.form['nome']
        nascimento = request.form['nascimento']
        telefone = request.form['telefone']
        endereco = request.form['endereco']
        cpf = request.form['cpf']
        genero = request.form['genero']
        doencas = request.form['doencas']
        medicamentos = request.form['medicamentos']
        alergias = request.form['alergias']
        cirurgias = request.form['cirurgias']
        habitos = request.form['habitos']
        observacoes = request.form['observacoes']
        
        conn = get_db()
        conn.execute('''
            UPDATE pacientes SET 
            nome = ?, nascimento = ?, telefone = ?, endereco = ?, 
            cpf = ?, genero = ?, doencas = ?, medicamentos = ?, 
            alergias = ?, cirurgias = ?, habitos = ?, observacoes = ?
            WHERE id = ?
        ''', (nome, nascimento, telefone, endereco, cpf, genero, doencas, medicamentos, 
              alergias, cirurgias, habitos, observacoes, id))
        conn.commit()
        conn.close()
        flash('Dados do paciente atualizados com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao atualizar paciente: {str(e)}', 'danger')
        logging.error(f"Error updating patient: {str(e)}")
    
    return redirect(url_for('paciente', id=id))

# Rota para adicionar evolução ao paciente
@app.route('/evolucao/<int:id>', methods=['POST'])
def evolucao(id):
    """Add a new evolution/consultation record"""
    try:
        data = request.form['data']
        procedimento = request.form['procedimento']
        supervisor = request.form['supervisor']
        observacao = request.form['observacao']
        detalhes = request.form['detalhes']
        
        if not data or not procedimento:
            flash('Data e procedimento são campos obrigatórios', 'danger')
            return redirect(url_for('paciente', id=id))
        
        conn = get_db()
        conn.execute('''
            INSERT INTO evolucoes (paciente_id, data, procedimento, supervisor, observacao, detalhes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (id, data, procedimento, supervisor, observacao, detalhes))
        conn.commit()
        conn.close()
        flash('Evolução registrada com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao registrar evolução: {str(e)}', 'danger')
        logging.error(f"Error adding evolution: {str(e)}")
    
    return redirect(url_for('paciente', id=id))

# Rota para detalhes da consulta
@app.route('/consulta/<int:evolucao_id>')
def consulta(evolucao_id):
    """Show detailed consultation record"""
    conn = get_db()
    evolucao = conn.execute("""
        SELECT e.*, p.nome as paciente_nome, p.id as paciente_id
        FROM evolucoes e 
        JOIN pacientes p ON e.paciente_id = p.id 
        WHERE e.id = ?
    """, (evolucao_id,)).fetchone()
    
    if not evolucao:
        conn.close()
        flash('Registro de consulta não encontrado', 'danger')
        return redirect(url_for('index'))
    
    conn.close()
    return render_template('consulta.html', consulta=evolucao)

# Rota para excluir evolução
@app.route('/excluir_evolucao/<int:evolucao_id>', methods=['POST'])
def excluir_evolucao(evolucao_id):
    """Delete an evolution record"""
    try:
        conn = get_db()
        # First get the patient ID so we can redirect back
        evolucao = conn.execute("SELECT paciente_id FROM evolucoes WHERE id = ?", (evolucao_id,)).fetchone()
        
        if not evolucao:
            conn.close()
            flash('Registro não encontrado', 'danger')
            return redirect(url_for('index'))
        
        paciente_id = evolucao['paciente_id']
        
        # Delete the evolution
        conn.execute("DELETE FROM evolucoes WHERE id = ?", (evolucao_id,))
        conn.commit()
        conn.close()
        flash('Registro de evolução excluído com sucesso!', 'success')
        return redirect(url_for('paciente', id=paciente_id))
    except Exception as e:
        flash(f'Erro ao excluir evolução: {str(e)}', 'danger')
        logging.error(f"Error deleting evolution: {str(e)}")
        return redirect(url_for('index'))

# Rota para upload de radiografia
@app.route('/upload_radiografia/<int:id>', methods=['POST'])
def upload_radiografia(id):
    """Upload a radiograph image"""
    try:
        arquivo = request.files['radiografia']
        descricao = request.form.get('descricao', '')
        
        if not arquivo:
            flash('Nenhum arquivo selecionado', 'danger')
            return redirect(url_for('paciente', id=id))
            
        # Create a unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{arquivo.filename}"
        file_path = os.path.join('static', 'radiografias', filename)
        arquivo.save(file_path)
        
        conn = get_db()
        conn.execute('''
            INSERT INTO radiografias (paciente_id, nome_arquivo, descricao, data_upload)
            VALUES (?, ?, ?, datetime('now'))
        ''', (id, filename, descricao))
        conn.commit()
        conn.close()
        flash('Radiografia enviada com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao enviar radiografia: {str(e)}', 'danger')
        logging.error(f"Error uploading radiograph: {str(e)}")
    
    return redirect(url_for('paciente', id=id))

# Rota para excluir radiografia
@app.route('/excluir_radiografia/<int:radiografia_id>', methods=['POST'])
def excluir_radiografia(radiografia_id):
    """Delete a radiograph record"""
    paciente_id = None  # Initialize with default value
    
    try:
        conn = get_db()
        
        # Get radiograph info
        radiografia = conn.execute("SELECT paciente_id, nome_arquivo FROM radiografias WHERE id = ?", (radiografia_id,)).fetchone()
        
        if not radiografia:
            conn.close()
            flash('Radiografia não encontrada', 'danger')
            return redirect(url_for('index'))
        
        paciente_id = radiografia['paciente_id']
        
        # Delete the file if it exists
        file_path = os.path.join('static', 'radiografias', radiografia['nome_arquivo'])
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete the database record
        conn.execute("DELETE FROM radiografias WHERE id = ?", (radiografia_id,))
        conn.commit()
        conn.close()
        flash('Radiografia excluída com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir radiografia: {str(e)}', 'danger')
        logging.error(f"Error deleting radiograph: {str(e)}")
        if paciente_id is None:
            return redirect(url_for('index'))
    
    return redirect(url_for('paciente', id=paciente_id))

# Agenda de consultas - Lista todas as consultas
@app.route('/agenda')
def agenda():
    """Display appointment calendar"""
    # Get today's date in YYYY-MM-DD format
    data_filtro = request.args.get('data', datetime.now().strftime('%Y-%m-%d'))
    
    conn = get_db()
    agendamentos = conn.execute("""
        SELECT a.*, p.nome as paciente_nome 
        FROM agendamentos a
        JOIN pacientes p ON a.paciente_id = p.id
        WHERE a.data_consulta = ?
        ORDER BY a.hora_consulta
    """, (data_filtro,)).fetchall()
    conn.close()
    
    return render_template('agenda.html', agendamentos=agendamentos, data_filtro=data_filtro)

# Agendar nova consulta
@app.route('/agendar', methods=['GET', 'POST'])
def agendar():
    """Schedule a new appointment"""
    if request.method == 'POST':
        try:
            paciente_id = request.form['paciente_id']
            data_consulta = request.form['data_consulta']
            hora_consulta = request.form['hora_consulta']
            tipo_consulta = request.form['tipo_consulta']
            observacao = request.form['observacao']
            
            if not paciente_id or not data_consulta or not hora_consulta or not tipo_consulta:
                flash('Todos os campos obrigatórios devem ser preenchidos', 'danger')
                return redirect(url_for('agendar'))
            
            conn = get_db()
            
            # Check if there's already an appointment at the same time
            existing = conn.execute("""
                SELECT id FROM agendamentos 
                WHERE data_consulta = ? AND hora_consulta = ? AND status = 'agendada'
            """, (data_consulta, hora_consulta)).fetchone()
            
            if existing:
                flash('Já existe uma consulta agendada para este horário', 'danger')
                conn.close()
                return redirect(url_for('agendar'))
            
            conn.execute("""
                INSERT INTO agendamentos (paciente_id, data_consulta, hora_consulta, tipo_consulta, observacao)
                VALUES (?, ?, ?, ?, ?)
            """, (paciente_id, data_consulta, hora_consulta, tipo_consulta, observacao))
            
            conn.commit()
            conn.close()
            
            flash('Consulta agendada com sucesso!', 'success')
            return redirect(url_for('agenda', data=data_consulta))
        
        except Exception as e:
            flash(f'Erro ao agendar consulta: {str(e)}', 'danger')
            logging.error(f"Error scheduling appointment: {str(e)}")
            return redirect(url_for('agendar'))
    
    # GET request - display form
    conn = get_db()
    pacientes = conn.execute("SELECT id, nome, cpf FROM pacientes ORDER BY nome").fetchall()
    conn.close()
    
    return render_template('agendar.html', pacientes=pacientes)

# Atualizar status da consulta
@app.route('/atualizar_consulta/<int:agendamento_id>', methods=['POST'])
def atualizar_consulta(agendamento_id):
    """Update appointment status"""
    try:
        novo_status = request.form['status']
        data_consulta = request.form.get('data_consulta', '')
        
        if not novo_status:
            flash('Status não fornecido', 'danger')
            return redirect(url_for('agenda'))
        
        conn = get_db()
        conn.execute("UPDATE agendamentos SET status = ? WHERE id = ?", 
                    (novo_status, agendamento_id))
        conn.commit()
        conn.close()
        
        flash('Status da consulta atualizado com sucesso!', 'success')
        return redirect(url_for('agenda', data=data_consulta))
    
    except Exception as e:
        flash(f'Erro ao atualizar consulta: {str(e)}', 'danger')
        logging.error(f"Error updating appointment: {str(e)}")
        return redirect(url_for('agenda'))

# Excluir agendamento
@app.route('/excluir_agendamento/<int:agendamento_id>', methods=['POST'])
def excluir_agendamento(agendamento_id):
    """Delete an appointment"""
    try:
        data_consulta = request.form.get('data_consulta', '')
        
        conn = get_db()
        conn.execute("DELETE FROM agendamentos WHERE id = ?", (agendamento_id,))
        conn.commit()
        conn.close()
        
        flash('Agendamento excluído com sucesso!', 'success')
        return redirect(url_for('agenda', data=data_consulta))
    
    except Exception as e:
        flash(f'Erro ao excluir agendamento: {str(e)}', 'danger')
        logging.error(f"Error deleting appointment: {str(e)}")
        return redirect(url_for('agenda'))

# Backup database route
@app.route('/backup', methods=['GET'])
def backup():
    """Create a simple backup of the database"""
    try:
        import shutil
        from datetime import datetime
        
        # Create a backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_{timestamp}_{DB_NAME}"
        
        # Create backup directory if it doesn't exist
        os.makedirs('backups', exist_ok=True)
        
        # Copy the database file
        shutil.copy2(DB_NAME, os.path.join('backups', backup_file))
        
        flash(f'Backup criado com sucesso: {backup_file}', 'success')
    except Exception as e:
        flash(f'Erro ao criar backup: {str(e)}', 'danger')
        logging.error(f"Error creating backup: {str(e)}")
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
