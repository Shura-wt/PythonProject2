from flask import Blueprint, request, jsonify, current_app
from flasgger import swag_from
from ..models.config import Config
from ..models import db
from sqlalchemy.exc import IntegrityError


config_bp = Blueprint('config_bp', __name__)
@config_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['Configuration CRUD'],
    'description': 'Récupère la liste de toutes les configurations.',
    'responses': {
        200: {
            'description': 'Liste des configurations.',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'format': 'int64', 'example': 1},
                        'key': {'type': 'string', 'example': 'site_name'},
                        'value': {'type': 'string', 'example': 'Mon Site'}
                    }
                }
            }
        },
        500: {'description': 'Erreur interne.'}
    }
})
#routes to get all configurations
def get_configs():
    try:
        configs = Config.query.all()
        result = [{'id': c.id, 'key': c.key, 'value': c.value} for c in configs]
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_configs: {e}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['Configuration CRUD'],
    'description': 'Crée une nouvelle configuration.',
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'required': ['key', 'value'],
                    'properties': {
                        'key': {'type': 'string', 'example': 'site_name'},
                        'value': {'type': 'string', 'example': 'Mon Site'}
                    }
                }
            }
        }
    },
    'responses': {
        201: {
            'description': 'Configuration créée avec succès.',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'format': 'int64', 'example': 1},
                    'key': {'type': 'string', 'example': 'site_name'},
                    'value': {'type': 'string', 'example': 'Mon Site'}
                }
            }
        },
        400: {'description': 'Données invalides ou manquantes.'},
        409: {'description': 'Une configuration avec cette clé existe déjà.'},
        500: {'description': 'Erreur interne.'}
    }
})
#route to create a new configuration
def create_config():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'key' not in data or 'value' not in data:
            return jsonify({'error': 'Les champs "key" et "value" sont requis'}), 400
            
        # Create new config
        new_config = Config(
            key=data['key'],
            value=data['value']
        )
        
        db.session.add(new_config)
        db.session.commit()
        
        # Return the created config
        return jsonify({
            'id': new_config.id,
            'key': new_config.key,
            'value': new_config.value
        }), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Une configuration avec cette clé existe déjà'}), 409
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in create_config: {e}")
        return jsonify({'error': str(e)}), 500


#routes to modify a configuration
@config_bp.route('/<int:config_id>', methods=['PUT'])
@swag_from({
    'tags': ['Configuration CRUD'],
    'description': 'Modifie une configuration par son ID.',
    'parameters': [
        {
            'name': 'config_id',
            'in': 'path',
            'type': 'integer',
            'format': 'int64',
            'required': True,
            'description': "ID de la configuration à modifier"
        }
    ],
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'key': {'type': 'string', 'example': 'site_name'},
                        'value': {'type': 'string', 'example': 'Mon Site'}
                    }
                }
            }
        }
    },
    'responses': {
        200: {'description': 'Configuration modifiée avec succès.'},
        404: {'description': "Configuration non trouvée."},
        500: {'description': "Erreur interne."}
    }
})
def update_config(config_id):
    try:
        config = Config.query.get_or_404(config_id)
        data = request.get_json()
        config.key = data.get('key', config.key)
        config.value = data.get('value', config.value)
        db.session.commit()
        return jsonify({'message': 'Configuration updated successfully'}), 200
    except Exception as e:
        current_app.logger.error(f"Error in update_config: {e}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/key/<string:key>', methods=['GET'])
@swag_from({
    'tags': ['Configuration CRUD'],
    'description': 'Récupère une configuration par sa clé.',
    'parameters': [
        {
            'name': 'key',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': "Clé de la configuration à récupérer"
        }
    ],
    'responses': {
        200: {
            'description': 'Configuration récupérée avec succès.',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'format': 'int64', 'example': 1},
                    'key': {'type': 'string', 'example': 'site_name'},
                    'value': {'type': 'string', 'example': 'Mon Site'}
                }
            }
        },
        404: {'description': "Configuration non trouvée."},
        500: {'description': "Erreur interne."}
    }
})
def get_config_by_key(key):
    try:
        config = Config.query.filter_by(key=key).first()
        if not config:
            return jsonify({'error': f"Configuration avec la clé '{key}' non trouvée"}), 404
            
        return jsonify({
            'id': config.id,
            'key': config.key,
            'value': config.value
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_config_by_key: {e}")
        return jsonify({'error': str(e)}), 500