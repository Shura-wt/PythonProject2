import os
import logging
import urllib
import pyodbc
import time
import sys

from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flasgger import Swagger
from flask_login import LoginManager
from sqlalchemy.exc import OperationalError, InterfaceError

from .models import db
from .models.user import User
from .models.site import Site
from .default_data import create_default_data
from .routes import init_app as init_routes


# Initialisation de l'application Flask
app = Flask(__name__)
app.secret_key = 'ta_clé_secrète_unique_et_complexe'
app.config['JWT_SECRET_KEY'] = app.secret_key  # Utiliser la même clé pour JWT
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', '0') == '1'
CORS(app)

# ===== Configuration de la base de données =====
# Get database connection details from environment variables
DB_USER = os.environ.get('DB_USER', 'Externe')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'Secur3P@ssw0rd!')
DB_HOST = os.environ.get('DB_HOST', 'mssql')
DB_NAME = os.environ.get('DB_NAME', 'master')
DB_PORT = os.environ.get('DB_PORT', '1433')

connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={DB_HOST};"
    f"DATABASE={DB_NAME};"
    f"UID={DB_USER};"
    f"PWD={DB_PASSWORD}"
)

# connection_string = (
#     "DRIVER={ODBC Driver 17 for SQL Server};"
#     "SERVER=127.0.0.1;"
#     "DATABASE=master;"
#     "UID=Externe;"
#     "PWD=Secur3P@ssw0rd!"
# )

params = urllib.parse.quote_plus(connection_string)
app.config['SQLALCHEMY_DATABASE_URI'] = f"mssql+pyodbc:///?odbc_connect={params}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True

# ===== Configuration pour l'upload =====
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# ===== Configuration du logging =====
logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)

# ===== Configuration Swagger avec définitions des modèles =====
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            # Exclure les anciennes routes '/erreurs' de la documentation pour éviter les doublons
            "rule_filter": lambda rule: not rule.rule.startswith('/erreurs'),
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/swagger/",
    "title": "BAES API - Documentation",
    "description": "API de gestion des BAES, avec endpoints pour l'authentification, les sites, bâtiments, étages, BAES, statuts et cartes.",
    "termsOfService": "",
    "version": "1.0",
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "BAES API",
        "description": "API pour la gestion des BAES",
        "version": "1.0",
    },
    "tags": [
        {"name": "Authentication", "description": "Authentification (login, logout)"},
        {"name": "User CRUD", "description": "Gestion des utilisateurs"},
        {"name": "Site CRUD", "description": "Gestion des sites"},
        {"name": "Batiment CRUD", "description": "Gestion des bâtiments"},
        {"name": "Etage CRUD", "description": "Gestion des étages"},
        {"name": "BAES CRUD", "description": "Gestion des BAES (Blocs Autonomes d'Éclairage de Sécurité)"},
        {"name": "Status CRUD", "description": "Gestion des statuts/erreurs des BAES"},
        {"name": "carte crud", "description": "Gestion des cartes (plans, coordonnées, zoom)"},
        {"name": "general", "description": "Routes utilitaires et agrégées (ex: version API, données consolidées)"},
        {"name": "Configuration CRUD", "description": "Paramètres de configuration"}
    ],
    "definitions": {
        "Baes": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "format": "int64"},
                "name": {"type": "string"},
                "label": {"type": "string"},
                "position": {"type": "object"},
                "etage_id": {"type": "integer", "format": "int64"},
                "created_at": {"type": "string", "format": "date-time"},
                "updated_at": {"type": "string", "format": "date-time"}
            }
        },
        "User": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "format": "int64"},
                "login": {"type": "string"},
                "created_at": {"type": "string", "format": "date-time"},
                "updated_at": {"type": "string", "format": "date-time"}
            }
        },
        "Carte": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "format": "int64"},
                "chemin": {"type": "string"},
                "etage_id": {"type": "integer", "format": "int64", "nullable": "true" },
                "site_id": {"type": "integer", "format": "int64", "nullable": "true"},
                "center_lat": {"type": "number", "format": "float"},
                "center_lng": {"type": "number", "format": "float"},
                "zoom": {"type": "number", "format": "float"},
                "created_at": {"type": "string", "format": "date-time"},
                "updated_at": {"type": "string", "format": "date-time"}
            }
        },
        "Batiment": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "format": "int64"},
                "name": {"type": "string"},
                "site_id": {"type": "integer", "format": "int64"},
                "created_at": {"type": "string", "format": "date-time"},
                "updated_at": {"type": "string", "format": "date-time"}
            }
        },
        "Etage": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "format": "int64"},
                "name": {"type": "string"},
                "batiment_id": {"type": "integer", "format": "int64"},
                "created_at": {"type": "string", "format": "date-time"},
                "updated_at": {"type": "string", "format": "date-time"}
            }
        },
        "Status": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "format": "int64"},
                "baes_id": {"type": "integer", "format": "int64"},
                "erreur": {"type": "integer"},
                "is_solved": {"type": "boolean"},
                "is_ignored": {"type": "boolean"},
                "acknowledged_by_user_id": {"type": "integer", "nullable": True},
                "acknowledged_at": {"type": "string", "format": "date-time", "nullable": True},
                "timestamp": {"type": "string", "format": "date-time"},
                "created_at": {"type": "string", "format": "date-time"},
                "updated_at": {"type": "string", "format": "date-time"}
            }
        },
        "Role": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "format": "int64"},
                "name": {"type": "string"},
                "created_at": {"type": "string", "format": "date-time"},
                "updated_at": {"type": "string", "format": "date-time"}
            }
        },
        "Site": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "format": "int64"},
                "name": {"type": "string"},
                "created_at": {"type": "string", "format": "date-time"},
                "updated_at": {"type": "string", "format": "date-time"}
            }
        },
        "UserSiteRole": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "format": "int64"},
                "user_id": {"type": "integer", "format": "int64"},
                "site_id": {"type": "integer", "format": "int64"},
                "role_id": {"type": "integer", "format": "int64"},
                "created_at": {"type": "string", "format": "date-time"},
                "updated_at": {"type": "string", "format": "date-time"}
            }
        }
    }
}

