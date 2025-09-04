# routes/status_routes.py
from flask import Blueprint, request, jsonify, current_app
from flasgger import swag_from
from ..models.status import Status
from ..models.baes import Baes
from ..models import db
from flask_login import current_user, login_required
from datetime import datetime, timezone


status_bp = Blueprint('status_bp', __name__)

@status_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['Status CRUD'],
    'description': 'Récupère la liste de toutes les erreurs.',
    'responses': {
        200: {
            'description': 'Liste des erreurs.',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'example': 1},
                        'baes_id': {'type': 'integer', 'format': 'int64', 'example': 1},
                        'erreur': {'type': 'integer', 'example': 1},
                        'is_solved': {'type': 'boolean', 'example': False},
                        'is_ignored': {'type': 'boolean', 'example': False},
                        'temperature': {'type': 'number', 'format': 'float', 'example': 25.5, 'nullable': True},
                        'vibration': {'type': 'boolean', 'example': True, 'nullable': True},
                        'timestamp': {'type': 'string', 'format': 'date-time', 'example': '2023-01-01T12:00:00Z'},
                        'updated_at': {'type': 'string', 'format': 'date-time', 'example': '2023-01-01T12:00:00Z'}
                    }
                }
            }
        },
        500: {'description': 'Erreur interne.'}
    }
})
def get_statuses():
    try:
        statuses = Status.query.all()
        result = [{
            'id': e.id,
            'baes_id': e.baes_id,
            'erreur': e.erreur,
            'is_solved': e.is_solved,
            'is_ignored': e.is_ignored,
            'temperature': e.temperature,
            'vibration': e.vibration,
            'timestamp': e.timestamp.isoformat() if e.timestamp else None,
            'updated_at': e.updated_at.isoformat() if e.updated_at else None
        } for e in statuses]
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_statuses: {e}")
        return jsonify({'error': str(e)}), 500

@status_bp.route('/<int:status_id>', methods=['GET'])
@swag_from({
    'tags': ['Status CRUD'],
    'description': 'Récupère une erreur par son ID.',
    'parameters': [
        {
            'name': 'status_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID de l'erreur à récupérer"
        }
    ],
    'responses': {
        200: {
            'description': "Détails de l'erreur.",
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'baes_id': {'type': 'integer', 'format': 'int64', 'example': 1},
                    'erreur': {'type': 'integer', 'example': 1},
                    'is_solved': {'type': 'boolean', 'example': False},
                    'is_ignored': {'type': 'boolean', 'example': False},
                    'temperature': {'type': 'number', 'format': 'float', 'example': 25.5, 'nullable': True},
                    'vibration': {'type': 'boolean', 'example': True, 'nullable': True},
                    'timestamp': {'type': 'string', 'format': 'date-time', 'example': '2023-01-01T12:00:00Z'},
                    'updated_at': {'type': 'string', 'format': 'date-time', 'example': '2023-01-01T12:00:00Z'}
                }
            }
        },
        404: {'description': "Erreur non trouvée."}
    }
})
def get_status(status_id):
    try:
        status = Status.query.get(status_id)
        if not status:
            return jsonify({'error': 'Erreur non trouvée'}), 404
        result = {
            'id': status.id,
            'baes_id': status.baes_id,
            'erreur': status.erreur,
            'is_solved': status.is_solved,
            'is_ignored': status.is_ignored,
            'temperature': status.temperature,
            'vibration': status.vibration,
            'timestamp': status.timestamp.isoformat() if status.timestamp else None,
            'updated_at': status.updated_at.isoformat() if status.updated_at else None
        }
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_status: {e}")
        return jsonify({'error': str(e)}), 500

