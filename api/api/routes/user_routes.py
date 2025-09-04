from flask import Blueprint, request, jsonify, current_app
from flasgger import swag_from
from ..models.user import User
from ..models import db
from sqlalchemy import text

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['User CRUD'],
    'description': 'Récupère la liste de tous les utilisateurs avec leurs sites et rôles associés.',
    'responses': {
        '200': {
            'description': 'Liste des utilisateurs avec leurs sites et rôles.',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'example': 1},
                        'login': {'type': 'string', 'example': 'user1'},
                        'roles': {
                            'type': 'array',
                            'items': {'type': 'string'},
                            'example': ['admin', 'user']
                        },
                        'sites': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'integer', 'example': 3},
                                    'name': {'type': 'string', 'example': 'Site test 1'}
                                }
                            },
                            'example': [
                                {'id': 3, 'name': 'Site test 1'},
                                {'id': 4, 'name': 'Site test 2'}
                            ]
                        }
                    }
                }
            }
        },
        '500': {'description': 'Erreur interne.'}
    }
})
def get_users():
    try:
        users = User.query.all()
        result = []
        for user in users:
            # Récupérer les rôles distincts via l'association
            roles_set = {assoc.role.name for assoc in user.user_site_roles if assoc.role}
            # Récupérer les sites distincts via l'association
            sites = []
            sites_ids = set()
            for assoc in user.user_site_roles:
                if assoc.site and assoc.site.id not in sites_ids:
                    sites.append({'id': assoc.site.id, 'name': assoc.site.name})
                    sites_ids.add(assoc.site.id)
            result.append({
                'id': user.id,
                'login': user.login,
                'roles': list(roles_set),
                'sites': sites
            })
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_users: {e}")
        return jsonify({'error': str(e)}), 500


@user_bp.route('/<int:user_id>', methods=['GET'])
@swag_from({
    'tags': ['User CRUD'],
    'description': "Récupère un utilisateur par son ID avec ses sites et rôles associés.",
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID de l'utilisateur à récupérer"
        }
    ],
    'responses': {
        '200': {
            'description': "Détails de l'utilisateur.",
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'login': {'type': 'string', 'example': 'user1'},
                    'roles': {'type': 'array', 'items': {'type': 'string'}},
                    'sites': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer', 'example': 3},
                                'name': {'type': 'string', 'example': 'Site test 1'}
                            }
                        }
                    }
                }
            }
        },
        '404': {'description': "Utilisateur non trouvé."},
        '500': {'description': "Erreur interne."}
    }
})
def get_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        roles_set = {assoc.role.name for assoc in user.user_site_roles if assoc.role}
        sites = []
        sites_ids = set()
        for assoc in user.user_site_roles:
            if assoc.site and assoc.site.id not in sites_ids:
                sites.append({'id': assoc.site.id, 'name': assoc.site.name})
                sites_ids.add(assoc.site.id)
        result = {
            'id': user.id,
            'login': user.login,
            'roles': list(roles_set),
            'sites': sites
        }
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_user: {e}")
        return jsonify({'error': str(e)}), 500