# ===== Initialisation des extensions =====
db.init_app(app)
migrate = Migrate(app, db)
swagger = Swagger(app, config=swagger_config, template=swagger_template)

# ===== Configuration de Flask-Login =====
login_manager = LoginManager()
login_manager.init_app(app)
# Désactiver la redirection HTML pour les endpoints API, retourner un JSON 401 à la place
login_manager.login_view = None

@login_manager.unauthorized_handler
def unauthorized():
    from flask import jsonify
    return jsonify({"error": "unauthorized"}), 401

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ===== Enregistrement des blueprints =====
init_routes(app)

# ===== Point d'entrée principal =====
if __name__ == '__main__':
    app.logger.debug("Démarrage de l'application et test de connexion à la base...")
    print("Pilotes ODBC installés :", pyodbc.drivers())


    # Paramètres de retry
    max_retries = 30
    retry_interval = 5  # secondes

    with app.app_context():
        # Boucle de retry pour la connexion à la base de données
        for retry in range(max_retries):
            try:
                app.logger.debug(f"Tentative de connexion à la base de données ({retry+1}/{max_retries})...")
                connection = db.engine.connect()
                connection.close()
                app.logger.debug("Connexion réussie à la base de données.")

                # Créer les tables si elles n'existent pas
                app.logger.debug("Création des tables si elles n'existent pas...")
                db.create_all()
                app.logger.debug("Tables créées avec succès.")

                # Création des données par défaut
                create_default_data()

                # Si on arrive ici, tout s'est bien passé, on sort de la boucle
                break

            except (OperationalError, InterfaceError) as e:
                app.logger.warning(f"Erreur de connexion à la base de données (tentative {retry+1}/{max_retries}): {e}")
                if retry < max_retries - 1:
                    app.logger.info(f"Nouvelle tentative dans {retry_interval} secondes...")
                    time.sleep(retry_interval)
                else:
                    app.logger.error(f"Échec de connexion à la base de données après {max_retries} tentatives.")
                    # On continue quand même pour démarrer l'application, elle réessaiera à chaque requête
            except Exception as e:
                app.logger.error(f"Erreur inattendue lors de l'initialisation de la base de données: {e}")
                # On continue quand même pour démarrer l'application

    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=True)
