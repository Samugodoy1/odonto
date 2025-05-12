import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix
from sqlalchemy.orm import DeclarativeBase

logging.basicConfig(level=logging.DEBUG)

# Create a custom base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy with the custom base class
db = SQLAlchemy(model_class=Base)

# Initialize LoginManager
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Configure database
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///pacientes.db")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    
    with app.app_context():
        # Import models here to ensure they're properly registered with SQLAlchemy
        from app.models import (Usuario, Paciente, Evolucao, Radiografia, 
                               Agendamento, FormularioPreConsulta)
        
        # Create all database tables
        db.create_all()
        
        # Ensure admin user exists
        from werkzeug.security import generate_password_hash
        
        # Create admin user if it doesn't exist
        try:
            admin = Usuario.query.filter_by(username='admin').first()
            if not admin:
                admin = Usuario(
                    username='admin',
                    password_hash=generate_password_hash('admin123'),
                    nome='Administrador',
                    email='admin@clinica.com',
                    tipo='admin'
                )
                db.session.add(admin)
                db.session.commit()
                app.logger.info('Admin user created')
        except Exception as e:
            app.logger.error(f"Error creating admin user: {e}")
            db.session.rollback()
    
    # Register blueprints and routes
    from app.routes import register_routes
    register_routes(app)
    
    return app

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from app.models import Usuario
    return Usuario.query.get(int(user_id))

# Create the app instance for import in main.py
app = create_app()