@user_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['User CRUD'],
    'consumes': ['application/json'],
    'description': "Crée un nouvel utilisateur et associe éventuellement des rôles et sites via l'association.",
    'parameters': [
        {
            'in': 'body',
            'name': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['login', 'password'],
                'properties': {
                    'login': {
                        'type': 'string',
                        'example': 'nouveluser'
                    },
                    'password': {
                        'type': 'string',
                        'example': 'motdepasse'
                    },
                    'roles': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'example': ['admin', 'user']
                    },
                    'sites': {
                        'type': 'array',
                        'items': {'type': 'integer'},
                        'example': [3, 4]
                    }
                }
            }
        }
    ],
    'responses': {
        '201': {
            'description': "Utilisateur créé avec succès.",
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'login': {'type': 'string', 'example': 'nouveluser'},
                    'roles': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'example': ['admin', 'user']
                    },
                    'sites': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer', 'example': 3},
                                'name': {'type': 'string', 'example': 'Site test 1'}
                            }
                        }
                    }
                }
            }
        },
        '400': {'description': "Mauvaise requête."}
    }
})
def create_user():
    data = request.get_json()
    if not data or 'login' not in data or 'password' not in data:
        return jsonify({'error': 'Les champs "login" et "password" sont requis'}), 400

    login = data['login']
    password = data['password']

    if User.query.filter_by(login=login).first():
        return jsonify({'error': 'Cet utilisateur existe déjà'}), 400

    user = User(login=login)
    user.set_password(password)

    # Ajouter l'utilisateur à la base de données pour obtenir son ID
    db.session.add(user)
    db.session.flush()  # Obtenir l'ID sans commit

    # Association facultative des rôles
    if 'roles' in data:
        from ..models.role import Role
        from ..models.user_site_role import UserSiteRole

        role_names = data['roles']
        roles = Role.query.filter(Role.name.in_(role_names)).all()

        # Créer des associations UserSiteRole pour chaque rôle (global, sans site)
        for role in roles:
            association = UserSiteRole(user_id=user.id, site_id=-1, role_id=role.id)
            db.session.add(association)

    # Association facultative des sites
    if 'sites' in data:
        from ..models.site import Site
        from ..models.user_site_role import UserSiteRole

        site_ids = data['sites']
        sites = Site.query.filter(Site.id.in_(site_ids)).all()

        # Si vous voulez associer un rôle par défaut pour chaque site
        default_role = Role.query.filter_by(name='user').first()
        if default_role:
            for site in sites:
                association = UserSiteRole(user_id=user.id, site_id=site.id, role_id=default_role.id)
                db.session.add(association)

    db.session.commit()

    # Récupérer les rôles et sites pour la réponse
    user_roles = []
    user_sites = []

    # Récupérer les rôles via les associations
    for usr in user.user_site_roles:
        if usr.role:
            user_roles.append(usr.role.name)

    # Récupérer les sites via les associations
    site_ids_set = set()
    for usr in user.user_site_roles:
        if usr.site and usr.site.id not in site_ids_set:
            site_ids_set.add(usr.site.id)
            user_sites.append({'id': usr.site.id, 'name': usr.site.name})

    result = {
        'id': user.id,
        'login': user.login,
        'roles': user_roles,
        'sites': user_sites
    }
    return jsonify(result), 201


@user_bp.route('/<int:user_id>', methods=['PUT'])
@swag_from({
    'tags': ['User CRUD'],
    'description': "Met à jour un utilisateur existant par son ID.",
    'consumes': ["application/json"],
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID de l'utilisateur à mettre à jour"
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'login': {'type': 'string', 'example': 'updateduser'},
                    'password': {'type': 'string', 'example': 'updatedpassword'},
                    'roles': {
                        'type': 'array',
                        'items': {'type': 'string', 'example': 'admin'},
                        'description': 'Liste des noms de rôles à associer (optionnel)'
                    }
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': "Utilisateur mis à jour avec succès.",
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'login': {'type': 'string', 'example': 'updateduser'},
                    'roles': {'type': 'array', 'items': {'type': 'string'}}
                }
            }
        },
        '404': {'description': "Utilisateur non trouvé."},
        '500': {'description': "Erreur interne."}
    }
})
def update_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        data = request.get_json()
        if 'login' in data:
            user.login = data['login']
        if 'password' in data:
            user.set_password(data['password'])
        if 'roles' in data:
            from ..models.role import Role
            from ..models.user_site_role import UserSiteRole

            # Supprimer les associations de rôles globaux existantes
            UserSiteRole.query.filter_by(user_id=user.id, site_id=-1).delete()

            # Ajouter les nouveaux rôles
            role_names = data['roles']
            roles = Role.query.filter(Role.name.in_(role_names)).all()

            for role in roles:
                association = UserSiteRole(user_id=user.id, site_id=-1, role_id=role.id)
                db.session.add(association)

        db.session.commit()

        # Récupérer les rôles pour la réponse
        user_roles = []
        for usr in user.user_site_roles:
            if usr.role:
                user_roles.append(usr.role.name)

        result = {
            'id': user.id,
            'login': user.login,
            'roles': user_roles
        }
        return jsonify(result), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in update_user: {e}")
        return jsonify({'error': str(e)}), 500