@status_bp.route('/after/<string:updated_at>', methods=['GET'])
@swag_from({
    'tags': ['Status CRUD'],
    'description': 'Récupère toutes les erreurs modifiées à ou après le timestamp spécifié (à la seconde près).',
    'parameters': [
        {
            'name': 'updated_at',
            'in': 'path',
            'type': 'string',
            'format': 'date-time',
            'required': True,
            'description': "Timestamp ISO 8601 (ex: 2023-01-01T12:00:00Z) à partir duquel récupérer les erreurs modifiées"
        }
    ],
    'responses': {
        200: {
            'description': 'Liste des erreurs modifiées à ou après le timestamp spécifié.',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'example': 13},
                        'baes_id': {'type': 'integer', 'format': 'int64', 'example': 1},
                        'erreur': {'type': 'integer', 'example': 1},
                        'is_solved': {'type': 'boolean', 'example': False},
                        'is_ignored': {'type': 'boolean', 'example': False},
                        'temperature': {'type': 'number', 'format': 'float', 'example': 25.5, 'nullable': True},
                        'vibration': {'type': 'boolean', 'example': True, 'nullable': True},
                        'timestamp': {'type': 'string', 'format': 'date-time', 'example': '2023-01-01T12:00:00Z'},
                        'updated_at': {'type': 'string', 'format': 'date-time', 'example': '2023-01-01T12:00:00Z'},
                        'acknowledged_by_user_id': {'type': 'integer', 'example': 1, 'nullable': True},
                        'acknowledged_at': {'type': 'string', 'format': 'date-time', 'example': '2023-01-02T14:30:00Z', 'nullable': True},
                        'acknowledged_by_login': {'type': 'string', 'example': 'user1', 'nullable': True}
                    }
                }
            }
        },
        400: {'description': 'Format de timestamp invalide.'},
        500: {'description': 'Erreur interne.'}
    }
})
def get_statuses_after_timestamp(updated_at):
    try:
        # Convertir le timestamp ISO 8601 en objet datetime
        try:
            timestamp = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Format de timestamp invalide. Utilisez le format ISO 8601 (ex: 2023-01-01T12:00:00Z)'}), 400

        # Récupérer toutes les erreurs modifiées à ou après le timestamp spécifié
        statuses = Status.query.filter(Status.updated_at >= timestamp).order_by(Status.updated_at).all()

        result = []
        for e in statuses:
            # Récupérer le login de l'utilisateur qui a acquitté l'erreur
            acknowledged_by_login = None
            if e.acknowledged_by_user_id:
                from ..models.user import User
                user = User.query.get(e.acknowledged_by_user_id)
                if user:
                    acknowledged_by_login = user.login

            result.append({
                'id': e.id,
                'baes_id': e.baes_id,
                'erreur': e.erreur,
                'is_solved': e.is_solved,
                'is_ignored': e.is_ignored,
                'temperature': e.temperature,
                'vibration': e.vibration,
                'timestamp': e.timestamp.isoformat() if e.timestamp else None,
                'updated_at': e.updated_at.isoformat() if e.updated_at else None,
                'acknowledged_by_user_id': e.acknowledged_by_user_id,
                'acknowledged_at': e.acknowledged_at.isoformat() if e.acknowledged_at else None,
                'acknowledged_by_login': acknowledged_by_login
            })

        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_erreurs_after_timestamp: {e}")
        return jsonify({'error': str(e)}), 500

@status_bp.route('/baes/<int:baes_id>', methods=['GET'])
@swag_from({
    'tags': ['Status CRUD'],
    'description': 'Récupère toutes les erreurs pour un BAES spécifique.',
    'parameters': [
        {
            'name': 'baes_id',
            'in': 'path',
            'type': 'integer',
            'format': 'int64',
            'required': True,
            'description': "ID du BAES dont on veut récupérer les erreurs"
        }
    ],
    'responses': {
        200: {
            'description': "Liste des erreurs pour le BAES spécifié.",
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'example': 1},
                        'baes_id': {'type': 'integer', 'format': 'int64', 'example': 1},
                        'erreur': {'type': 'integer', 'example': 1},
                        'is_solved': {'type': 'boolean', 'example': False},
                        'is_ignored': {'type': 'boolean', 'example': False},
                        'temperature': {'type': 'number', 'format': 'float', 'example': 25.5, 'nullable': True},
                        'vibration': {'type': 'boolean', 'example': True, 'nullable': True},
                        'timestamp': {'type': 'string', 'format': 'date-time', 'example': '2023-01-01T12:00:00Z'},
                        'updated_at': {'type': 'string', 'format': 'date-time', 'example': '2023-01-01T12:00:00Z'},
                        'acknowledged_by_user_id': {'type': 'integer', 'example': 1, 'nullable': True},
                        'acknowledged_at': {'type': 'string', 'format': 'date-time', 'example': '2023-01-02T14:30:00Z', 'nullable': True},
                        'acknowledged_by_login': {'type': 'string', 'example': 'user1', 'nullable': True}
                    }
                }
            }
        },
        404: {'description': "BAES non trouvé."}
    }
})
def get_statuses_by_baes(baes_id):
    try:
        # Vérifier si le BAES existe
        baes = Baes.query.get(baes_id)
        if not baes:
            return jsonify({'error': 'BAES non trouvé'}), 404

        statuses = Status.query.filter_by(baes_id=baes_id).all()
        result = []
        for e in statuses:
            # Récupérer le login de l'utilisateur qui a acquitté l'erreur
            acknowledged_by_login = None
            if e.acknowledged_by_user_id:
                from ..models.user import User
                user = User.query.get(e.acknowledged_by_user_id)
                if user:
                    acknowledged_by_login = user.login

            result.append({
                'id': e.id,
                'baes_id': e.baes_id,
                'erreur': e.erreur,
                'is_solved': e.is_solved,
                'is_ignored': e.is_ignored,
                'temperature': e.temperature,
                'vibration': e.vibration,
                'timestamp': e.timestamp.isoformat() if e.timestamp else None,
                'updated_at': e.updated_at.isoformat() if e.updated_at else None,
                'acknowledged_by_user_id': e.acknowledged_by_user_id,
                'acknowledged_at': e.acknowledged_at.isoformat() if e.acknowledged_at else None,
                'acknowledged_by_login': acknowledged_by_login
            })
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_erreurs_by_baes: {e}")
        return jsonify({'error': str(e)}), 500

