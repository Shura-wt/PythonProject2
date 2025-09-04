# routes/batiment_routes.py
from flask import Blueprint, request, jsonify, current_app
from flasgger import swag_from
from ..models.batiment import Batiment
from ..models.etage import Etage
from ..models.baes import Baes
from ..models.carte import Carte
from ..models import db


batiment_bp = Blueprint('batiment_bp', __name__)

@batiment_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['Batiment CRUD'],
    'description': 'Récupère la liste de tous les bâtiments.',
    'responses': {
        200: {
            'description': 'Liste des bâtiments.',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'example': 1},
                        'name': {'type': 'string', 'example': 'Batiment 1'},
                        'polygon_points': {'type': 'object'},
                        'site_id': {'type': 'integer', 'example': 1}
                    }
                }
            }
        },
        500: {'description': 'Erreur interne.'}
    }
})
def get_batiments():
    try:
        batiments = Batiment.query.all()
        result = [{
            'id': b.id,
            'name': b.name,
            'polygon_points': b.polygon_points,
            'site_id': b.site_id
        } for b in batiments]
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_batiments: {e}")
        return jsonify({'error': str(e)}), 500

@batiment_bp.route('/<int:batiment_id>', methods=['GET'])
@swag_from({
    'tags': ['Batiment CRUD'],
    'description': 'Récupère un bâtiment par son ID.',
    'parameters': [
        {
            'name': 'batiment_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID du bâtiment à récupérer"
        }
    ],
    'responses': {
        200: {
            'description': "Détails du bâtiment.",
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'name': {'type': 'string', 'example': 'Batiment 1'},
                    'polygon_points': {'type': 'object'},
                    'site_id': {'type': 'integer', 'example': 1}
                }
            }
        },
        404: {'description': "Bâtiment non trouvé."}
    }
})
def get_batiment(batiment_id):
    try:
        batiment = Batiment.query.get(batiment_id)
        if not batiment:
            return jsonify({'error': 'Bâtiment non trouvé'}), 404
        result = {
            'id': batiment.id,
            'name': batiment.name,
            'polygon_points': batiment.polygon_points,
            'site_id': batiment.site_id
        }
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_batiment: {e}")
        return jsonify({'error': str(e)}), 500

@batiment_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['Batiment CRUD'],
    'description': "Crée un nouveau bâtiment.",
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'example': 'Batiment 1'},
                    'polygon_points': {'type': 'object', 'example': {"points": [[0,0],[1,1]]}},
                    'site_id': {'type': 'integer', 'example': 1}
                },
                'required': ['name']
            }
        }
    ],
    'responses': {
        201: {
            'description': "Bâtiment créé avec succès.",
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'name': {'type': 'string', 'example': 'Batiment 1'},
                    'polygon_points': {'type': 'object'},
                    'site_id': {'type': 'integer', 'example': 1}
                }
            }
        },
        400: {'description': "Mauvaise requête."}
    }
})
def create_batiment():
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': 'Le champ name est requis'}), 400
        batiment = Batiment(
            name=data['name'],
            polygon_points=data.get('polygon_points'),
            site_id=data.get('site_id')
        )
        db.session.add(batiment)
        db.session.commit()
        result = {
            'id': batiment.id,
            'name': batiment.name,
            'polygon_points': batiment.polygon_points,
            'site_id': batiment.site_id
        }
        return jsonify(result), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in create_batiment: {e}")
        return jsonify({'error': str(e)}), 500

@batiment_bp.route('/<int:batiment_id>', methods=['PUT'])
@swag_from({
    'tags': ['Batiment CRUD'],
    'description': "Met à jour un bâtiment existant par son ID.",
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'batiment_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID du bâtiment à mettre à jour"
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'example': 'Batiment mis à jour'},
                    'polygon_points': {'type': 'object', 'example': {"points": [[1,1],[2,2]]}},
                    'site_id': {'type': 'integer', 'example': 2}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': "Bâtiment mis à jour avec succès.",
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'name': {'type': 'string', 'example': 'Batiment mis à jour'},
                    'polygon_points': {'type': 'object'},
                    'site_id': {'type': 'integer', 'example': 2}
                }
            }
        },
        404: {'description': "Bâtiment non trouvé."}
    }
})
def update_batiment(batiment_id):
    try:
        batiment = Batiment.query.get(batiment_id)
        if not batiment:
            return jsonify({'error': 'Bâtiment non trouvé'}), 404
        data = request.get_json()
        if 'name' in data:
            batiment.name = data['name']
        if 'polygon_points' in data:
            batiment.polygon_points = data['polygon_points']
        if 'site_id' in data:
            batiment.site_id = data['site_id']
        db.session.commit()
        result = {
            'id': batiment.id,
            'name': batiment.name,
            'polygon_points': batiment.polygon_points,
            'site_id': batiment.site_id
        }
        return jsonify(result), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in update_batiment: {e}")
        return jsonify({'error': str(e)}), 500

@batiment_bp.route('/<int:batiment_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Batiment CRUD'],
    'description': "Supprime un bâtiment par son ID.",
    'parameters': [
        {
            'name': 'batiment_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID du bâtiment à supprimer"
        }
    ],
    'responses': {
        200: {
            'description': "Bâtiment supprimé avec succès.",
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Bâtiment supprimé avec succès'}
                }
            }
        },
        404: {'description': "Bâtiment non trouvé."}
    }
})
def delete_batiment(batiment_id):
    try:
        batiment = Batiment.query.get(batiment_id)
        if not batiment:
            return jsonify({'error': 'Bâtiment non trouvé'}), 404

        # Récupérer tous les étages du bâtiment
        etages = Etage.query.filter_by(batiment_id=batiment_id).all()

        for etage in etages:
            # Détacher les BAES de cet étage (etage_id = NULL)
            baes_list = Baes.query.filter_by(etage_id=etage.id).all()
            for b in baes_list:
                b.etage_id = None

            # Supprimer la carte associée à l'étage (si elle existe)
            carte = Carte.query.filter_by(etage_id=etage.id).first()
            if carte:
                db.session.delete(carte)

            # Supprimer l'étage
            db.session.delete(etage)

        # Enfin, supprimer le bâtiment
        db.session.delete(batiment)
        db.session.commit()
        return jsonify({'message': 'Bâtiment supprimé avec succès'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in delete_batiment: {e}")
        return jsonify({'error': str(e)}), 500

@batiment_bp.route('/<int:batiment_id>/floors', methods=['GET'])
@swag_from({
    'tags': ['Batiment CRUD'],
    'description': 'Récupère tous les étages d\'un bâtiment par son ID.',
    'parameters': [
        {
            'name': 'batiment_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID du bâtiment dont on veut récupérer les étages"
        }
    ],
    'responses': {
        200: {
            'description': "Liste des étages du bâtiment.",
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
        404: {'description': "Bâtiment non trouvé."}
    }
})
def get_floors_by_batiment_id(batiment_id):
    try:
        batiment = Batiment.query.get(batiment_id)
        if not batiment:
            return jsonify({'error': 'Bâtiment non trouvé'}), 404

        etages = Etage.query.filter_by(batiment_id=batiment_id).all()
        result = [{'id': e.id, 'name': e.name, 'batiment_id': e.batiment_id} for e in etages]
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_floors_by_batiment_id: {e}")
        return jsonify({'error': str(e)}), 500
