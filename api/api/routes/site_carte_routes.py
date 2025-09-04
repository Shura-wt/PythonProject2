# routes/site_carte.py
import os
import uuid
from flask import Blueprint, request, jsonify, current_app, send_from_directory, url_for
from flasgger import swag_from
from werkzeug.utils import secure_filename
from ..models.site import Site
from ..models.carte import Carte
from ..models.etage import Etage
from ..models import db

def generate_unique_filename(original_filename):
    """Generate a unique filename using UUID while preserving the file extension."""
    # Get the file extension
    _, file_extension = os.path.splitext(original_filename)
    # Generate a random UUID
    random_id = str(uuid.uuid4())
    # Return the new filename with the original extension
    return f"{random_id}{file_extension}"

site_carte_bp = Blueprint('site_carte_bp', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@site_carte_bp.route('/<int:site_id>/assign', methods=['POST'])
@swag_from({
    'tags': ['assignation carte'],
    'description': "Assigne une carte existante à un site. Le JSON doit contenir 'card_id'.",
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'site_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID du site"
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'card_id': {'type': 'integer', 'example': 5}
                },
                'required': ['card_id']
            }
        }
    ],
    'responses': {
        200: {
            'description': "Carte assignée au site avec succès.",
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': "Carte assignée au site avec succès."}
                }
            }
        },
        400: {'description': "Carte déjà assignée ou champ manquant."},
        404: {'description': "Site ou carte non trouvé."},
        500: {'description': "Erreur interne."}
    }
})
def assign_card_to_site(site_id):
    try:
        site = Site.query.get(site_id)
        if not site:
            return jsonify({'error': 'Site non trouvé'}), 404

        data = request.get_json()
        if not data or 'card_id' not in data:
            return jsonify({'error': 'Le champ "card_id" est requis'}), 400

        card_id = data['card_id']
        card = Carte.query.get(card_id)
        if not card:
            return jsonify({'error': 'Carte non trouvée'}), 404

        # Vérifier que la carte n'est pas déjà assignée
        if card.etage_id is not None or card.site_id is not None:
            return jsonify({'error': 'Carte déjà assignée à un étage ou un site'}), 400

        card.site_id = site.id
        db.session.commit()
        return jsonify({'message': "Carte assignée au site avec succès."}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in assign_card_to_site: {e}")
        return jsonify({'error': str(e)}), 500

@site_carte_bp.route('/get_by_site/<int:site_id>', methods=['GET'])
@swag_from({
    'tags': ['carte crud'],
    'description': "Récupère la carte associée au site dont l'ID est fourni en paramètre.",
    'parameters': [
        {
            'name': 'site_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID du site"
        }
    ],
    'responses': {
        200: {
            'description': "Carte associée au site.",
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 5},
                    'chemin': {'type': 'string', 'example': "/path/to/image.png"},
                    'center_lat': {'type': 'number', 'example': 0.1},
                    'center_lng': {'type': 'number', 'example': 0.2},
                    'zoom': {'type': 'number', 'example': 1.0},
                    'etage_id': {'type': 'integer', 'example': None},
                    'site_id': {'type': 'integer', 'example': 1}
                }
            }
        },
        404: {'description': "Site ou carte non trouvé."},
        500: {'description': "Erreur interne."}
    }
})
def get_cart_by_site_id(site_id):
    try:
        site = Site.query.get(site_id)
        if not site:
            return jsonify({'error': 'Site non trouvé'}), 404

        carte = Carte.query.filter_by(site_id=site.id).first()
        if not carte:
            return jsonify({'error': 'Aucune carte trouvée pour ce site'}), 404

        # Générer une URL d'accès publique pour l'image
        filename = os.path.basename(carte.chemin)
        chemin_url = url_for('carte_bp.uploaded_file', filename=filename, _external=True)

        result = {
            'id': carte.id,
            'chemin': chemin_url,
            'center_lat': carte.center_lat,
            'center_lng': carte.center_lng,
            'zoom': carte.zoom,
            'etage_id': carte.etage_id,
            'site_id': carte.site_id
        }
        return jsonify(result), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in get_cart_by_site_id: {e}")
        return jsonify({'error': str(e)}), 500