@status_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['Status CRUD'],
    'description': "Crée une nouvelle entrée d'erreur.",
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'baes_id': {'type': 'integer', 'format': 'int64', 'example': 1},
                    'erreur': {'type ': 'integer ', 'example': 1, 'description': "Type d'erreur décrit dans le front (1 pour erreur_connexion, 2 pour erreur_batterie)"},
                    'is_solved': {'type': 'boolean', 'example': False},
                    'is_ignored': {'type': 'boolean', 'example': False},
                    'name': {'type': 'string', 'example': 'BAES-1', 'description': 'Nom du BAES (utilisé si le BAES n\'existe pas)', 'nullable': True},
                    'label': {'type': 'string', 'example': 'Étiquette BAES', 'description': 'Étiquette du BAES (utilisé si le BAES n\'existe pas)', 'nullable': True},
                    'temperature': {'type': 'number', 'format': 'float', 'example': 25.5, 'description': 'Température du BAES (utilisé si le BAES n\'existe pas)', 'nullable': True},
                    'vibration': {'type': 'boolean', 'example': True, 'description': 'État de vibration du BAES (utilisé si le BAES n\'existe pas)', 'nullable': True}
                },
                'required': ['baes_id', 'erreur']
            }
        }
    ],
    'responses': {
        201: {
            'description': "Erreur créée avec succès.",
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'baes_id': {'type': 'integer', 'format': 'int64', 'example': 1},
                    'erreur': {'type': 'integer', 'example': 1},
                    'is_solved': {'type': 'boolean', 'example': False},
                    'is_ignored': {'type': 'boolean', 'example': False},
                    'temperature': {'type': 'number', 'format': 'float', 'example': 25.5, 'nullable': True},
                    'vibration': {'type': 'boolean', 'example': True, 'nullable': True},
                    'timestamp': {'type': 'string', 'format': 'date-time', 'example': '2023-01-01T12:00:00Z'},
                    'baes': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer', 'format': 'int64', 'example': 1},
                            'name': {'type': 'string', 'example': 'BAES-1', 'nullable': True},
                            'label': {'type': 'string', 'example': 'Étiquette BAES', 'nullable': True}
                        }
                    }
                }
            }
        },
        400: {'description': "Mauvaise requête."},
        404: {'description': "BAES non trouvé."}
    }
})
def create_status():
    try:
        data = request.get_json()
        if not data or 'baes_id' not in data or 'erreur' not in data:
            return jsonify({'error': 'Les champs baes_id et erreur sont requis'}), 400

        # Vérifier si le BAES existe
        baes = Baes.query.get(data['baes_id'])
        if not baes:
            # Si le BAES n'existe pas, on le crée avec etage_id à null
            new_baes = Baes(
                id=data['baes_id'],
                name=data.get('name', f"BAES-{data['baes_id']}"),  # Utiliser le nom fourni ou un nom générique
                label=data.get('label'),  # Utiliser le label fourni ou null
                position={"x": 0, "y": 0},  # Position par défaut
                etage_id=None  # Site_id à null (via etage_id)
            )
            db.session.add(new_baes)
            db.session.commit()
            baes = new_baes

        # Vérifier si le type d'erreur est valide

        status = Status(
            baes_id=data['baes_id'],
            erreur=data['erreur'],
            is_solved=data.get('is_solved', False),
            is_ignored=data.get('is_ignored', False),
            temperature=data.get('temperature'),  # Utiliser la température fournie ou null
            vibration=data.get('vibration', False)  # Utiliser la vibration fournie ou False par défaut
        )
        db.session.add(status)
        db.session.commit()

        result = {
            'id': status.id,
            'baes_id': status.baes_id,
            'erreur': status.erreur,
            'is_solved': status.is_solved,
            'is_ignored': status.is_ignored,
            'temperature': status.temperature,
            'vibration': status.vibration,
            'timestamp': status.timestamp.isoformat() if status.timestamp else None,
            'baes': {
                'id': baes.id,
                'name': baes.name,
                'label': baes.label
            }
        }
        return jsonify(result), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in create_status: {e}")
        return jsonify({'error': str(e)}), 500

