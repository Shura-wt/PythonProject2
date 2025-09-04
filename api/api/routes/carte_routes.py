import os
import uuid
from flask import Blueprint, request, jsonify, current_app, send_from_directory, url_for
from werkzeug.utils import secure_filename
from flasgger import swag_from
from ..models.carte import Carte
from ..models import db

def generate_unique_filename(original_filename):
    """Generate a unique filename using UUID while preserving the file extension."""
    # Get the file extension
    _, file_extension = os.path.splitext(original_filename)
    # Generate a random UUID
    random_id = str(uuid.uuid4())
    # Return the new filename with the original extension
    return f"{random_id}{file_extension}"

carte_bp = Blueprint('carte_bp', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@carte_bp.route('/upload-carte', methods=['POST'])
@swag_from({
    'tags': ['carte crud'],
    'description': "Upload d'une carte avec ses paramètres (centre, zoom) et son association à un site ou un étage. "
                   "Vous devez fournir l'ID du site (`site_id`) ou l'ID de l'étage (`etage_id`), mais pas les deux. "
                   "La réponse renvoie une URL accessible pour l'image uploadée.",
    'consumes': ['multipart/form-data'],
    'parameters': [
        {
            'name': 'file',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': 'Fichier image de la carte (png, jpg, etc.)'
        },
        {
            'name': 'center_lat',
            'in': 'formData',
            'type': 'number',
            'required': False,
            'default': 0.0,
            'description': 'Latitude du centre de la carte'
        },
        {
            'name': 'center_lng',
            'in': 'formData',
            'type': 'number',
            'required': False,
            'default': 0.0,
            'description': 'Longitude du centre de la carte'
        },
        {
            'name': 'zoom',
            'in': 'formData',
            'type': 'number',
            'required': False,
            'default': 1.0,
            'description': 'Niveau de zoom de la carte'
        },
        {
            'name': 'site_id',
            'in': 'formData',
            'type': 'integer',
            'required': False,
            'description': 'ID du site auquel la carte sera associée (si la carte est liée à un site)'
        },
        {
            'name': 'etage_id',
            'in': 'formData',
            'type': 'integer',
            'required': False,
            'description': "ID de l'étage auquel la carte sera associée (si la carte est liée à un étage)"
        }
    ],
    'responses': {
        200: {
            'description': 'Fichier uploadé avec succès, carte sauvegardée avec une URL accessible pour l\'image.',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Fichier uploadé avec succès'},
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
        400: {'description': 'Erreur de requête, fichier non fourni, paramètres invalides ou aucune association renseignée.'}
    }
})
def upload_carte():
    # Vérifier la présence du fichier dans la requête
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier fourni'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nom de fichier vide'}), 400

    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Extension de fichier non autorisée'}), 400

    # Secure the original filename
    original_filename = secure_filename(file.filename)
    # Generate a unique filename with UUID
    unique_filename = generate_unique_filename(original_filename)
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, unique_filename)
    file.save(file_path)

    # Traitement des paramètres (center_lat, center_lng, zoom)
    try:
        center_lat = float(request.form.get('center_lat', 0.0))
        center_lng = float(request.form.get('center_lng', 0.0))
        zoom = float(request.form.get('zoom', 1.0))
    except ValueError:
        return jsonify({'error': 'Paramètres invalides pour la configuration de la carte'}), 400

    # Récupérer les associations
    site_id = request.form.get('site_id')
    etage_id = request.form.get('etage_id')
    site_id = int(site_id) if site_id not in (None, '') else None
    etage_id = int(etage_id) if etage_id not in (None, '') else None

    if (site_id is None and etage_id is None) or (site_id is not None and etage_id is not None):
        return jsonify({'error': 'Vous devez fournir soit site_id, soit etage_id (mais pas les deux)'}), 400

    try:
        # Vérifier si une carte existe déjà pour ce site ou cet étage
        existing_carte = None
        if site_id is not None:
            existing_carte = Carte.query.filter_by(site_id=site_id).first()
        elif etage_id is not None:
            existing_carte = Carte.query.filter_by(etage_id=etage_id).first()

        if existing_carte:
            # Mettre à jour la carte existante
            existing_carte.chemin = file_path
            existing_carte.center_lat = center_lat
            existing_carte.center_lng = center_lng
            existing_carte.zoom = zoom
            carte = existing_carte
            db.session.commit()
        else:
            # Créer une nouvelle carte
            carte = Carte(
                chemin=file_path,
                center_lat=center_lat,
                center_lng=center_lng,
                zoom=zoom,
                site_id=site_id,
                etage_id=etage_id
            )
            db.session.add(carte)
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de la sauvegarde de la carte: {str(e)}'}), 500

    # Générer une URL d'accès publique pour l'image à partir du nom de fichier
    chemin_url = url_for('carte_bp.uploaded_file', filename=unique_filename, _external=True)

    return jsonify({
        'message': 'Fichier uploadé avec succès',
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

@carte_bp.route('/uploads/<path:filename>')
@swag_from({
    'tags': ['carte crud'],
    'description': "Retourne le fichier image uploadé à partir du nom de fichier fourni.",
    'parameters': [
        {
            'name': 'filename',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': "Nom du fichier à servir."
        }
    ],
    'responses': {
        200: {
            'description': "Fichier image renvoyé avec succès."
        },
        404: {
            'description': "Fichier non trouvé."
        }
    }
})
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@carte_bp.route('/carte/<int:carte_id>', methods=['GET'])
@swag_from(
    {
        'tags': ['carte crud'],
        'description': "Retourne le fichier image uploadé à partir de l'id de la carte",
        'parameters': [
            {
                'name': 'carte_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': "ID de la carte dont on veut récupérer l'image."
            }
        ],
        'responses': {
            200: {
                'description': "Fichier image renvoyé avec succès."
            },
            404: {
                'description': "Fichier non trouvé."
            }
        }

    }
)

def get_carte_by_id(carte_id):
    carte = Carte.query.get(carte_id)
    if carte is None:
        return jsonify({'error': 'Carte non trouvée'}), 404

    # Générer une URL d'accès publique pour l'image
    filename = os.path.basename(carte.chemin)
    chemin_url = url_for('carte_bp.uploaded_file', filename=filename, _external=True)

    return jsonify({
        'id': carte.id,
        'chemin': chemin_url,
        'center_lat': carte.center_lat,
        'center_lng': carte.center_lng,
        'zoom': carte.zoom,
        'site_id': carte.site_id,
        'etage_id': carte.etage_id
    })

@carte_bp.route('/carte/<int:carte_id>', methods=['PUT'])
@swag_from({
    'tags': ['carte crud'],
    'description': "Met à jour une carte existante avec de nouveaux paramètres. "
                   "Vous pouvez mettre à jour l'image, les coordonnées du centre, le zoom, "
                   "et l'association à un site ou un étage. "
                   "Si vous fournissez un nouveau fichier, l'ancien sera remplacé.",
    'consumes': ['multipart/form-data'],
    'parameters': [
        {
            'name': 'carte_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID de la carte à mettre à jour."
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
        },
        {
            'name': 'site_id',
            'in': 'formData',
            'type': 'integer',
            'required': False,
            'description': 'Nouvel ID du site auquel la carte sera associée (si la carte est liée à un site)'
        },
        {
            'name': 'etage_id',
            'in': 'formData',
            'type': 'integer',
            'required': False,
            'description': "Nouvel ID de l'étage auquel la carte sera associée (si la carte est liée à un étage)"
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
        400: {'description': 'Erreur de requête, paramètres invalides ou association incorrecte.'},
        404: {'description': 'Carte non trouvée.'}
    }
})
def update_carte(carte_id):
    # Récupérer la carte existante
    carte = Carte.query.get(carte_id)
    if carte is None:
        return jsonify({'error': 'Carte non trouvée'}), 404

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
        # Stocker le chemin complet pour la cohérence avec la méthode d'upload
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

    # Récupérer les associations
    site_id = request.form.get('site_id')
    etage_id = request.form.get('etage_id')

    # Mettre à jour les associations seulement si elles sont fournies
    if site_id is not None or etage_id is not None:
        site_id = int(site_id) if site_id not in (None, '') else None
        etage_id = int(etage_id) if etage_id not in (None, '') else None

        if (site_id is None and etage_id is None) or (site_id is not None and etage_id is not None):
            return jsonify({'error': 'Vous devez fournir soit site_id, soit etage_id (mais pas les deux)'}), 400

        carte.site_id = site_id
        carte.etage_id = etage_id

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de la mise à jour de la carte: {str(e)}'}), 500

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
