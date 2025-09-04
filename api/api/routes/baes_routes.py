# routes/baes_routes.py
from flask import Blueprint, request, jsonify, current_app
from flasgger import swag_from
from ..models.baes import Baes
from ..models.user import User
from ..models.user_site_role import UserSiteRole
from ..models.site import Site
from ..models.batiment import Batiment
from ..models.etage import Etage
from ..models.status import Status
from ..models import db
from sqlalchemy import desc, func
from sqlalchemy.orm import aliased


baes_bp = Blueprint('baes_bp', __name__)

@baes_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['BAES CRUD'],
    'description': 'Récupère la liste de tous les BAES.',
    'responses': {
        200: {
            'description': 'Liste des BAES.',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'format': 'int64', 'example': 1},
                        'name': {'type': 'string', 'example': 'BAES 1'},
                        'label': {'type': 'string', 'example': 'Étiquette BAES 1'},
                        'position': {'type': 'object', 'example': {"x": 100, "y": 200}},
                        'etage_id': {'type': 'integer', 'example': 1}
                    }
                }
            }
        },
        500: {'description': 'Erreur interne.'}
    }
})
def get_baes():
    try:
        baes_list = Baes.query.all()
        result = [{
            'id': b.id,
            'name': b.name,
            'label': b.label,
            'position': b.position,
            'etage_id': b.etage_id
        } for b in baes_list]
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_baes: {e}")
        return jsonify({'error': str(e)}), 500

@baes_bp.route('/<int:baes_id>', methods=['GET'])
@swag_from({
    'tags': ['BAES CRUD'],
    'description': 'Récupère un BAES par son ID.',
    'parameters': [
        {
            'name': 'baes_id',
            'in': 'path',
            'type': 'integer',
            'format': 'int64',
            'required': True,
            'description': "ID du BAES à récupérer"
        }
    ],
    'responses': {
        200: {
            'description': "Détails du BAES.",
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'format': 'int64', 'example': 1},
                    'name': {'type': 'string', 'example': 'BAES 1'},
                    'label': {'type': 'string', 'example': 'Étiquette BAES 1'},
                    'position': {'type': 'object', 'example': {"x": 100, "y": 200}},
                    'etage_id': {'type': 'integer', 'example': 1}
                }
            }
        },
        404: {'description': "BAES non trouvé."}
    }
})
def get_baes_by_id(baes_id):
    try:
        baes = Baes.query.get(baes_id)
        if not baes:
            return jsonify({'error': 'BAES non trouvé'}), 404
        result = {
            'id': baes.id,
            'name': baes.name,
            'label': baes.label,
            'position': baes.position,
            'etage_id': baes.etage_id
        }
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_baes_by_id: {e}")
        return jsonify({'error': str(e)}), 500

@baes_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['BAES CRUD'],
    'description': "Crée un nouveau BAES.",
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'example': 'BAES 1'},
                    'label': {'type': 'string', 'example': 'Étiquette BAES 1'},
                    'position': {'type': 'object', 'example': {"x": 100, "y": 200}},
                    'etage_id': {'type': 'integer', 'example': 1}
                },
                'required': ['name', 'position', 'etage_id']
            }
        }
    ],
    'responses': {
        201: {
            'description': "BAES créé avec succès.",
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'format': 'int64', 'example': 1},
                    'name': {'type': 'string', 'example': 'BAES 1'},
                    'label': {'type': 'string', 'example': 'Étiquette BAES 1'},
                    'position': {'type': 'object', 'example': {"x": 100, "y": 200}},
                    'etage_id': {'type': 'integer', 'example': 1}
                }
            }
        },
        400: {'description': "Mauvaise requête."}
    }
})
def create_baes():
    try:
        data = request.get_json()
        if not data or 'name' not in data or 'position' not in data or 'etage_id' not in data:
            return jsonify({'error': 'Les champs name, position et etage_id sont requis'}), 400
        baes = Baes(
            name=data['name'],
            label=data.get('label'),
            position=data['position'],
            etage_id=data['etage_id']
        )
        db.session.add(baes)
        db.session.commit()
        result = {
            'id': baes.id,
            'name': baes.name,
            'label': baes.label,
            'position': baes.position,
            'etage_id': baes.etage_id
        }
        return jsonify(result), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in create_baes: {e}")
        return jsonify({'error': str(e)}), 500