@status_bp.route('/<int:status_id>/status', methods=['PUT'])
@swag_from({
    'tags': ['Status CRUD'],
    'description': "Met à jour le statut d'une erreur (résolu/ignoré) et enregistre l'utilisateur qui a fait l'acquittement.",
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'status_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID de l'erreur à mettre à jour"
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'is_solved': {'type': 'boolean', 'example': True},
                    'is_ignored': {'type': 'boolean', 'example': False},
                    'user_id': {'type': 'integer', 'example': 1, 'description': 'ID de l\'utilisateur qui acquitte l\'erreur (optionnel)'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': "Statut de l'erreur mis à jour avec succès.",
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'baes_id': {'type': 'integer', 'format': 'int64', 'example': 1},
                    'erreur': {'type': 'integer', 'example': 1},
                    'is_solved': {'type': 'boolean', 'example': True},
                    'is_ignored': {'type': 'boolean', 'example': False},
                    'timestamp': {'type': 'string', 'format': 'date-time', 'example': '2023-01-01T12:00:00Z'},
                    'acknowledged_by_user_id': {'type': 'integer', 'example': 1},
                    'acknowledged_at': {'type': 'string', 'format': 'date-time', 'example': '2023-01-02T14:30:00Z'},
                    'acknowledged_by_login': {'type': 'string', 'example': 'user1'}
                }
            }
        },
        400: {'description': "Mauvaise requête."},
        404: {'description': "Erreur non trouvée."}
    }
})
def update_status_status(status_id):
    try:
        status = Status.query.get(status_id)
        if not status:
            return jsonify({'error': 'Erreur non trouvée'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Aucune donnée fournie'}), 400

        # Vérifier si l'état de l'erreur change
        status_changed = False
        if 'is_solved' in data and status.is_solved != data['is_solved']:
            status.is_solved = data['is_solved']
            status_changed = True
        if 'is_ignored' in data and status.is_ignored != data['is_ignored']:
            status.is_ignored = data['is_ignored']
            status_changed = True

        # Si l'état a changé, enregistrer l'utilisateur qui a fait l'acquittement
        if status_changed:
            # Vérifier si un utilisateur est connecté ou si un user_id est fourni dans les données
            if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
                status.acknowledged_by_user_id = current_user.id
            elif 'user_id' in data:
                # Utiliser l'ID d'utilisateur fourni dans la requête
                status.acknowledged_by_user_id = data['user_id']
            else:
                # Aucun utilisateur spécifié, utiliser None ou une valeur par défaut
                status.acknowledged_by_user_id = None

            status.acknowledged_at = datetime.now(timezone.utc)

        db.session.commit()

        # Récupérer le login de l'utilisateur qui a acquitté l'erreur
        acknowledged_by_login = None
        if status.acknowledged_by_user_id:
            from ..models.user import User
            user = User.query.get(status.acknowledged_by_user_id)
            if user:
                acknowledged_by_login = user.login

        result = {
            'id': status.id,
            'baes_id': status.baes_id,
            'erreur': status.erreur,
            'is_solved': status.is_solved,
            'is_ignored': status.is_ignored,
            'temperature': status.temperature,
            'vibration': status.vibration,
            'timestamp': status.timestamp.isoformat() if status.timestamp else None,
            'acknowledged_by_user_id': status.acknowledged_by_user_id,
            'acknowledged_at': status.acknowledged_at.isoformat() if status.acknowledged_at else None,
            'acknowledged_by_login': acknowledged_by_login
        }
        return jsonify(result), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in update_status_status: {e}")
        return jsonify({'error': str(e)}), 500

@status_bp.route('/baes/<int:baes_id>/type/<int:_erreur>', methods=['PUT'])
@swag_from({
    'tags': ['Status CRUD'],
    'description': "Modifie les détails d'une erreur identifiée par le BAES et le type d'erreur.",
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'baes_id',
            'in': 'path',
            'type': 'integer',
            'format': 'int64',
            'required': True,
            'description': "ID du BAES associé à l'erreur"
        },
        {
            'name': 'erreur',
            'in': 'path',
            'type': 'integer',
            'format': 'int64',
            'required': True,
            'description': "int 64 du type d'erreur (1 pour erreur_connexion, 2 pour erreur_batterie, etc.)"
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'is_solved': {'type': 'boolean', 'example': False},
                    'is_ignored': {'type': 'boolean', 'example': False}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': "Erreur modifiée avec succès.",
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'baes_id': {'type': 'integer', 'format': 'int64', 'example': 1},
                    'erreur': {'type': 'integer', 'example': 1},
                    'is_solved': {'type': 'boolean', 'example': False},
                    'is_ignored': {'type': 'boolean', 'example': False},
                    'timestamp': {'type': 'string', 'format': 'date-time', 'example': '2023-01-01T12:00:00Z'},
                    'acknowledged_by_user_id': {'type': 'integer', 'example': 1, 'nullable': True},
                    'acknowledged_at': {'type': 'string', 'format': 'date-time', 'example': '2023-01-02T14:30:00Z', 'nullable': True},
                    'acknowledged_by_login': {'type': 'string', 'example': 'user1', 'nullable': True}
                }
            }
        },
        400: {'description': "Mauvaise requête."},
        404: {'description': "Erreur non trouvée ou BAES non trouvé."}
    }
})
def update_status(baes_id, erreur):
    try:
        # Vérifier si le BAES existe
        from ..models.baes import Baes
        baes = Baes.query.get(baes_id)
        if not baes:
            return jsonify({'error': 'BAES non trouvé'}), 404

        # Rechercher l'erreur par baes_id et erreur
        status_obj = Status.query.filter_by(baes_id=baes_id, erreur=erreur).first()
        if not status_obj:
            return jsonify({'error': f'Erreur de type {erreur} non trouvée pour le BAES {baes_id}'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Aucune donnée fournie'}), 400

        # Mise à jour des champs
        if 'is_solved' in data:
            status_obj.is_solved = data['is_solved']

        if 'is_ignored' in data:
            status_obj.is_ignored = data['is_ignored']

        db.session.commit()

        # Récupérer le login de l'utilisateur qui a acquitté l'erreur
        acknowledged_by_login = None
        if status_obj.acknowledged_by_user_id:
            from ..models.user import User
            user = User.query.get(status_obj.acknowledged_by_user_id)
            if user:
                acknowledged_by_login = user.login

        result = {
            'id': status_obj.id,
            'baes_id': status_obj.baes_id,
            'erreur': status_obj.erreur,
            'is_solved': status_obj.is_solved,
            'is_ignored': status_obj.is_ignored,
            'temperature': status_obj.temperature,
            'vibration': status_obj.vibration,
            'timestamp': status_obj.timestamp.isoformat() if status_obj.timestamp else None,
            'acknowledged_by_user_id': status_obj.acknowledged_by_user_id,
            'acknowledged_at': status_obj.acknowledged_at.isoformat() if status_obj.acknowledged_at else None,
            'acknowledged_by_login': acknowledged_by_login
        }
        return jsonify(result), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in update_status: {e}")
        return jsonify({'error': str(e)}), 500

@status_bp.route('/acknowledged', methods=['GET'])
@swag_from({
    'tags': ['Status CRUD'],
    'description': "Récupère la liste des erreurs acquittées avec les informations sur qui les a acquittées.",
    'responses': {
        200: {
            'description': "Liste des erreurs acquittées.",
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'example': 1},
                        'baes_id': {'type': 'integer', 'format': 'int64', 'example': 1},
                        'erreur': {'type': 'integer', 'example': 1},
                        'is_solved': {'type': 'boolean', 'example': True},
                        'is_ignored': {'type': 'boolean', 'example': False},
                        'temperature': {'type': 'number', 'format': 'float', 'example': 25.5, 'nullable': True},
                        'vibration': {'type': 'boolean', 'example': True, 'nullable': True},
                        'timestamp': {'type': 'string', 'format': 'date-time', 'example': '2023-01-01T12:00:00Z'},
                        'updated_at': {'type': 'string', 'format': 'date-time', 'example': '2023-01-01T12:00:00Z'},
                        'acknowledged_by_user_id': {'type': 'integer', 'example': 1},
                        'acknowledged_at': {'type': 'string', 'format': 'date-time', 'example': '2023-01-02T14:30:00Z'},
                        'acknowledged_by_login': {'type': 'string', 'example': 'user1'}
                    }
                }
            }
        },
        500: {'description': 'Erreur interne.'}
    }
})
def get_acknowledged_statuses():
    try:
        # Récupérer toutes les erreurs qui ont été acquittées
        statuses = Status.query.filter(Status.acknowledged_by_user_id.isnot(None)).all()

        result = []
        for e in statuses:
            # Récupérer le login de l'utilisateur qui a acquitté l'erreur
            acknowledged_by_login = None
            if e.acknowledged_by_user_id:
                from ..models.user import User
                user = User.query.get(e.acknowledged_by_user_id)
                if user:
                    acknowledged_by_login = user.login

            result.append({
                'id': e.id,
                'baes_id': e.baes_id,
                'erreur': e.erreur,
                'is_solved': e.is_solved,
                'is_ignored': e.is_ignored,
                'temperature': e.temperature,
                'vibration': e.vibration,
                'timestamp': e.timestamp.isoformat() if e.timestamp else None,
                'updated_at': e.updated_at.isoformat() if e.updated_at else None,
                'acknowledged_by_user_id': e.acknowledged_by_user_id,
                'acknowledged_at': e.acknowledged_at.isoformat() if e.acknowledged_at else None,
                'acknowledged_by_login': acknowledged_by_login
            })

        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_acknowledged_statuses: {e}")
        return jsonify({'error': str(e)}), 500

