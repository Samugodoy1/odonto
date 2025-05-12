# Sistema de Gerenciamento de Clínica Odontológica

Sistema completo para gerenciamento de clínicas odontológicas desenvolvido com Flask e PostgreSQL.

## Funcionalidades

- **Gerenciamento de Pacientes**: Cadastro, edição e visualização completa de informações de pacientes
- **Agendamento de Consultas**: Agenda interativa com marcação, alteração e cancelamento
- **Histórico Clínico**: Registro de evoluções e procedimentos realizados
- **Formulários Online**: Envio de anamnese e formulário de primeira consulta para pacientes
- **Radiografias**: Gerenciamento de imagens radiográficas
- **Notificações**: Sistema de avisos por e-mail (SendGrid) e SMS (Twilio)
- **Painel Administrativo**: Controle de usuários e permissões

## Tecnologias Utilizadas

- **Backend**: Python 3.11 com Flask
- **ORM**: SQLAlchemy
- **Banco de Dados**: PostgreSQL
- **Frontend**: HTML, CSS (Bootstrap), JavaScript
- **Autenticação**: Flask-Login
- **Validação de Formulários**: Flask-WTF
- **Envio de E-mails**: SendGrid API
- **Envio de SMS**: Twilio API

## Requisitos

Todas as dependências do projeto estão listadas no arquivo `dependencies.txt`.

## Estrutura do Projeto

- `app/`: Pasta principal da aplicação
  - `__init__.py`: Inicialização da aplicação Flask
  - `models.py`: Modelos de dados (SQLAlchemy)
  - `forms.py`: Formulários (Flask-WTF)
  - `routes.py`: Rotas da aplicação
  - `notifications.py`: Funções para envio de notificações
  - `templates/`: Templates HTML (Jinja2)
  - `static/`: Arquivos estáticos (CSS, JS, imagens)

## Configuração

O sistema utiliza variáveis de ambiente para configurações sensíveis:

- `DATABASE_URL`: URL de conexão com o banco de dados PostgreSQL
- `SESSION_SECRET`: Chave secreta para sessões
- `SENDGRID_API_KEY`: Chave de API do SendGrid (para envio de e-mails)
- `TWILIO_ACCOUNT_SID`: SID da conta Twilio
- `TWILIO_AUTH_TOKEN`: Token de autenticação do Twilio
- `TWILIO_PHONE_NUMBER`: Número de telefone Twilio para envio de SMS

## Funcionalidade de Formulários

### Formulário de Primeira Consulta

O sistema permite criar formulários para novos pacientes preencherem suas informações básicas antes da primeira consulta:

1. Administradores podem gerar links de formulários para enviar aos pacientes
2. Pacientes preenchem suas informações pessoais e de saúde
3. Administradores visualizam os formulários preenchidos e convertem em cadastros de pacientes

### Formulário de Anamnese

Para pacientes já cadastrados, é possível enviar formulários de anamnese antes de consultas específicas:

1. Seleção do paciente e consulta relacionada
2. Envio de link por e-mail
3. Armazenamento das informações para uso clínico