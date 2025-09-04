# routes/user_site_routes.py
from flask import Blueprint, request, jsonify, current_app
from flasgger import swag_from
from ..models import db
from ..models.user import User
from ..models.site import Site

user_site_bp = Blueprint('user_site_bp', __name__)


@user_site_bp.route('/<int:user_id>/sites', methods=['GET'])
@swag_from({
    'tags': ['User-Site Relations'],
    'description': "Récupère la liste des sites associés à un utilisateur donné.",
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
            'description': "Liste des sites pour l'utilisateur.",
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
        404: {'description': "Utilisateur non trouvé."},
        500: {'description': "Erreur interne."}
    }
})
def get_user_sites(user_id):
    try:
        from ..models.user_site_role import UserSiteRole

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': "Utilisateur non trouvé"}), 404

        # Récupérer les sites via les associations UserSiteRole
        site_ids_set = set()
        sites = []

        for usr in user.user_site_roles:
            if usr.site and usr.site.id not in site_ids_set:
                site_ids_set.add(usr.site.id)
                sites.append(usr.site)

        result = [{
            'id': site.id,
            'name': site.name
        } for site in sites]
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_user_sites: {e}")
        return jsonify({'error': str(e)}), 500


@user_site_bp.route('/<int:user_id>/sites', methods=['POST'])
@swag_from({
    'tags': ['User-Site Relations'],
    'description': "Associe un site à un utilisateur ou met à jour une association existante. Attendez un JSON contenant 'site_id'.",
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID de l'utilisateur"
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'site_id': {'type': 'integer', 'example': 1}
                },
                'required': ['site_id']
            }
        }
    ],
    'responses': {
        200: {
            'description': "Site associé avec succès à l'utilisateur ou association mise à jour.",
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': "Site ajouté à l'utilisateur ou association mise à jour."}
                }
            }
        },
        404: {'description': "Utilisateur ou site non trouvé."},
        500: {'description': "Erreur interne."}
    }
})
def add_site_to_user(user_id):
    try:
        from ..models.user_site_role import UserSiteRole
        from ..models.role import Role

        data = request.get_json()
        if not data or 'site_id' not in data:
            return jsonify({'error': "Le champ 'site_id' est requis"}), 400
        site_id = data['site_id']
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': "Utilisateur non trouvé"}), 404
        site = Site.query.get(site_id)
        if not site:
            return jsonify({'error': "Site non trouvé"}), 404

        # Trouver un rôle par défaut
        default_role = Role.query.filter_by(name='user').first()
        if not default_role:
            # Si le rôle 'user' n'existe pas, utiliser le premier rôle disponible
            default_role = Role.query.first()
            if not default_role:
                return jsonify({'error': "Aucun rôle disponible pour l'association"}), 500

        # Vérifier si l'association exacte existe déjà
        existing = UserSiteRole.query.filter_by(user_id=user_id, site_id=site_id, role_id=default_role.id).first()
        if existing:
            return jsonify({'message': "Site déjà associé à l'utilisateur avec ce rôle."}), 200

        # Vérifier si une autre association existe pour cet utilisateur et ce rôle (mais avec un site différent)
        other_association = UserSiteRole.query.filter_by(user_id=user_id, role_id=default_role.id).first()

        # Si une autre association existe, on la met à jour
        if other_association:
            old_site_id = other_association.site_id
            other_association.site_id = site_id
            db.session.commit()
            return jsonify({'message': f"Site mis à jour pour l'utilisateur. Ancien site: {old_site_id}, Nouveau site: {site_id}"}), 200

        # Sinon, on crée une nouvelle association
        association = UserSiteRole(user_id=user_id, site_id=site_id, role_id=default_role.id)
        db.session.add(association)
        db.session.commit()
        return jsonify({'message': "Site ajouté à l'utilisateur."}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in add_site_to_user: {e}")
        return jsonify({'error': str(e)}), 500


@user_site_bp.route('/<int:user_id>/sites/<int:site_id>', methods=['DELETE'])
@swag_from({
    'tags': ['User-Site Relations'],
    'description': "Dissocie un site d'un utilisateur.",
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID de l'utilisateur"
        },
        {
            'name': 'site_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID du site à dissocier"
        }
    ],
    'responses': {
        200: {
            'description': "Site dissocié avec succès.",
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': "Site dissocié de l'utilisateur."}
                }
            }
        },
        404: {'description': "Utilisateur ou site non trouvé, ou site non associé."},
        500: {'description': "Erreur interne."}
    }
})
def remove_site_from_user(user_id, site_id):
    try:
        from ..models.user_site_role import UserSiteRole

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': "Utilisateur non trouvé"}), 404
        site = Site.query.get(site_id)
        if not site:
            return jsonify({'error': "Site non trouvé"}), 404

        # Vérifier si l'utilisateur est associé à ce site
        associations = UserSiteRole.query.filter_by(user_id=user_id, site_id=site_id).all()
        if not associations:
            return jsonify({'error': "Site non associé à l'utilisateur"}), 404

        # Supprimer toutes les associations entre l'utilisateur et ce site
        for association in associations:
            db.session.delete(association)

        db.session.commit()
        return jsonify({'message': "Site dissocié de l'utilisateur."}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in remove_site_from_user: {e}")
        return jsonify({'error': str(e)}), 500