@status_bp.route('/etage/<int:etage_id>', methods=['GET'])
@swag_from({
    'tags': ['Status CRUD'],
    'description': "Récupère toutes les erreurs de tous les BAES présents dans un étage spécifique.",
    'parameters': [
        {
            'name': 'etage_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID de l'étage dont on veut récupérer les erreurs de tous les BAES"
        }
    ],
    'responses': {
        200: {
            'description': "Liste des erreurs pour tous les BAES de l'étage spécifié.",
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'example': 1},
                        'baes_id': {'type': 'integer', 'format': 'int64', 'example': 1},
                        'baes_name': {'type': 'string', 'example': 'BAES-001'},
                        'erreur': {'type': 'integer', 'example': 1},
                        'is_solved': {'type': 'boolean', 'example': False},
                        'is_ignored': {'type': 'boolean', 'example': False},
                        'temperature': {'type': 'number', 'format': 'float', 'example': 25.5, 'nullable': True},
                        'vibration': {'type': 'boolean', 'example': True, 'nullable': True},
                        'timestamp': {'type': 'string', 'format': 'date-time', 'example': '2023-01-01T12:00:00Z'},
                        'updated_at': {'type': 'string', 'format': 'date-time', 'example': '2023-01-01T12:00:00Z'},
                        'acknowledged_by_user_id': {'type': 'integer', 'example': 1, 'nullable': True},
                        'acknowledged_at': {'type': 'string', 'format': 'date-time', 'example': '2023-01-02T14:30:00Z', 'nullable': True},
                        'acknowledged_by_login': {'type': 'string', 'example': 'user1', 'nullable': True}
                    }
                }
            }
        },
        404: {'description': "Étage non trouvé."},
        500: {'description': "Erreur interne."}
    }
})
def get_statuses_by_etage(etage_id):
    try:
        # Vérifier si l'étage existe
        from ..models.etage import Etage
        etage = Etage.query.get(etage_id)
        if not etage:
            return jsonify({'error': 'Étage non trouvé'}), 404

        # Récupérer tous les BAES de cet étage
        baes_list = Baes.query.filter_by(etage_id=etage_id).all()
        if not baes_list:
            return jsonify([]), 200  # Retourne une liste vide si aucun BAES n'est trouvé

        # Récupérer toutes les erreurs pour ces BAES
        result = []
        for baes in baes_list:
            statuses = Status.query.filter_by(baes_id=baes.id).all()
            for e in statuses:
                # Récupérer le login de l'utilisateur qui a acquitté l'erreur
                acknowledged_by_login = None
                if e.acknowledged_by_user_id:
                    from ..models.user import User
                    user = User.query.get(e.acknowledged_by_user_id)
                    if user:
                        acknowledged_by_login = user.login

                result.append({
                    'id': e.id,
                    'baes_id': e.baes_id,
                    'baes_name': baes.name,
                    'erreur': e.erreur,
                    'is_solved': e.is_solved,
                    'is_ignored': e.is_ignored,
                    'temperature': e.temperature,
                    'vibration': e.vibration,
                    'timestamp': e.timestamp.isoformat() if e.timestamp else None,
                    'updated_at': e.updated_at.isoformat() if e.updated_at else None,
                    'acknowledged_by_user_id': e.acknowledged_by_user_id,
                    'acknowledged_at': e.acknowledged_at.isoformat() if e.acknowledged_at else None,
                    'acknowledged_by_login': acknowledged_by_login
                })

        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_statuses_by_etage: {e}")
        return jsonify({'error': str(e)}), 500

