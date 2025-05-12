-- Schema for the pacientes.db database

-- Pacientes table
CREATE TABLE IF NOT EXISTS pacientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    nascimento TEXT, -- Date format YYYY-MM-DD
    telefone TEXT,
    endereco TEXT,
    cpf TEXT UNIQUE,
    genero TEXT,
    doencas TEXT, -- Doenças preexistentes
    medicamentos TEXT, -- Medicamentos em uso
    alergias TEXT,
    cirurgias TEXT, -- Histórico de cirurgias
    habitos TEXT, -- Hábitos relevantes (fumo, álcool, etc)
    observacoes TEXT,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Evolucoes table (consultas/atendimentos)
CREATE TABLE IF NOT EXISTS evolucoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id INTEGER,
    data TEXT NOT NULL, -- Date format YYYY-MM-DD
    procedimento TEXT NOT NULL,
    supervisor TEXT, -- Nome do supervisor/dentista
    observacao TEXT,
    detalhes TEXT, -- Detalhes extensos do procedimento
    data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paciente_id) REFERENCES pacientes (id) ON DELETE CASCADE
);

-- Radiografias table
CREATE TABLE IF NOT EXISTS radiografias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id INTEGER,
    nome_arquivo TEXT NOT NULL,
    descricao TEXT,
    data_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paciente_id) REFERENCES pacientes (id) ON DELETE CASCADE
);

-- Appointments table (agenda de consultas)
CREATE TABLE IF NOT EXISTS agendamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id INTEGER,
    data_consulta TEXT NOT NULL, -- Date format YYYY-MM-DD
    hora_consulta TEXT NOT NULL, -- Time format HH:MM
    tipo_consulta TEXT NOT NULL,
    observacao TEXT,
    status TEXT DEFAULT 'agendada', -- agendada, concluida, cancelada, faltou
    data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paciente_id) REFERENCES pacientes (id) ON DELETE CASCADE
);

-- Users table for dentist login
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    nome TEXT NOT NULL,
    email TEXT UNIQUE,
    tipo TEXT DEFAULT 'dentista', -- dentista, admin, etc.
    ativo INTEGER DEFAULT 1, -- 0=inactive, 1=active
    ultimo_acesso TIMESTAMP,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Formulários para pacientes preencherem antes da consulta
CREATE TABLE IF NOT EXISTS formularios_pre_consulta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id INTEGER,
    agendamento_id INTEGER,
    token TEXT UNIQUE, -- token único para acesso do paciente
    data_envio TIMESTAMP,
    data_preenchimento TIMESTAMP,
    status TEXT DEFAULT 'pendente', -- pendente, preenchido, expirado
    historico_medico TEXT,
    queixas TEXT,
    medicamentos_atuais TEXT,
    alergias_novas TEXT,
    observacoes TEXT,
    FOREIGN KEY (paciente_id) REFERENCES pacientes (id) ON DELETE CASCADE,
    FOREIGN KEY (agendamento_id) REFERENCES agendamentos (id) ON DELETE CASCADE
);

-- Indexes for faster searching
CREATE INDEX IF NOT EXISTS idx_pacientes_nome ON pacientes(nome);
CREATE INDEX IF NOT EXISTS idx_pacientes_cpf ON pacientes(cpf);
CREATE INDEX IF NOT EXISTS idx_evolucoes_paciente ON evolucoes(paciente_id);
CREATE INDEX IF NOT EXISTS idx_radiografias_paciente ON radiografias(paciente_id);
CREATE INDEX IF NOT EXISTS idx_agendamentos_paciente ON agendamentos(paciente_id);
CREATE INDEX IF NOT EXISTS idx_agendamentos_data ON agendamentos(data_consulta);
CREATE INDEX IF NOT EXISTS idx_usuarios_username ON usuarios(username);
CREATE INDEX IF NOT EXISTS idx_formularios_token ON formularios_pre_consulta(token);
CREATE INDEX IF NOT EXISTS idx_formularios_paciente ON formularios_pre_consulta(paciente_id);
