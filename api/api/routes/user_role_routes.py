# routes/user_role_routes.py
from flask import Blueprint, request, jsonify, current_app
from flasgger import swag_from
from ..models.user import User
from ..models.role import Role
from ..models import db

user_role_bp = Blueprint('user_role_bp', __name__)
#
# @user_role_bp.route('/<int:user_id>/roles', methods=['GET'])
# @swag_from({
#     'tags': ['User-Role Relations'],
#     'description': "Récupère la liste des rôles associés à un utilisateur donné.",
#     'parameters': [
#         {
#             'name': 'user_id',
#             'in': 'path',
#             'type': 'integer',
#             'required': True,
#             'description': "ID de l'utilisateur"
#         }
#     ],
#     'responses': {
#         200: {
#             'description': "Liste des rôles de l'utilisateur.",
#             'schema': {
#                 'type': 'array',
#                 'items': {
#                     'type': 'object',
#                     'properties': {
#                         'id': {'type': 'integer', 'example': 1},
#                         'name': {'type': 'string', 'example': 'admin'}
#                     }
#                 }
#             }
#         },
#         404: {'description': "Utilisateur non trouvé."},
#         500: {'description': "Erreur interne."}
#     }
# })
# def get_user_roles(user_id):
#     try:
#         user = User.query.get(user_id)
#         if not user:
#             return jsonify({'error': 'Utilisateur non trouvé'}), 404
#         roles = [{'id': role.id, 'name': role.name} for role in user.roles]
#         return jsonify(roles), 200
#     except Exception as e:
#         current_app.logger.error(f"Error in get_user_roles: {e}")
#         return jsonify({'error': str(e)}), 500
#
# @user_role_bp.route('/<int:user_id>/roles', methods=['POST'])
# @swag_from({
#     'tags': ['User-Role Relations'],
#     'description': "Attribue un rôle à un utilisateur. Le JSON doit contenir 'role_id'.",
#     'consumes': ['application/json'],
#     'parameters': [
#         {
#             'name': 'user_id',
#             'in': 'path',
#             'type': 'integer',
#             'required': True,
#             'description': "ID de l'utilisateur"
#         },
#         {
#             'name': 'body',
#             'in': 'body',
#             'required': True,
#             'schema': {
#                 'type': 'object',
#                 'properties': {
#                     'role_id': {'type': 'integer', 'example': 2}
#                 },
#                 'required': ['role_id']
#             }
#         }
#     ],
#     'responses': {
#         200: {
#             'description': "Rôle ajouté à l'utilisateur avec succès.",
#             'schema': {
#                 'type': 'object',
#                 'properties': {
#                     'message': {'type': 'string', 'example': "Rôle ajouté à l'utilisateur."}
#                 }
#             }
#         },
#         400: {'description': "Mauvaise requête ou rôle déjà associé."},
#         404: {'description': "Utilisateur ou rôle non trouvé."},
#         500: {'description': "Erreur interne."}
#     }
# })
# def add_role_to_user(user_id):
#     try:
#         data = request.get_json()
#         if not data or 'role_id' not in data:
#             return jsonify({'error': "Le champ 'role_id' est requis"}), 400
#         role_id = data['role_id']
#         user = User.query.get(user_id)
#         if not user:
#             return jsonify({'error': 'Utilisateur non trouvé'}), 404
#         role = Role.query.get(role_id)
#         if not role:
#             return jsonify({'error': 'Rôle non trouvé'}), 404
#
#         if role in user.roles:
#             return jsonify({'message': "Rôle déjà associé à l'utilisateur."}), 200
#
#         user.roles.append(role)
#         db.session.commit()
#         return jsonify({'message': "Rôle ajouté à l'utilisateur."}), 200
#     except Exception as e:
#         db.session.rollback()
#         current_app.logger.error(f"Error in add_role_to_user: {e}")
#         return jsonify({'error': str(e)}), 500
#
# @user_role_bp.route('/<int:user_id>/roles/<int:role_id>', methods=['DELETE'])
# @swag_from({
#     'tags': ['User-Role Relations'],
#     'description': "Retire un rôle d'un utilisateur.",
#     'parameters': [
#         {
#             'name': 'user_id',
#             'in': 'path',
#             'type': 'integer',
#             'required': True,
#             'description': "ID de l'utilisateur"
#         },
#         {
#             'name': 'role_id',
#             'in': 'path',
#             'type': 'integer',
#             'required': True,
#             'description': "ID du rôle à retirer"
#         }
#     ],
#     'responses': {
#         200: {
#             'description': "Rôle retiré avec succès.",
#             'schema': {
#                 'type': 'object',
#                 'properties': {
#                     'message': {'type': 'string', 'example': "Rôle retiré de l'utilisateur."}
#                 }
#             }
#         },
#         404: {'description': "Utilisateur ou rôle non trouvé, ou rôle non associé."},
#         500: {'description': "Erreur interne."}
#     }
# })
# def remove_role_from_user(user_id, role_id):
#     try:
#         user = User.query.get(user_id)
#         if not user:
#             return jsonify({'error': 'Utilisateur non trouvé'}), 404
#         role = Role.query.get(role_id)
#         if not role or role not in user.roles:
#             return jsonify({'error': "Rôle non trouvé ou non associé à l'utilisateur"}), 404
#         user.roles.remove(role)
#         db.session.commit()
#         return jsonify({'message': "Rôle retiré de l'utilisateur."}), 200
#     except Exception as e:
#         db.session.rollback()
#         current_app.logger.error(f"Error in remove_role_from_user: {e}")
#         return jsonify({'error': str(e)}), 500
#
# @user_role_bp.route('/<int:user_id>/roles', methods=['PUT'])
# @swag_from({
#     'tags': ['User-Role Relations'],
#     'description': "Remplace l'ensemble des rôles d'un utilisateur. Le JSON doit contenir 'role_ids' (une liste d'ID de rôles).",
#     'consumes': ['application/json'],
#     'parameters': [
#         {
#             'name': 'user_id',
#             'in': 'path',
#             'type': 'integer',
#             'required': True,
#             'description': "ID de l'utilisateur"
#         },
#         {
#             'name': 'body',
#             'in': 'body',
#             'required': True,
#             'schema': {
#                 'type': 'object',
#                 'properties': {
#                     'role_ids': {
#                         'type': 'array',
#                         'items': {'type': 'integer', 'example': 2},
#                         'description': "Liste des ID des rôles à associer"
#                     }
#                 },
#                 'required': ['role_ids']
#             }
#         }
#     ],
#     'responses': {
#         200: {
#             'description': "Les rôles de l'utilisateur ont été mis à jour avec succès.",
#             'schema': {
#                 'type': 'object',
#                 'properties': {
#                     'message': {'type': 'string', 'example': "Les rôles de l'utilisateur ont été mis à jour."}
#                 }
#             }
#         },
#         404: {'description': "Utilisateur ou rôle non trouvé."},
#         500: {'description': "Erreur interne."}
#     }
# })
# def update_user_roles(user_id):
#     try:
#         data = request.get_json()
#         if not data or 'role_ids' not in data:
#             return jsonify({'error': "Le champ 'role_ids' est requis"}), 400
#         role_ids = data['role_ids']
#         user = User.query.get(user_id)
#         if not user:
#             return jsonify({'error': 'Utilisateur non trouvé'}), 404
#         roles = Role.query.filter(Role.id.in_(role_ids)).all()
#         if not roles:
#             return jsonify({'error': 'Aucun rôle trouvé pour les ID fournis'}), 404
#         user.roles = roles
#         db.session.commit()
#         return jsonify({'message': "Les rôles de l'utilisateur ont été mis à jour."}), 200
#     except Exception as e:
#         db.session.rollback()
#         current_app.logger.error(f"Error in update_user_roles: {e}")
#         return jsonify({'error': str(e)}), 500
