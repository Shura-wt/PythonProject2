# routes/etage_carte.py
import os
import uuid
from flask import Blueprint, request, jsonify, current_app, url_for
from flasgger import swag_from
from werkzeug.utils import secure_filename
from ..models.etage import Etage
from ..models.carte import Carte
from ..models.site import Site
from ..models import db

def generate_unique_filename(original_filename):
    """Generate a unique filename using UUID while preserving the file extension."""
    # Get the file extension
    _, file_extension = os.path.splitext(original_filename)
    # Generate a random UUID
    random_id = str(uuid.uuid4())
    # Return the new filename with the original extension
    return f"{random_id}{file_extension}"

etage_carte_bp = Blueprint('etage_carte_bp', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@etage_carte_bp.route('/<int:etage_id>/assign', methods=['POST'])
@swag_from({
    'tags': ['assignation carte'],
    'description': "Assigne une carte existante à un étage. Le JSON doit contenir 'card_id'.",
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'etage_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID de l'étage"
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'card_id': {'type': 'integer', 'example': 3}
                },
                'required': ['card_id']
            }
        }
    ],
    'responses': {
        200: {
            'description': "Carte assignée à l'étage avec succès.",
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': "Carte assignée à l'étage avec succès."}
                }
            }
        },
        400: {'description': "Carte déjà assignée ou champ manquant."},
        404: {'description': "Étage ou carte non trouvé."},
        500: {'description': "Erreur interne."}
    }
})
def assign_card_to_etage(etage_id):
    try:
        etage = Etage.query.get(etage_id)
        if not etage:
            return jsonify({'error': 'Étage non trouvé'}), 404

        data = request.get_json()
        if not data or 'card_id' not in data:
            return jsonify({'error': 'Le champ "card_id" est requis'}), 400

        card_id = data['card_id']
        card = Carte.query.get(card_id)
        if not card:
            return jsonify({'error': 'Carte non trouvée'}), 404

        # Vérifier si la carte est déjà attribuée (à un étage ou à un site)
        if card.etage_id is not None or card.site_id is not None:
            return jsonify({'error': 'Carte déjà assignée à un étage ou un site'}), 400

        card.etage_id = etage.id
        db.session.commit()
        return jsonify({'message': "Carte assignée à l'étage avec succès."}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in assign_card_to_etage: {e}")
        return jsonify({'error': str(e)}), 500

@etage_carte_bp.route('/update_by_site_etage/<int:site_id>/<int:etage_id>', methods=['PUT'])
@swag_from({
    'tags': ['carte crud'],
    'description': "Met à jour une carte existante associée à un étage d'un site spécifique. "
                   "Vous pouvez mettre à jour l'image, les coordonnées du centre et le zoom. "
                   "Si vous fournissez un nouveau fichier, l'ancien sera remplacé.",
    'consumes': ['multipart/form-data'],
    'parameters': [
        {
            'name': 'site_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID du site"
        },
        {
            'name': 'etage_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID de l'étage dont la carte sera mise à jour"
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
                            'chemin': {'type': 'string', 'example': 'http://localhost:5000/uploads/etage_carte.jpg'},
                            'center_lat': {'type': 'number', 'example': 48.8566},
                            'center_lng': {'type': 'number', 'example': 2.3522},
                            'zoom': {'type': 'number', 'example': 1.0},
                            'site_id': {'type': 'integer', 'example': None},
                            'etage_id': {'type': 'integer', 'example': 2}
                        }
                    }
                }
            }
        },
        400: {'description': 'Erreur de requête ou paramètres invalides.'},
        404: {'description': 'Site, étage ou carte non trouvé.'}
    }
})
def update_carte_by_site_etage_id(site_id, etage_id):
    try:
        # Vérifier que le site existe
        site = Site.query.get(site_id)
        if not site:
            return jsonify({'error': 'Site non trouvé'}), 404

        # Vérifier que l'étage existe et appartient au site spécifié
        etage = Etage.query.get(etage_id)
        if not etage:
            return jsonify({'error': 'Étage non trouvé'}), 404

        # Vérifier que l'étage appartient au site spécifié
        batiment = etage.batiment
        if not batiment or batiment.site_id != site_id:
            return jsonify({'error': 'Cet étage n\'appartient pas au site spécifié'}), 400

        # Récupérer la carte associée à l'étage
        carte = Carte.query.filter_by(etage_id=etage.id).first()
        if not carte:
            return jsonify({'error': 'Aucune carte trouvée pour cet étage'}), 404

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
        current_app.logger.error(f"Error in update_carte_by_site_etage_id: {e}")
        return jsonify({'error': str(e)}), 500
