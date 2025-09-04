# routes/user_site_role.py
from flask import Blueprint, jsonify, request
from flasgger import swag_from
from sqlalchemy.exc import IntegrityError
from ..models import db, UserSiteRole, User, Site, Role

# Créer le blueprint pour les routes user-site-role
user_site_role_bp = Blueprint('user_site_role', __name__, url_prefix='/user-site-roles')


@user_site_role_bp.route('', methods=['GET'])
@swag_from({
    'tags': ['UserSiteRole'],
    'summary': 'Récupère toutes les relations user-site-role',
    'description': 'Récupère toutes les relations avec possibilité de filtrer par user_id, site_id ou role_id',
    'parameters': [
        {
            'name': 'user_id',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'Filtrer par ID utilisateur'
        },
        {
            'name': 'site_id',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'Filtrer par ID site'
        },
        {
            'name': 'role_id',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'Filtrer par ID rôle'
        }
    ],
    'responses': {
        200: {
            'description': 'Liste des relations user-site-role',
            'schema': {
                'type': 'array',
                'items': {
                    '$ref': '#/definitions/UserSiteRole'
                }
            }
        },
        500: {
            'description': 'Erreur serveur'
        }
    }
})
def get_user_site_roles():
    """Récupère toutes les relations user-site-role avec possibilité de filtrer"""
    try:
        # Récupérer les paramètres de filtre
        user_id = request.args.get('user_id', type=int)
        site_id = request.args.get('site_id', type=int)
        role_id = request.args.get('role_id', type=int)

        # Construire la requête
        query = UserSiteRole.query

        if user_id:
            query = query.filter_by(user_id=user_id)
        if site_id:
            query = query.filter_by(site_id=site_id)
        if role_id:
            query = query.filter_by(role_id=role_id)

        # Exécuter la requête
        user_site_roles = query.all()

        # Formater la réponse
        result = []
        for usr in user_site_roles:
            result.append({
                'id': usr.id,
                'user_id': usr.user_id,
                'site_id': usr.site_id,
                'role_id': usr.role_id,
                'user_login': usr.user.login if usr.user else None,
                'site_name': usr.site.name if usr.site else None,
                'role_name': usr.role.name if usr.role else None,
                'created_at': usr.created_at.isoformat() if usr.created_at else None,
                'updated_at': usr.updated_at.isoformat() if usr.updated_at else None
            })

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_site_role_bp.route('/<int:id>', methods=['GET'])
@swag_from({
    'tags': ['UserSiteRole'],
    'summary': 'Récupère une relation spécifique',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID de la relation'
        }
    ],
    'responses': {
        200: {
            'description': 'Relation trouvée',
            'schema': {
                '$ref': '#/definitions/UserSiteRole'
            }
        },
        404: {
            'description': 'Relation non trouvée'
        }
    }
})
def get_user_site_role(id):
    """Récupère une relation user-site-role spécifique"""
    try:
        usr = UserSiteRole.query.get(id)

        if not usr:
            return jsonify({'error': 'Relation non trouvée'}), 404

        result = {
            'id': usr.id,
            'user_id': usr.user_id,
            'site_id': usr.site_id,
            'role_id': usr.role_id,
            'user_login': usr.user.login if usr.user else None,
            'site_name': usr.site.name if usr.site else None,
            'role_name': usr.role.name if usr.role else None,
            'created_at': usr.created_at.isoformat() if usr.created_at else None,
            'updated_at': usr.updated_at.isoformat() if usr.updated_at else None
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_site_role_bp.route('', methods=['POST'])
@swag_from({
    'tags': ['UserSiteRole'],
    'summary': 'Crée une nouvelle relation user-site-role',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['user_id', 'role_id'],
                'properties': {
                    'user_id': {
                        'type': 'integer',
                        'description': 'ID de l\'utilisateur'
                    },
                    'site_id': {
                        'type': 'integer',
                        'nullable': True,
                        'description': 'ID du site (null pour rôle global)'
                    },
                    'role_id': {
                        'type': 'integer',
                        'description': 'ID du rôle'
                    }
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Relation créée avec succès',
            'schema': {
                '$ref': '#/definitions/UserSiteRole'
            }
        },
        400: {
            'description': 'Données invalides'
        },
        404: {
            'description': 'Ressource non trouvée'
        },
        409: {
            'description': 'La relation existe déjà'
        }
    }
})
def create_user_site_role():
    """Crée une nouvelle relation user-site-role"""
    try:
        data = request.get_json()

        # Validation des données requises
        if not data or 'user_id' not in data or 'role_id' not in data:
            return jsonify({'error': 'user_id et role_id sont requis'}), 400

        # Vérifier que l'utilisateur existe
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404

        # Vérifier que le rôle existe
        role = Role.query.get(data['role_id'])
        if not role:
            return jsonify({'error': 'Rôle non trouvé'}), 404

        # Vérifier que le site existe si site_id est fourni
        if 'site_id' in data and data['site_id'] is not None:
            site = Site.query.get(data['site_id'])
            if not site:
                return jsonify({'error': 'Site non trouvé'}), 404

        # Vérifier qu'une relation similaire n'existe pas déjà
        existing = UserSiteRole.query.filter_by(
            user_id=data['user_id'],
            site_id=data.get('site_id'),
            role_id=data['role_id']
        ).first()

        if existing:
            return jsonify({'error': 'Cette relation existe déjà'}), 409

        # Créer la nouvelle relation
        new_usr = UserSiteRole(
            user_id=data['user_id'],
            site_id=data.get('site_id'),
            role_id=data['role_id']
        )

        db.session.add(new_usr)
        db.session.commit()

        # Retourner la relation créée
        result = {
            'id': new_usr.id,
            'user_id': new_usr.user_id,
            'site_id': new_usr.site_id,
            'role_id': new_usr.role_id,
            'user_login': new_usr.user.login,
            'site_name': new_usr.site.name if new_usr.site else None,
            'role_name': new_usr.role.name,
            'created_at': new_usr.created_at.isoformat() if new_usr.created_at else None,
            'updated_at': new_usr.updated_at.isoformat() if new_usr.updated_at else None
        }

        return jsonify(result), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Erreur d\'intégrité des données'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@user_site_role_bp.route('/<int:id>', methods=['PUT', 'PATCH'])