@baes_bp.route('/<int:baes_id>', methods=['PUT'])
@swag_from({
    'tags': ['BAES CRUD'],
    'description': "Met à jour un BAES existant par son ID.",
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'baes_id',
            'in': 'path',
            'type': 'integer',
            'format': 'int64',
            'required': True,
            'description': "ID du BAES à mettre à jour"
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'example': 'BAES mis à jour'},
                    'label': {'type': 'string', 'example': 'Étiquette BAES mise à jour'},
                    'position': {'type': 'object', 'example': {"x": 150, "y": 250}},
                    'etage_id': {'type': 'integer', 'example': 2}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': "BAES mis à jour avec succès.",
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'format': 'int64', 'example': 1},
                    'name': {'type': 'string', 'example': 'BAES mis à jour'},
                    'label': {'type': 'string', 'example': 'Étiquette BAES mise à jour'},
                    'position': {'type': 'object', 'example': {"x": 150, "y": 250}},
                    'etage_id': {'type': 'integer', 'example': 2}
                }
            }
        },
        404: {'description': "BAES non trouvé."}
    }
})
def update_baes(baes_id):
    try:
        baes = Baes.query.get(baes_id)
        if not baes:
            return jsonify({'error': 'BAES non trouvé'}), 404
        data = request.get_json()
        if 'name' in data:
            baes.name = data['name']
        if 'label' in data:
            baes.label = data['label']
        if 'position' in data:
            baes.position = data['position']
        if 'etage_id' in data:
            baes.etage_id = data['etage_id']
        db.session.commit()
        result = {
            'id': baes.id,
            'name': baes.name,
            'label': baes.label,
            'position': baes.position,
            'etage_id': baes.etage_id
        }
        return jsonify(result), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in update_baes: {e}")
        return jsonify({'error': str(e)}), 500

@baes_bp.route('/<int:baes_id>', methods=['DELETE'])
@swag_from({
    'tags': ['BAES CRUD'],
    'description': "Supprime un BAES par son ID.",
    'parameters': [
        {
            'name': 'baes_id',
            'in': 'path',
            'type': 'integer',
            'format': 'int64',
            'required': True,
            'description': "ID du BAES à supprimer"
        }
    ],
    'responses': {
        200: {
            'description': "BAES supprimé avec succès.",
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'BAES supprimé avec succès'}
                }
            }
        },
        404: {'description': "BAES non trouvé."}
    }
})
def delete_baes(baes_id):
    try:
        baes = Baes.query.get(baes_id)
        if not baes:
            return jsonify({'error': 'BAES non trouvé'}), 404
        db.session.delete(baes)
        db.session.commit()
        return jsonify({'message': 'BAES supprimé avec succès'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in delete_baes: {e}")
        return jsonify({'error': str(e)}), 500


@baes_bp.route('/without-etage', methods=['GET'])
@swag_from({
    'tags': ['BAES CRUD'],
    'description': 'Récupère la liste de tous les BAES qui n\'ont pas d\'étage assigné (etage_id = null).',
    'responses': {
        200: {
            'description': 'Liste des BAES sans étage.',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'format': 'int64', 'example': 1},
                        'name': {'type': 'string', 'example': 'BAES 1'},
                        'label': {'type': 'string', 'example': 'Étiquette BAES 1'},
                        'position': {'type': 'object', 'example': {"x": 100, "y": 200}},
                        'etage_id': {'type': 'null', 'example': None}
                    }
                }
            }
        },
        500: {'description': 'Erreur interne.'}
    }
})
def get_baes_without_etage():
    try:
        baes_list = Baes.query.filter_by(etage_id=None).all()
        result = [{
            'id': b.id,
            'name': b.name,
            'label': b.label,
            'position': b.position,
            'etage_id': b.etage_id
        } for b in baes_list]
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_baes_without_etage: {e}")
        return jsonify({'error': str(e)}), 500

@baes_bp.route('/user/<int:user_id>', methods=['GET'])
@swag_from({
    'tags': ['BAES Operations'],
    'description': 'Récupère le dernier status de chaque BAES visible par un utilisateur et chaque BAES non attribué à un étage.',
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
def get_baes_by_user(user_id):
    """
    Récupère le dernier status de chaque BAES visible par un utilisateur et chaque BAES non attribué à un étage.
    """
    try:
        # Vérifier si l'utilisateur existe
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404

        # 1. Récupérer tous les sites auxquels l'utilisateur a accès
        sites = db.session.query(Site).join(
            UserSiteRole, UserSiteRole.site_id == Site.id
        ).filter(
            UserSiteRole.user_id == user_id
        ).distinct().all()

        site_ids = [site.id for site in sites]

        # 2. Récupérer tous les BAES visibles par l'utilisateur (dans les sites auxquels il a accès)
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
        current_app.logger.error(f"Error in get_baes_by_user: {e}")
        return jsonify({'error': str(e)}), 500