@status_bp.route('/latest', methods=['GET'])
@swag_from({
    'tags': ['Status CRUD'],
    'description': "Récupère l'erreur la plus récemment modifiée ou créée.",
    'responses': {
        200: {
            'description': "Détails de l'erreur la plus récente.",
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'baes_id': {'type': 'integer', 'format': 'int64', 'example': 1},
                    'erreur': {'type': 'integer', 'example': 1},
                    'is_solved': {'type': 'boolean', 'example': False},
                    'is_ignored': {'type': 'boolean', 'example': False},
                    'temperature': {'type': 'number', 'format': 'float', 'example': 25.5, 'nullable': True},
                    'vibration': {'type': 'boolean', 'example': True, 'nullable': True},
                    'timestamp': {'type': 'string', 'format': 'date-time', 'example': '2023-01-01T12:00:00Z'},
                    'updated_at': {'type': 'string', 'format': 'date-time', 'example': '2023-01-01T12:00:00Z'},
                    'acknowledged_by_user_id': {'type': 'integer', 'example': 1, 'nullable': True},
                    'acknowledged_at': {'type': 'string', 'format': 'date-time', 'example': '2023-01-02T14:30:00Z', 'nullable': True},
                    'acknowledged_by_login': {'type': 'string', 'example': 'user1', 'nullable': True}
                }
            }
        },
        404: {'description': "Aucune erreur trouvée."}
    }
})
def get_latest_status():
    try:
        # Récupérer l'erreur la plus récente basée sur le timestamp
        status = Status.query.order_by(Status.updated_at.desc()).first()

        if not status:
            return jsonify({'error': 'Aucune erreur trouvée'}), 404

        # Récupérer le login de l'utilisateur qui a acquitté l'erreur
        acknowledged_by_login = None
        if status.acknowledged_by_user_id:
            from ..models.user import User
            user = User.query.get(status.acknowledged_by_user_id)
            if user:
                acknowledged_by_login = user.login

        result = {
            'id': status.id,
            'baes_id': status.baes_id,
            'erreur': status.erreur,
            'is_solved': status.is_solved,
            'is_ignored': status.is_ignored,
            'temperature': status.temperature,
            'vibration': status.vibration,
            'timestamp': status.timestamp.isoformat() if status.timestamp else None,
            'updated_at': status.updated_at.isoformat() if status.updated_at else None,
            'acknowledged_by_user_id': status.acknowledged_by_user_id,
            'acknowledged_at': status.acknowledged_at.isoformat() if status.acknowledged_at else None,
            'acknowledged_by_login': acknowledged_by_login
        }

        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_latest_status: {e}")
        return jsonify({'error': str(e)}), 500