@user_bp.route('/<int:user_id>', methods=['DELETE'])
@swag_from({
    'tags': ['User CRUD'],
    'description': "Supprime un utilisateur par son ID.",
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID de l'utilisateur à supprimer"
        }
    ],
    'responses': {
        '200': {
            'description': "Utilisateur supprimé avec succès.",
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Utilisateur supprimé avec succès'}
                }
            }
        },
        '404': {'description': "Utilisateur non trouvé."},
        '500': {'description': "Erreur interne."}
    }
})
def delete_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404

        # Supprimer d'abord les associations UserSiteRole
        from ..models.user_site_role import UserSiteRole

        # Récupérer toutes les associations de l'utilisateur
        user_site_roles = UserSiteRole.query.filter_by(user_id=user_id).all()
        current_app.logger.info(f"Suppression de {len(user_site_roles)} relations pour l'utilisateur {user_id}")

        # Supprimer chaque association individuellement
        for usr in user_site_roles:
            current_app.logger.info(f"Suppression de la relation: user_id={usr.user_id}, site_id={usr.site_id}, role_id={usr.role_id}")
            db.session.delete(usr)

        # Ensuite supprimer l'utilisateur
        current_app.logger.info(f"Suppression de l'utilisateur {user_id}")
        db.session.delete(user)

        # Commit des changements
        db.session.commit()
        current_app.logger.info(f"Utilisateur {user_id} et ses relations supprimés avec succès")

        return jsonify({'message': 'Utilisateur supprimé avec succès'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in delete_user: {e}")
        return jsonify({'error': str(e)}), 500


@user_bp.route('/create-with-relations', methods=['POST'])
@swag_from({
    'tags': ['User CRUD'],
    'consumes': ['application/json'],
    'description': "Crée un nouvel utilisateur avec toutes ses relations site-rôle en une seule requête.",
    'parameters': [
        {
            'in': 'body',
            'name': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['login', 'password', 'rolesBySite'],
                'properties': {
                    'login': {
                        'type': 'string',
                        'example': 'nouveluser'
                    },
                    'password': {
                        'type': 'string',
                        'example': 'motdepasse'
                    },
                    'rolesBySite': {
                        'type': 'object',
                        'example': {
                            "1": 2,
                            "3": 1
                        },
                        'description': 'Objet où les clés sont les IDs des sites et les valeurs sont les IDs des rôles'
                    }
                }
            }
        }
    ],
    'responses': {
        '201': {
            'description': "Utilisateur créé avec succès avec toutes ses relations.",
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'login': {'type': 'string', 'example': 'nouveluser'},
                    'relations': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'site_id': {'type': 'integer', 'example': 1},
                                'site_name': {'type': 'string', 'example': 'Site A'},
                                'role_id': {'type': 'integer', 'example': 2},
                                'role_name': {'type': 'string', 'example': 'editor'}
                            }
                        }
                    }
                }
            }
        },
        '400': {'description': "Mauvaise requête ou utilisateur existant."},
        '404': {'description': "Site ou rôle non trouvé."},
        '500': {'description': "Erreur interne."}
    }
})
def create_user_with_relations():
    try:
        data = request.get_json()
        if not data or 'login' not in data or 'password' not in data or 'rolesBySite' not in data:
            return jsonify({'error': 'Les champs "login", "password" et "rolesBySite" sont requis'}), 400

        login = data['login']
        password = data['password']
        roles_by_site = data['rolesBySite']

        # Vérifier si l'utilisateur existe déjà
        if User.query.filter_by(login=login).first():
            return jsonify({'error': 'Cet utilisateur existe déjà'}), 400

        # Importer les modèles nécessaires
        from ..models.site import Site
        from ..models.role import Role
        from ..models.user_site_role import UserSiteRole

        # 1. Créer l'utilisateur
        user = User(login=login)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # Obtenir l'ID sans commit

        # 2. Créer les relations user-site-role
        relations = []

        for site_id_str, role_id in roles_by_site.items():
            try:
                site_id = int(site_id_str)
            except ValueError:
                continue  # Ignorer les clés non numériques

            # Vérifier l'existence du site et du rôle
            site = Site.query.get(site_id)
            role = Role.query.get(role_id)

            if not site:
                db.session.rollback()
                return jsonify({'error': f'Site avec ID {site_id} non trouvé'}), 404

            if not role:
                db.session.rollback()
                return jsonify({'error': f'Rôle avec ID {role_id} non trouvé'}), 404

            # Vérifier si une relation user-role identique existe déjà sans site attribué
            existing_global_relation = UserSiteRole.query.filter_by(
                user_id=user.id, 
                role_id=role_id, 
                site_id=-1
            ).first()

            if existing_global_relation:
                # Modifier cette relation pour ajouter le site
                existing_global_relation.site_id = site_id
                relations.append({
                    'site_id': site_id,
                    'site_name': site.name,
                    'role_id': role_id,
                    'role_name': role.name,
                    'status': 'updated_global'
                })
            else:
                # Vérifier si une relation user-role existe avec un site différent
                existing_site_relation = UserSiteRole.query.filter(
                    UserSiteRole.user_id == user.id,
                    UserSiteRole.role_id == role_id,
                    UserSiteRole.site_id != site_id,
                    UserSiteRole.site_id != -1
                ).first()

                # Créer une nouvelle relation dans tous les cas
                new_relation = UserSiteRole(user_id=user.id, site_id=site_id, role_id=role_id)
                db.session.add(new_relation)

                status = 'created_new' if existing_site_relation else 'created'
                relations.append({
                    'site_id': site_id,
                    'site_name': site.name,
                    'role_id': role_id,
                    'role_name': role.name,
                    'status': status
                })

        # Valider la transaction
        db.session.commit()

        # Préparer la réponse
        result = {
            'id': user.id,
            'login': user.login,
            'relations': relations
        }

        return jsonify(result), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in create_user_with_relations: {e}")
        return jsonify({'error': str(e)}), 500


