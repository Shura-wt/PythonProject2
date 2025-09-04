from flask import Blueprint, request, jsonify, redirect, url_for, render_template, current_app
from flask_login import login_user, logout_user, login_required
from flasgger import swag_from
from ..models.user import User
from ..models import db
import jwt
import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
@swag_from({
    'tags': ['Authentication'],
    'description': 'Connexion de l\'utilisateur via JSON. Fournissez "login" et "password" dans le corps de la requête.',
    'consumes': ['application/json'],
    'parameters': [
        {
            'in': 'body',
            'name': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['login', 'password'],
                'properties': {
                    'login': {'type': 'string', 'example': 'monlogin'},
                    'password': {'type': 'string', 'example': 'monmotdepasse'}
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Utilisateur connecté avec succès',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Connecté'},
                    'user_id': {'type': 'integer', 'example': 1},
                    'sites': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer', 'example': 3},
                                'name': {'type': 'string', 'example': 'Site A'},
                                'roles': {
                                    'type': 'array',
                                    'items': {
                                        'type': 'object',
                                        'properties': {
                                            'id': {'type': 'integer', 'example': 2},
                                            'name': {'type': 'string', 'example': 'admin'}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    'global_roles': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer', 'example': 1},
                                'name': {'type': 'string', 'example': 'super_admin'}
                            }
                        },
                        'description': 'Rôles globaux de l\'utilisateur (non liés à un site spécifique)'
                    },
                    'token': {'type': 'string', 'example': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...', 'description': 'JWT token d\'authentification'}
                }
            }
        },
        '401': {
            'description': 'Identifiants invalides',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Identifiants invalides'}
                }
            }
        }
    }
})
def login():
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.get_json()
    if not data or 'login' not in data or 'password' not in data:
        return jsonify({'error': 'Les champs "login" et "password" sont requis'}), 400

    login_input = data.get('login')
    password = data.get('password')
    user = User.query.filter_by(login=login_input).first()
    if user and user.check_password(password):
        login_user(user)  # L'utilisateur est connecté et stocké dans la session

        # Récupérer la liste des associations via le backref user_site_roles
        # et grouper par site avec leurs rôles associés.
        sites_dict = {}
        global_roles = []

        for assoc in user.user_site_roles.all():
            # Traiter les rôles globaux (sans site)
            if assoc.site_id is None:
                if assoc.role and assoc.role.id not in [r['id'] for r in global_roles]:
                    global_roles.append({
                        'id': assoc.role.id,
                        'name': assoc.role.name
                    })
            # Traiter les rôles liés à un site
            elif assoc.site:
                sid = assoc.site.id
                if sid not in sites_dict:
                    sites_dict[sid] = {
                        'id': assoc.site.id,
                        'name': assoc.site.name,
                        'roles': []
                    }
                if assoc.role:
                    # Ajoute le rôle s'il n'est pas déjà présent
                    if assoc.role.id not in [r['id'] for r in sites_dict[sid]['roles']]:
                        sites_dict[sid]['roles'].append({
                            'id': assoc.role.id,
                            'name': assoc.role.name
                        })

        # Générer un token JWT
        token_payload = {
            'user_id': user.id,
            'login': user.login,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)  # Expiration dans 1 jour
        }

        # Utiliser une clé secrète depuis la configuration de l'application ou une valeur par défaut
        secret_key = current_app.config.get('JWT_SECRET_KEY', 'default_secret_key')
        token = jwt.encode(token_payload, secret_key, algorithm='HS256')

        response = {
            'message': 'Connecté',
            'user_id': user.id,
            'sites': list(sites_dict.values()),
            'token': token
        }

        # Ajouter les rôles globaux à la réponse s'il y en a
        if global_roles:
            response['global_roles'] = global_roles

        return jsonify(response), 200
    else:
        return jsonify({'error': 'Identifiants invalides'}), 401

@auth_bp.route('/logout', methods=['POST', 'OPTIONS', 'GET'])
@swag_from({
    'tags': ['Authentication'],
    'description': 'Déconnecte l\'utilisateur connecté.',
    'responses': {
        '200': {
            'description': 'Utilisateur déconnecté avec succès',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Déconnecté'}
                }
            }
        }
    }
})
def logout():
    # CORS preflight
    if request.method == 'OPTIONS':
        return '', 200

    # Support stateless JWT-first clients: accept Bearer token but we just return success.
    # If a Flask-Login session exists, we clear it; otherwise, still return 200 to be idempotent.
    try:
        logout_user()
    except Exception:
        pass
    return jsonify({'message': 'Déconnecté'}), 200
