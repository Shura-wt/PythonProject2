# routes/etage_routes.py
from flask import Blueprint, request, jsonify, current_app
from flasgger import swag_from
from ..models.etage import Etage
from ..models.baes import Baes
from ..models.carte import Carte
from ..models import db
from .general_routes import status_to_dict

etage_bp = Blueprint('etage_bp', __name__)

@etage_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['Etage CRUD'],
    'description': 'Récupère la liste de tous les étages.',
    'responses': {
        200: {
            'description': 'Liste des étages.',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'example': 1},
                        'name': {'type': 'string', 'example': 'Etage 1'},
                        'batiment_id': {'type': 'integer', 'example': 1}
                    }
                }
            }
        },
        500: {'description': 'Erreur interne.'}
    }
})
def get_etages():
    try:
        etages = Etage.query.all()
        result = [{'id': e.id, 'name': e.name, 'batiment_id': e.batiment_id} for e in etages]
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_etages: {e}")
        return jsonify({'error': str(e)}), 500

@etage_bp.route('/<int:etage_id>', methods=['GET'])
@swag_from({
    'tags': ['Etage CRUD'],
    'description': 'Récupère un étage par son ID.',
    'parameters': [
        {
            'name': 'etage_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID de l'étage à récupérer"
        }
    ],
    'responses': {
        200: {
            'description': "Détails de l'étage.",
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'name': {'type': 'string', 'example': 'Etage 1'},
                    'batiment_id': {'type': 'integer', 'example': 1}
                }
            }
        },
        404: {'description': "Étage non trouvé."}
    }
})
def get_etage(etage_id):
    try:
        etage = Etage.query.get(etage_id)
        if not etage:
            return jsonify({'error': "Étage non trouvé"}), 404
        result = {'id': etage.id, 'name': etage.name, 'batiment_id': etage.batiment_id}
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_etage: {e}")
        return jsonify({'error': str(e)}), 500

@etage_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['Etage CRUD'],
    'description': "Crée un nouvel étage.",
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'example': 'Etage 1'},
                    'batiment_id': {'type': 'integer', 'example': 1}
                },
                'required': ['name', 'batiment_id']
            }
        }
    ],
    'responses': {
        201: {
            'description': "Étage créé avec succès.",
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'name': {'type': 'string', 'example': 'Etage 1'},
                    'batiment_id': {'type': 'integer', 'example': 1}
                }
            }
        },
        400: {'description': "Mauvaise requête."}
    }
})
def create_etage():
    try:
        data = request.get_json()
        if not data or 'name' not in data or 'batiment_id' not in data:
            return jsonify({'error': 'Les champs name et batiment_id sont requis'}), 400
        etage = Etage(name=data['name'], batiment_id=data['batiment_id'])
        db.session.add(etage)
        db.session.commit()
        result = {'id': etage.id, 'name': etage.name, 'batiment_id': etage.batiment_id}
        return jsonify(result), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in create_etage: {e}")
        return jsonify({'error': str(e)}), 500

@etage_bp.route('/<int:etage_id>', methods=['PUT'])
@swag_from({
    'tags': ['Etage CRUD'],
    'description': "Met à jour un étage existant par son ID.",
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'etage_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID de l'étage à mettre à jour"
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'example': 'Etage mis à jour'},
                    'batiment_id': {'type': 'integer', 'example': 2}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': "Étage mis à jour avec succès.",
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'name': {'type': 'string', 'example': 'Etage mis à jour'},
                    'batiment_id': {'type': 'integer', 'example': 2}
                }
            }
        },
        404: {'description': "Étage non trouvé."}
    }
})
def update_etage(etage_id):
    try:
        etage = Etage.query.get(etage_id)
        if not etage:
            return jsonify({'error': "Étage non trouvé"}), 404
        data = request.get_json()
        if 'name' in data:
            etage.name = data['name']
        if 'batiment_id' in data:
            etage.batiment_id = data['batiment_id']
        db.session.commit()
        result = {'id': etage.id, 'name': etage.name, 'batiment_id': etage.batiment_id}
        return jsonify(result), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in update_etage: {e}")
        return jsonify({'error': str(e)}), 500

@etage_bp.route('/<int:etage_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Etage CRUD'],
    'description': "Supprime un étage par son ID, met à jour les BAES associés (etage_id = null) et supprime la carte associée.",
    'parameters': [
        {
            'name': 'etage_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID de l'étage à supprimer"
        }
    ],
    'responses': {
        200: {
            'description': "Étage supprimé avec succès.",
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Étage supprimé avec succès'},
                    'baes_updated': {'type': 'integer', 'example': 3},
                    'carte_deleted': {'type': 'integer', 'example': 1}
                }
            }
        },
        404: {'description': "Étage non trouvé."}
    }
})
def delete_etage(etage_id):
    try:
        etage = Etage.query.get(etage_id)
        if not etage:
            return jsonify({'error': "Étage non trouvé"}), 404

        # Supprimer la carte associée à cet étage, si elle existe
        carte = Carte.query.filter_by(etage_id=etage_id).first()
        carte_deleted = 0
        if carte:
            db.session.delete(carte)
            carte_deleted = 1

        # Récupérer tous les BAES associés à cet étage
        baes_list = Baes.query.filter_by(etage_id=etage_id).all()
        baes_count = len(baes_list)

        # Mettre à jour les BAES pour définir etage_id à null au lieu de les supprimer
        for baes in baes_list:
            baes.etage_id = None

        # Supprimer l'étage
        db.session.delete(etage)
        db.session.commit()

        return jsonify({
            'message': 'Étage supprimé avec succès',
            'baes_updated': baes_count,
            'carte_deleted': carte_deleted
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in delete_etage: {e}")
        return jsonify({'error': str(e)}), 500

@etage_bp.route('/<int:etage_id>/baes', methods=['GET'])
@swag_from({
    'tags': ['Etage CRUD'],
    'description': 'Récupère tous les BAES d\'un étage par son ID.',
    'parameters': [
        {
            'name': 'etage_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID de l'étage dont on veut récupérer les BAES"
        }
    ],
    'responses': {
        200: {
            'description': "Liste des BAES de l'étage.",
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'format': 'int64', 'example': 1},
                        'name': {'type': 'string', 'example': 'BAES 1'},
                        'position': {'type': 'object', 'example': {"x": 100, "y": 200}},
                        'etage_id': {'type': 'integer', 'example': 1},
                        'erreurs': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'integer', 'example': 1},
                                    'erreur': {'type': 'integer', 'example': 1},
                                    'timestamp': {'type': 'string', 'example': "2025-04-03T12:34:56Z"},
                                    'is_solved': {'type': 'boolean', 'example': False},
                                    'is_ignored': {'type': 'boolean', 'example': False}
                                }
                            }
                        }
                    }
                }
            }
        },
        404: {'description': "Étage non trouvé."}
    }
})
def get_baes_by_etage_id(etage_id):
    try:
        etage = Etage.query.get(etage_id)
        if not etage:
            return jsonify({'error': "Étage non trouvé"}), 404

        baes_list = Baes.query.filter_by(etage_id=etage_id).all()
        result = [
            {
                'id': b.id, 
                'name': b.name, 
                'position': b.position, 
                'etage_id': b.etage_id,
                'erreurs': [status_to_dict(e) for e in b.statuses] if b.statuses else []
            } for b in baes_list
        ]
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_baes_by_etage_id: {e}")
        return jsonify({'error': str(e)}), 500
