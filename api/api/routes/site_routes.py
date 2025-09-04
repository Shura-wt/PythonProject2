# routes/site_routes.py
from flask import Blueprint, request, jsonify, current_app
from flasgger import swag_from
from ..models.site import Site
from ..models import db

site_bp = Blueprint('site_bp', __name__)

@site_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['Site CRUD'],
    'description': 'Récupère la liste de tous les sites.',
    'responses': {
        200: {
            'description': 'Liste des sites.',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'example': 1},
                        'name': {'type': 'string', 'example': 'Site 1'},
                    }
                }
            }
        },
        500: {'description': 'Erreur interne.'}
    }
})
def get_sites():
    try:
        sites = Site.query.all()
        result = [{'id': s.id, 'name': s.name} for s in sites]
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_sites: {e}")
        return jsonify({'error': str(e)}), 500

@site_bp.route('/<int:site_id>', methods=['GET'])
@site_bp.route('/<int:site_id>/', methods=['GET'])
@swag_from({
    'tags': ['Site CRUD'],
    'description': 'Récupère un site par son ID.',
    'parameters': [
        {
            'name': 'site_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID du site à récupérer'
        }
    ],
    'responses': {
        200: {
            'description': 'Détails du site.',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'name': {'type': 'string', 'example': 'Site 1'},
                }
            }
        },
        404: {'description': 'Site non trouvé.'}
    }
})
def get_site(site_id):
    try:
        site = Site.query.get(site_id)
        if not site:
            return jsonify({'error': 'Site non trouvé'}), 404
        result = {'id': site.id, 'name': site.name}
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_site: {e}")
        return jsonify({'error': str(e)}), 500

@site_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['Site CRUD'],
    'description': "Crée un nouveau site.",
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'example': 'Site 1'},
                },
                'required': ['name']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Site créé avec succès.',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'name': {'type': 'string', 'example': 'Site 1'},
                }
            }
        },
        400: {'description': 'Mauvaise requête.'}
    }
})
def create_site():
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': 'Les champs name est requis'}), 400
        site = Site(name=data['name'])
        db.session.add(site)
        db.session.commit()
        result = {'id': site.id, 'name': site.name}
        return jsonify(result), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in create_site: {e}")
        return jsonify({'error': str(e)}), 500

@site_bp.route('/<int:site_id>', methods=['PUT'])
@site_bp.route('/<int:site_id>/', methods=['PUT'])
@swag_from({
    'tags': ['Site CRUD'],
    'description': "Met à jour un site existant.",
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'site_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID du site à mettre à jour"
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'example': 'Site mis à jour'},
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Site mis à jour avec succès.',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'name': {'type': 'string', 'example': 'Site mis à jour'},
                }
            }
        },
        404: {'description': 'Site non trouvé.'}
    }
})
def update_site(site_id):
    try:
        site = Site.query.get(site_id)
        if not site:
            return jsonify({'error': 'Site non trouvé'}), 404
        data = request.get_json()
        if 'name' in data:
            site.name = data['name']
        db.session.commit()
        result = {'id': site.id, 'name': site.name}
        return jsonify(result), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in update_site: {e}")
        return jsonify({'error': str(e)}), 500

@site_bp.route('/<int:site_id>', methods=['DELETE'])
@site_bp.route('/<int:site_id>/', methods=['DELETE'])
@swag_from({
    'tags': ['Site CRUD'],
    'description': "Supprime un site par son ID et tous les éléments associés (bâtiments, étages, BAES, erreurs, cartes) en cascade. Les liaisons user-site-role sont conservées avec site_id=NULL pour maintenir les relations user-role.",
    'parameters': [
        {
            'name': 'site_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID du site à supprimer"
        }
    ],
    'responses': {
        200: {
            'description': 'Site supprimé avec succès.',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Site supprimé avec succès'},
                    'batiments_deleted': {'type': 'integer', 'example': 2},
                    'etages_deleted': {'type': 'integer', 'example': 5},
                    'baes_deleted': {'type': 'integer', 'example': 10},
                    'erreurs_deleted': {'type': 'integer', 'example': 15},
                    'cartes_deleted': {'type': 'integer', 'example': 3},
                    'user_site_roles_preserved': {'type': 'integer', 'example': 4}
                }
            }
        },
        404: {'description': 'Site non trouvé.'}
    }
})
def delete_site(site_id):
    try:
        site = Site.query.get(site_id)
        if not site:
            return jsonify({'error': 'Site non trouvé'}), 404

        # Initialiser les compteurs
        batiments_count = 0
        etages_count = 0
        baes_count = 0
        statuses_count = 0
        cartes_count = 0
        user_site_roles_count = 0

        # 1. Supprimer la carte associée directement au site, si elle existe
        from ..models.carte import Carte
        site_carte = Carte.query.filter_by(site_id=site_id).first()
        if site_carte:
            db.session.delete(site_carte)
            cartes_count += 1

        # 2. Récupérer tous les bâtiments associés à ce site
        from ..models.batiment import Batiment
        batiments = Batiment.query.filter_by(site_id=site_id).all()
        batiments_count = len(batiments)

        # 3. Pour chaque bâtiment, supprimer ses étages et tout ce qui leur est associé
        from ..models.etage import Etage
        from ..models.baes import Baes
        from ..models.status import Status

        for batiment in batiments:
            # Récupérer tous les étages de ce bâtiment
            etages = Etage.query.filter_by(batiment_id=batiment.id).all()
            etages_count += len(etages)

            for etage in etages:
                # Supprimer la carte associée à cet étage, si elle existe
                etage_carte = Carte.query.filter_by(etage_id=etage.id).first()
                if etage_carte:
                    db.session.delete(etage_carte)
                    cartes_count += 1

                # Récupérer tous les BAES associés à cet étage
                baes_list = Baes.query.filter_by(etage_id=etage.id).all()
                baes_count += len(baes_list)

                for baes in baes_list:
                    # Supprimer toutes les erreurs associées à ce BAES
                    statuses = Status.query.filter_by(baes_id=baes.id).all()
                    statuses_count += len(statuses)
                    for status in statuses:
                        db.session.delete(status)

                    # Supprimer le BAES
                    db.session.delete(baes)

                # Supprimer l'étage
                db.session.delete(etage)

            # Supprimer le bâtiment
            db.session.delete(batiment)

        # 4. Mettre à jour les liaisons user-site-role pour conserver les relations user-role
        from ..models.user_site_role import UserSiteRole
        user_site_roles = UserSiteRole.query.filter_by(site_id=site_id).all()
        user_site_roles_count = len(user_site_roles)

        # Mettre à jour site_id à NULL pour conserver les relations user-role
        for user_site_role in user_site_roles:
            user_site_role.site_id = None

        # 5. Supprimer le site
        db.session.delete(site)
        db.session.commit()

        return jsonify({
            'message': 'Site supprimé avec succès',
            'batiments_deleted': batiments_count,
            'etages_deleted': etages_count,
            'baes_deleted': baes_count,
            'statuses_deleted': statuses_count,
            'cartes_deleted': cartes_count,
            'user_site_roles_preserved': user_site_roles_count
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in delete_site: {e}")
        return jsonify({'error': str(e)}), 500