@user_bp.route('/<int:user_id>/update-with-relations', methods=['PUT'])
@swag_from({
    'tags': ['User CRUD'],
    'consumes': ['application/json'],
    'description': "Met à jour un utilisateur existant avec ses relations site-rôle en une seule requête.",
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "ID de l'utilisateur à mettre à jour"
        },
        {
            'in': 'body',
            'name': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'login': {
                        'type': 'string',
                        'example': 'utilisateurmodifie'
                    },
                    'password': {
                        'type': 'string',
                        'example': 'nouveaumotdepasse'
                    },
                    'rolesBySite': {
                        'type': 'object',
                        'example': {
                            "1": 2,
                            "3": 1
                        },
                        'description': 'Objet où les clés sont les IDs des sites et les valeurs sont les IDs des rôles'
                    },
                    'replaceExistingRelations': {
                        'type': 'boolean',
                        'example': False,
                        'description': 'Si true, remplace toutes les relations existantes. Si false, ajoute ou met à jour les relations fournies.'
                    }
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': "Utilisateur mis à jour avec succès avec ses relations.",
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'login': {'type': 'string', 'example': 'utilisateurmodifie'},
                    'relations': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'site_id': {'type': 'integer', 'example': 1},
                                'site_name': {'type': 'string', 'example': 'Site A'},
                                'role_id': {'type': 'integer', 'example': 2},
                                'role_name': {'type': 'string', 'example': 'editor'},
                                'status': {'type': 'string', 'example': 'created'}
                            }
                        }
                    }
                }
            }
        },
        '400': {'description': "Mauvaise requête."},
        '404': {'description': "Utilisateur, site ou rôle non trouvé."},
        '500': {'description': "Erreur interne."}
    }
})
def update_user_with_relations(user_id):
    try:
        # Vérifier si l'utilisateur existe
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Données JSON requises'}), 400

        # Importer les modèles nécessaires
        from ..models.site import Site
        from ..models.role import Role
        from ..models.user_site_role import UserSiteRole

        # 1. Mettre à jour les informations de base de l'utilisateur
        if 'login' in data:
            # Vérifier si le nouveau login est déjà utilisé par un autre utilisateur
            existing_user = User.query.filter(User.login == data['login'], User.id != user_id).first()
            if existing_user:
                return jsonify({'error': 'Ce login est déjà utilisé par un autre utilisateur'}), 400
            user.login = data['login']

        if 'password' in data:
            user.set_password(data['password'])

        # 2. Mettre à jour les relations user-site-role si fournies
        relations = []

        if 'rolesBySite' in data:
            roles_by_site = data['rolesBySite']
            replace_existing = data.get('replaceExistingRelations', False)

            # Si on remplace toutes les relations existantes
            if replace_existing:
                try:
                    # Récupérer toutes les relations existantes pour les supprimer une par une
                    existing_relations = UserSiteRole.query.filter_by(user_id=user_id).all()
                    current_app.logger.info(f"Found {len(existing_relations)} existing relations for user {user_id}")

                    # Log each relation for debugging
                    for relation in existing_relations:
                        current_app.logger.info(f"Deleting relation: user_id={relation.user_id}, site_id={relation.site_id}, role_id={relation.role_id}")
                        db.session.delete(relation)

                    # Commit immédiat de la suppression
                    db.session.commit()
                    current_app.logger.info(f"Deleted {len(existing_relations)} existing relations for user {user_id}")
                except Exception as delete_error:
                    db.session.rollback()
                    current_app.logger.error(f"Error deleting existing relations: {delete_error}")
                    return jsonify({'error': f"Erreur lors de la suppression des relations existantes: {str(delete_error)}"}), 500

                # Créer un dictionnaire pour suivre les relations déjà créées
                created_relations = set()

                # Nouvelle session pour les insertions
                try:
                    # Vérifier d'abord s'il existe des relations qui pourraient causer des conflits
                    # Utiliser une requête SQL directe pour s'assurer qu'aucune relation n'existe
                    for site_id_str, role_id in roles_by_site.items():
                        try:
                            site_id = int(site_id_str)
                            role_id = int(role_id)
                        except (ValueError, TypeError):
                            continue  # Ignorer les valeurs non numériques

                        # Vérifier si la relation existe déjà dans la base de données avec une requête SQL directe
                        sql = text(f"SELECT * FROM user_site_role WHERE user_id = {user_id} AND site_id = {site_id}")
                        result = db.session.execute(sql).fetchall()

                        if result:
                            current_app.logger.warning(f"Found {len(result)} existing relations with user_id={user_id}, site_id={site_id}")
                            # Supprimer toutes les relations avec ce user_id et site_id
                            delete_sql = text(f"DELETE FROM user_site_role WHERE user_id = {user_id} AND site_id = {site_id}")
                            db.session.execute(delete_sql)
                            db.session.commit()  # Commit immédiatement pour s'assurer que la suppression est appliquée
                            current_app.logger.warning(f"Deleted all relations with user_id={user_id}, site_id={site_id}")

                    # Les suppressions ont déjà été commitées individuellement

                    # Maintenant créer les nouvelles relations
                    for site_id_str, role_id in roles_by_site.items():
                        try:
                            site_id = int(site_id_str)
                            role_id = int(role_id)
                        except (ValueError, TypeError):
                            continue  # Ignorer les valeurs non numériques

                        # Vérifier l'existence du site et du rôle
                        site = Site.query.get(site_id)
                        role = Role.query.get(role_id)

                        if not site or not role:
                            continue  # Ignorer les sites ou rôles non existants

                        # Vérifier si nous avons déjà créé cette relation (pour éviter les doublons)
                        relation_key = (user_id, site_id, role_id)
                        if relation_key in created_relations:
                            continue

                        # Vérifier une dernière fois si la relation existe déjà
                        check_sql = text(f"SELECT COUNT(*) FROM user_site_role WHERE user_id = {user_id} AND site_id = {site_id} AND role_id = {role_id}")
                        count = db.session.execute(check_sql).scalar()

                        if count > 0:
                            current_app.logger.warning(f"Relation already exists and will be skipped: user_id={user_id}, site_id={site_id}, role_id={role_id}")
                            continue

                        try:
                            # Vérifier une dernière fois si la relation existe et la supprimer si nécessaire
                            check_and_delete_sql = text(f"""
                            DELETE FROM user_site_role 
                            WHERE user_id = {user_id} AND site_id = {site_id} AND role_id = {role_id}
                            """)
                            db.session.execute(check_and_delete_sql)
                            db.session.commit()  # Commit la suppression avant d'insérer

                            # Créer la relation avec une requête SQL directe pour éviter les problèmes d'ORM
                            insert_sql = text(f"""
                            INSERT INTO user_site_role (user_id, site_id, role_id, created_at, updated_at) 
                            VALUES ({user_id}, {site_id}, {role_id}, GETDATE(), GETDATE())
                            """)
                            db.session.execute(insert_sql)
                            db.session.commit()  # Commit après chaque insertion pour éviter les conflits

                            created_relations.add(relation_key)
                            current_app.logger.info(f"Successfully created relation: user_id={user_id}, site_id={site_id}, role_id={role_id}")

                            relations.append({
                                'site_id': site_id,
                                'site_name': site.name,
                                'role_id': role_id,
                                'role_name': role.name,
                                'status': 'created'
                            })
                        except Exception as relation_error:
                            db.session.rollback()
                            current_app.logger.error(f"Error creating relation: user_id={user_id}, site_id={site_id}, role_id={role_id}, error={relation_error}")

                            # Si c'est une violation de clé primaire, essayer de supprimer explicitement et réessayer
                            if "Violation of PRIMARY KEY constraint" in str(relation_error):
                                try:
                                    current_app.logger.warning(f"Primary key violation detected. Attempting to explicitly delete and retry.")
                                    # Supprimer explicitement avec une requête directe
                                    delete_sql = text(f"DELETE FROM user_site_role WHERE user_id = {user_id} AND site_id = {site_id}")
                                    db.session.execute(delete_sql)
                                    db.session.commit()

                                    # Réessayer l'insertion
                                    insert_sql = text(f"""
                                    INSERT INTO user_site_role (user_id, site_id, role_id, created_at, updated_at) 
                                    VALUES ({user_id}, {site_id}, {role_id}, GETDATE(), GETDATE())
                                    """)
                                    db.session.execute(insert_sql)
                                    db.session.commit()

                                    created_relations.add(relation_key)
                                    current_app.logger.info(f"Successfully created relation on retry: user_id={user_id}, site_id={site_id}, role_id={role_id}")

                                    relations.append({
                                        'site_id': site_id,
                                        'site_name': site.name,
                                        'role_id': role_id,
                                        'role_name': role.name,
                                        'status': 'created_after_retry'
                                    })
                                except Exception as retry_error:
                                    db.session.rollback()
                                    current_app.logger.error(f"Error on retry: user_id={user_id}, site_id={site_id}, role_id={role_id}, error={retry_error}")

                            # Continue with other relations instead of failing completely
                            continue

                    current_app.logger.info(f"Created {len(created_relations)} new relations for user {user_id}")
                except Exception as insert_error:
                    db.session.rollback()
                    current_app.logger.error(f"Error creating new relations: {insert_error}")
                    return jsonify({'error': f"Erreur lors de la création des nouvelles relations: {str(insert_error)}"}), 500
            else:
                # Traitement normal pour les mises à jour sans remplacement complet
                for site_id_str, role_id in roles_by_site.items():
                    try:
                        site_id = int(site_id_str)
                    except ValueError:
                        continue  # Ignorer les clés non numériques

                    try:
                        role_id = int(role_id)
                    except (ValueError, TypeError):
                        return jsonify({'error': f'ID de rôle invalide: {role_id}'}), 400

                    # Vérifier l'existence du site et du rôle
                    site = Site.query.get(site_id)
                    role = Role.query.get(role_id)

                    if not site:
                        return jsonify({'error': f'Site avec ID {site_id} non trouvé'}), 404

                    if not role:
                        return jsonify({'error': f'Rôle avec ID {role_id} non trouvé'}), 404

                    # Vérifier si une relation identique existe déjà
                    existing_relation = UserSiteRole.query.filter_by(
                        user_id=user_id,
                        site_id=site_id,
                        role_id=role_id
                    ).first()

                    if existing_relation:
                        # La relation existe déjà, pas besoin de la modifier
                        relations.append({
                            'site_id': site_id,
                            'site_name': site.name,
                            'role_id': role_id,
                            'role_name': role.name,
                            'status': 'unchanged'
                        })
                    else:
                        # Vérifier si une relation avec le même site mais un rôle différent existe
                        existing_site_relation = UserSiteRole.query.filter_by(
                            user_id=user_id,
                            site_id=site_id
                        ).first()

                        if existing_site_relation:
                            # Mettre à jour le rôle pour ce site
                            old_role_id = existing_site_relation.role_id
                            old_role = Role.query.get(old_role_id)
                            existing_site_relation.role_id = role_id
                            relations.append({
                                'site_id': site_id,
                                'site_name': site.name,
                                'role_id': role_id,
                                'role_name': role.name,
                                'old_role_id': old_role_id,
                                'old_role_name': old_role.name if old_role else None,
                                'status': 'updated'
                            })
                        else:
                            # Créer une nouvelle relation
                            new_relation = UserSiteRole(user_id=user_id, site_id=site_id, role_id=role_id)
                            db.session.add(new_relation)
                            relations.append({
                                'site_id': site_id,
                                'site_name': site.name,
                                'role_id': role_id,
                                'role_name': role.name,
                                'status': 'created'
                            })

        # Valider les modifications
        db.session.commit()

        # Préparer la réponse
        result = {
            'id': user.id,
            'login': user.login,
            'relations': relations
        }

        return jsonify(result), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in update_user_with_relations: {e}")
        return jsonify({'error': str(e)}), 500