@site_carte_bp.route('/get_by_floor/<int:floor_id>', methods=['GET'])
@swag_from({
    'tags': ['carte crud'],
    'description': "Récupère la carte associée à l'étage dont l'ID est fourni en paramètre.",
    'parameters': [
        {
            'name': 'floor_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID de l'étage"
        }
    ],
    'responses': {
        200: {
            'description': "Carte associée à l'étage.",
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 3},
                    'chemin': {'type': 'string', 'example': "/path/to/floor_image.png"},
                    'center_lat': {'type': 'number', 'example': 0.3},
                    'center_lng': {'type': 'number', 'example': 0.4},
                    'zoom': {'type': 'number', 'example': 1.2},
                    'etage_id': {'type': 'integer', 'example': 2},
                    'site_id': {'type': 'integer', 'example': None}
                }
            }
        },
        404: {'description': "Étape ou carte non trouvé."},
        500: {'description': "Erreur interne."}
    }
})
def get_carte_by_floor_id(floor_id):
    try:
        etage = Etage.query.get(floor_id)
        if not etage:
            return jsonify({'error': 'Étape non trouvée'}), 404

        carte = Carte.query.filter_by(etage_id=etage.id).first()
        if not carte:
            return jsonify({'error': 'Aucune carte trouvée pour cet étage'}), 404

        # Générer une URL d'accès publique pour l'image
        filename = os.path.basename(carte.chemin)
        chemin_url = url_for('carte_bp.uploaded_file', filename=filename, _external=True)

        result = {
            'id': carte.id,
            'chemin': chemin_url,
            'center_lat': carte.center_lat,
            'center_lng': carte.center_lng,
            'zoom': carte.zoom,
            'etage_id': carte.etage_id,
            'site_id': carte.site_id
        }
        return jsonify(result), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in get_carte_by_floor_id: {e}")
        return jsonify({'error': str(e)}), 500

@site_carte_bp.route('/update_by_site/<int:site_id>', methods=['PUT'])
@swag_from({
    'tags': ['carte crud'],
    'description': "Met à jour une carte existante associée à un site. "
                   "Vous pouvez mettre à jour l'image, les coordonnées du centre et le zoom. "
                   "Si vous fournissez un nouveau fichier, l'ancien sera remplacé.",
    'consumes': ['multipart/form-data'],
    'parameters': [
        {
            'name': 'site_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID du site dont la carte sera mise à jour."
        },
        {
            'name': 'file',
            'in': 'formData',
            'type': 'file',
            'required': False,
            'description': 'Nouveau fichier image de la carte (png, jpg, etc.)'
        },
        {
            'name': 'center_lat',
            'in': 'formData',
            'type': 'number',
            'required': False,
            'description': 'Nouvelle latitude du centre de la carte'
        },
        {
            'name': 'center_lng',
            'in': 'formData',
            'type': 'number',
            'required': False,
            'description': 'Nouvelle longitude du centre de la carte'
        },
        {
            'name': 'zoom',
            'in': 'formData',
            'type': 'number',
            'required': False,
            'description': 'Nouveau niveau de zoom de la carte'
        }
    ],
    'responses': {
        200: {
            'description': 'Carte mise à jour avec succès.',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Carte mise à jour avec succès'},
                    'carte': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer', 'example': 1},
                            'chemin': {'type': 'string', 'example': 'http://localhost:5000/uploads/vue_site.jpg'},
                            'center_lat': {'type': 'number', 'example': 48.8566},
                            'center_lng': {'type': 'number', 'example': 2.3522},
                            'zoom': {'type': 'number', 'example': 1.0},
                            'site_id': {'type': 'integer', 'example': 3},
                            'etage_id': {'type': 'integer', 'example': None}
                        }
                    }
                }
            }
        },
        400: {'description': 'Erreur de requête ou paramètres invalides.'},
        404: {'description': 'Site ou carte non trouvé.'}
    }
})
def update_carte_by_site_id(site_id):
    try:
        # Vérifier que le site existe
        site = Site.query.get(site_id)
        if not site:
            return jsonify({'error': 'Site non trouvé'}), 404

        # Récupérer la carte associée au site
        carte = Carte.query.filter_by(site_id=site.id).first()
        if not carte:
            return jsonify({'error': 'Aucune carte trouvée pour ce site'}), 404

        # Vérifier si un nouveau fichier est fourni
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            if not allowed_file(file.filename):
                return jsonify({'error': 'Extension de fichier non autorisée'}), 400

            # Sauvegarder le nouveau fichier
            # Secure the original filename
            original_filename = secure_filename(file.filename)
            # Generate a unique filename with UUID
            unique_filename = generate_unique_filename(original_filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)

            # Mettre à jour le chemin de la carte
            carte.chemin = file_path

        # Traitement des paramètres (center_lat, center_lng, zoom)
        try:
            if 'center_lat' in request.form:
                carte.center_lat = float(request.form.get('center_lat'))
            if 'center_lng' in request.form:
                carte.center_lng = float(request.form.get('center_lng'))
            if 'zoom' in request.form:
                carte.zoom = float(request.form.get('zoom'))
        except ValueError:
            return jsonify({'error': 'Paramètres invalides pour la configuration de la carte'}), 400

        # Sauvegarder les modifications
        db.session.commit()

        # Générer une URL d'accès publique pour l'image
        filename = os.path.basename(carte.chemin)
        chemin_url = url_for('carte_bp.uploaded_file', filename=filename, _external=True)

        return jsonify({
            'message': 'Carte mise à jour avec succès',
            'carte': {
                'id': carte.id,
                'chemin': chemin_url,
                'center_lat': carte.center_lat,
                'center_lng': carte.center_lng,
                'zoom': carte.zoom,
                'site_id': carte.site_id,
                'etage_id': carte.etage_id
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in update_carte_by_site_id: {e}")
        return jsonify({'error': str(e)}), 500