@swag_from({
    'tags': ['UserSiteRole'],
    'summary': 'Modifie une relation existante',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID de la relation à modifier'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'user_id': {
                        'type': 'integer',
                        'description': 'ID de l\'utilisateur'
                    },
                    'site_id': {
                        'type': 'integer',
                        'nullable': True,
                        'description': 'ID du site'
                    },
                    'role_id': {
                        'type': 'integer',
                        'description': 'ID du rôle'
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Relation modifiée avec succès',
            'schema': {
                '$ref': '#/definitions/UserSiteRole'
            }
        },
        400: {
            'description': 'Données invalides'
        },
        404: {
            'description': 'Relation non trouvée'
        },
        409: {
            'description': 'La relation existe déjà'
        }
    }
})
def update_user_site_role(id):
    """Modifie une relation user-site-role existante"""
    try:
        usr = UserSiteRole.query.get(id)

        if not usr:
            return jsonify({'error': 'Relation non trouvée'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Aucune donnée fournie'}), 400

        # Mise à jour des champs si fournis
        if 'user_id' in data:
            user = User.query.get(data['user_id'])
            if not user:
                return jsonify({'error': 'Utilisateur non trouvé'}), 404
            usr.user_id = data['user_id']

        if 'site_id' in data:
            if data['site_id'] is not None:
                site = Site.query.get(data['site_id'])
                if not site:
                    return jsonify({'error': 'Site non trouvé'}), 404
            usr.site_id = data['site_id']

        if 'role_id' in data:
            role = Role.query.get(data['role_id'])
            if not role:
                return jsonify({'error': 'Rôle non trouvé'}), 404
            usr.role_id = data['role_id']

        # Vérifier qu'une relation similaire n'existe pas déjà
        existing = UserSiteRole.query.filter(
            UserSiteRole.id != id,
            UserSiteRole.user_id == usr.user_id,
            UserSiteRole.site_id == usr.site_id,
            UserSiteRole.role_id == usr.role_id
        ).first()

        if existing:
            return jsonify({'error': 'Cette relation existe déjà'}), 409

        db.session.commit()

        # Retourner la relation mise à jour
        result = {
            'id': usr.id,
            'user_id': usr.user_id,
            'site_id': usr.site_id,
            'role_id': usr.role_id,
            'user_login': usr.user.login,
            'site_name': usr.site.name if usr.site else None,
            'role_name': usr.role.name,
            'created_at': usr.created_at.isoformat() if usr.created_at else None,
            'updated_at': usr.updated_at.isoformat() if usr.updated_at else None
        }

        return jsonify(result), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Erreur d\'intégrité des données'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@user_site_role_bp.route('/<int:id>', methods=['DELETE'])
@swag_from({
    'tags': ['UserSiteRole'],
    'summary': 'Supprime une relation',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID de la relation à supprimer'
        }
    ],
    'responses': {
        200: {
            'description': 'Relation supprimée avec succès',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'remaining_permissions': {'type': 'integer'}
                }
            }
        },
        404: {
            'description': 'Relation non trouvée'
        }
    }
})
def delete_user_site_role(id):
    """Supprime une relation user-site-role"""
    try:
        usr = UserSiteRole.query.get(id)

        if not usr:
            return jsonify({'error': 'Relation non trouvée'}), 404

        # Sauvegarder les infos pour le message de retour
        user_id = usr.user_id
        site_name = usr.site.name if usr.site else 'Tous les sites'
        role_name = usr.role.name

        db.session.delete(usr)
        db.session.commit()

        # Vérifier si l'utilisateur a encore des permissions
        remaining_permissions = UserSiteRole.query.filter_by(user_id=user_id).count()

        return jsonify({
            'message': f'Relation supprimée avec succès (User ID: {user_id}, Site: {site_name}, Role: {role_name})',
            'remaining_permissions': remaining_permissions
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@user_site_role_bp.route('/user/<int:user_id>/permissions', methods=['GET'])
@swag_from({
    'tags': ['UserSiteRole'],
    'summary': 'Récupère toutes les permissions d\'un utilisateur',
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID de l\'utilisateur'
        }
    ],
    'responses': {
        200: {
            'description': 'Permissions de l\'utilisateur',
            'schema': {
                'type': 'object',
                'properties': {
                    'user_id': {'type': 'integer'},
                    'user_login': {'type': 'string'},
                    'permissions': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer'},
                                'site_id': {'type': 'integer', 'nullable': True},
                                'site_name': {'type': 'string'},
                                'role_id': {'type': 'integer'},
                                'role_name': {'type': 'string'},
                                'created_at': {'type': 'string', 'format': 'date-time'}
                            }
                        }
                    }
                }
            }
        },
        404: {
            'description': 'Utilisateur non trouvé'
        }
    }
})
def get_user_permissions(user_id):
    """Récupère tous les sites et rôles associés à un utilisateur"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404

        permissions = UserSiteRole.query.filter_by(user_id=user_id).all()

        result = {
            'user_id': user_id,
            'user_login': user.login,
            'permissions': []
        }

        for perm in permissions:
            result['permissions'].append({
                'id': perm.id,
                'site_id': perm.site_id,
                'site_name': perm.site.name if perm.site else 'Tous les sites',
                'role_id': perm.role_id,
                'role_name': perm.role.name,
                'created_at': perm.created_at.isoformat() if perm.created_at else None
            })

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_site_role_bp.route('/site/<int:site_id>/users', methods=['GET'])
@swag_from({
    'tags': ['UserSiteRole'],
    'summary': 'Récupère tous les utilisateurs d\'un site',
    'parameters': [
        {
            'name': 'site_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID du site'
        }
    ],
    'responses': {
        200: {
            'description': 'Utilisateurs du site',
            'schema': {
                'type': 'object',
                'properties': {
                    'site_id': {'type': 'integer'},
                    'site_name': {'type': 'string'},
                    'users': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer'},
                                'user_id': {'type': 'integer'},
                                'user_login': {'type': 'string'},
                                'role_id': {'type': 'integer'},
                                'role_name': {'type': 'string'},
                                'created_at': {'type': 'string', 'format': 'date-time'}
                            }
                        }
                    }
                }
            }
        },
        404: {
            'description': 'Site non trouvé'
        }
    }
})
def get_site_users(site_id):
    """Récupère tous les utilisateurs ayant accès à un site"""
    try:
        site = Site.query.get(site_id)
        if not site:
            return jsonify({'error': 'Site non trouvé'}), 404

        users_roles = UserSiteRole.query.filter_by(site_id=site_id).all()

        result = {
            'site_id': site_id,
            'site_name': site.name,
            'users': []
        }

        for ur in users_roles:
            result['users'].append({
                'id': ur.id,
                'user_id': ur.user_id,
                'user_login': ur.user.login,
                'role_id': ur.role_id,
                'role_name': ur.role.name,
                'created_at': ur.created_at.isoformat() if ur.created_at else None
            })

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_site_role_bp.route('/user/<int:user_id>/site/<int:site_id>', methods=['DELETE'])
@swag_from({
    'tags': ['UserSiteRole'],
    'summary': 'Supprime toutes les permissions d\'un utilisateur sur un site',
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID de l\'utilisateur'
        },
        {
            'name': 'site_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID du site'
        }
    ],
    'responses': {
        200: {
            'description': 'Permissions supprimées',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'remaining_permissions': {'type': 'integer'}
                }
            }
        },
        404: {
            'description': 'Ressource non trouvée'
        }
    }
})
def delete_user_site_permissions(user_id, site_id):
    """Supprime toutes les permissions d'un utilisateur pour un site donné"""
    try:
        # Vérifier que l'utilisateur et le site existent
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404

        site = Site.query.get(site_id)
        if not site:
            return jsonify({'error': 'Site non trouvé'}), 404

        # Supprimer toutes les relations pour cet utilisateur sur ce site
        permissions = UserSiteRole.query.filter_by(user_id=user_id, site_id=site_id).all()

        if not permissions:
            return jsonify({'error': 'Aucune permission trouvée pour cet utilisateur sur ce site'}), 404

        count = len(permissions)
        for perm in permissions:
            db.session.delete(perm)

        db.session.commit()

        # Vérifier les permissions restantes
        remaining = UserSiteRole.query.filter_by(user_id=user_id).count()

        return jsonify({
            'message': f'{count} permission(s) supprimée(s) pour l\'utilisateur {user.login} sur le site {site.name}',
            'remaining_permissions': remaining
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@user_site_role_bp.route('/user/<int:user_id>/global-role', methods=['POST'])
@swag_from({
    'tags': ['UserSiteRole'],
    'summary': 'Attribue un rôle global à un utilisateur',
    'description': 'Attribue un rôle global (site=null) à un utilisateur. Utile quand un utilisateur n\'a plus de site spécifique',
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID de l\'utilisateur'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['role_id'],
                'properties': {
                    'role_id': {
                        'type': 'integer',
                        'description': 'ID du rôle global à attribuer'
                    }
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Rôle global attribué',
            'schema': {
                '$ref': '#/definitions/UserSiteRole'
            }
        },
        400: {
            'description': 'Données invalides'
        },
        404: {
            'description': 'Ressource non trouvée'
        },
        409: {
            'description': 'Ce rôle global est déjà attribué'
        }
    }
})
def assign_global_role(user_id):
    """Attribue un rôle global (site=null) à un utilisateur"""
    try:
        data = request.get_json()
        if not data or 'role_id' not in data:
            return jsonify({'error': 'role_id est requis'}), 400

        # Vérifier que l'utilisateur existe
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404

        # Vérifier que le rôle existe
        role = Role.query.get(data['role_id'])
        if not role:
            return jsonify({'error': 'Rôle non trouvé'}), 404

        # Vérifier qu'un rôle global n'existe pas déjà
        existing = UserSiteRole.query.filter_by(
            user_id=user_id,
            site_id=None,
            role_id=data['role_id']
        ).first()

        if existing:
            return jsonify({'error': 'Ce rôle global est déjà attribué à cet utilisateur'}), 409

        # Créer la relation avec site_id=null
        global_role = UserSiteRole(
            user_id=user_id,
            site_id=None,
            role_id=data['role_id']
        )

        db.session.add(global_role)
        db.session.commit()

        return jsonify({
            'id': global_role.id,
            'user_id': user_id,
            'user_login': user.login,
            'site_id': None,
            'site_name': 'Tous les sites',
            'role_id': global_role.role_id,
            'role_name': role.name,
            'created_at': global_role.created_at.isoformat() if global_role.created_at else None,
            'updated_at': global_role.updated_at.isoformat() if global_role.updated_at else None,
            'message': 'Rôle global attribué avec succès'
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500