@status_bp.route('/<int:status_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Status CRUD'],
    'description': "Supprime une erreur par son ID.",
    'parameters': [
        {
            'name': 'status_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID de l'erreur à supprimer"
        }
    ],
    'responses': {
        200: {
            'description': "Erreur supprimée avec succès.",
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Erreur supprimée avec succès'}
                }
            }
        },
        404: {'description': "Erreur non trouvée."}
    }
})
def delete_status(status_id):
    try:
        status = Status.query.get(status_id)
        if not status:
            return jsonify({'error': 'Erreur non trouvée'}), 404

        db.session.delete(status)
        db.session.commit()

        return jsonify({'message': 'Erreur supprimée avec succès'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in delete_status: {e}")
        return jsonify({'error': str(e)}), 500






@status_bp.route('/user/<int:user_id>', methods=['GET'])
@swag_from({
    'tags': ['Status CRUD'],
    'description': 'Récupère le dernier message de status pour chaque BAES visible par un utilisateur et chaque BAES non attribué à un étage.',
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID de l'utilisateur"
        }
    ],
    'responses': {
        200: {
            'description': 'Liste des BAES avec leur dernier status.',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'format': 'int64', 'example': 1},
                        'name': {'type': 'string', 'example': 'BAES 1'},
                        'label': {'type': 'string', 'example': 'Étiquette BAES 1'},
                        'position': {'type': 'object', 'example': {"x": 100, "y": 200}},
                        'etage_id': {'type': 'integer', 'example': 1, 'nullable': True},
                        'latest_status': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer', 'example': 1},
                                'erreur': {'type': 'integer', 'example': 1},
                                'is_solved': {'type': 'boolean', 'example': False},
                                'is_ignored': {'type': 'boolean', 'example': False},
                                'temperature': {'type': 'number', 'format': 'float', 'example': 25.5, 'nullable': True},
                                'vibration': {'type': 'boolean', 'example': True, 'nullable': True},
                                'timestamp': {'type': 'string', 'format': 'date-time', 'example': '2023-01-01T12:00:00Z'}
                            },
                            'nullable': True
                        }
                    }
                }
            }
        },
        404: {'description': 'Utilisateur non trouvé.'},
        500: {'description': 'Erreur interne.'}
    }
})
def get_status_by_user(user_id):
    """
    Récupère le dernier message de status pour chaque BAES visible par un utilisateur et chaque BAES non attribué à un étage.
    """
    try:
        # Vérifier si l'utilisateur existe
        from ..models.user import User
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404

        # 1. Récupérer tous les sites auxquels l'utilisateur a accès
        from ..models.site import Site
        from ..models.user_site_role import UserSiteRole
        sites = db.session.query(Site).join(
            UserSiteRole, UserSiteRole.site_id == Site.id
        ).filter(
            UserSiteRole.user_id == user_id
        ).distinct().all()

        site_ids = [site.id for site in sites]

        # 2. Récupérer tous les BAES visibles par l'utilisateur (dans les sites auxquels il a accès)
        from ..models.batiment import Batiment
        from ..models.etage import Etage
        visible_baes = db.session.query(Baes).join(
            Etage, Baes.etage_id == Etage.id
        ).join(
            Batiment, Etage.batiment_id == Batiment.id
        ).filter(
            Batiment.site_id.in_(site_ids)
        ).all()

        # 3. Récupérer tous les BAES non attribués à un étage
        unassigned_baes = Baes.query.filter_by(etage_id=None).all()

        # Combiner les deux listes de BAES (en évitant les doublons)
        all_baes = {b.id: b for b in visible_baes}
        for b in unassigned_baes:
            if b.id not in all_baes:
                all_baes[b.id] = b

        # 4. Pour chaque BAES, récupérer son dernier status
        result = []
        for baes_id, baes in all_baes.items():
            # Récupérer le dernier status pour ce BAES
            latest_status = Status.query.filter_by(baes_id=baes_id).order_by(Status.timestamp.desc()).first()
            
            baes_dict = {
                'id': baes.id,
                'name': baes.name,
                'label': baes.label,
                'position': baes.position,
                'etage_id': baes.etage_id,
                'latest_status': None
            }
            
            if latest_status:
                baes_dict['latest_status'] = {
                    'id': latest_status.id,
                    'erreur': latest_status.erreur,
                    'is_solved': latest_status.is_solved,
                    'is_ignored': latest_status.is_ignored,
                    'temperature': latest_status.temperature,
                    'vibration': latest_status.vibration,
                    'timestamp': latest_status.timestamp.isoformat() if latest_status.timestamp else None
                }
            
            result.append(baes_dict)
        
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_status_by_user: {e}")
        return jsonify({'error': str(e)}), 500
