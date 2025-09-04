from flask import current_app
from .models import db
from .models.user import User
from .models.site import Site
from .models.role import Role
from .models.user_site_role import UserSiteRole

def create_default_data():
    """
    Create default data for the application:
    - Default roles
    - Default site
    - Default users with appropriate roles
    - Super-admin user with default site association (but with global access)
    """
    current_app.logger.debug("Création des données par défaut...")

    # 1. Création des rôles par défaut
    default_roles = ['user', 'technicien', 'admin', 'super-admin']
    roles = {}

    for role_name in default_roles:
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name)
            db.session.add(role)
            current_app.logger.debug("Création du rôle %s", role_name)
        roles[role_name] = role
    db.session.commit()

    # 2. Création d'un site par défaut
    default_site_name = "Site par défaut"
    site = Site.query.filter_by(name=default_site_name).first()
    if not site:
        site = Site(name=default_site_name)
        db.session.add(site)
        current_app.logger.debug("Création du site %s", default_site_name)
    db.session.commit()

    # 3. Création des utilisateurs par défaut et association via UserSiteRole
    default_users = {
        'user': {'login': 'user', 'password': 'user_password'},
        'technicien': {'login': 'technicien', 'password': 'tech_password'},
        'admin': {'login': 'admin', 'password': 'admin_password'},
    }

    # Création des utilisateurs standard (avec site)
    for role_name, user_data in default_users.items():
        user = User.query.filter_by(login=user_data['login']).first()
        if not user:
            user = User(login=user_data['login'])
            user.set_password(user_data['password'])
            db.session.add(user)
            current_app.logger.debug("Création de l'utilisateur %s", user_data['login'])
            db.session.commit()

        association = UserSiteRole.query.filter_by(
            user_id=user.id,
            site_id=site.id,
            role_id=roles[role_name].id
        ).first()

        if not association:
            association = UserSiteRole(
                user_id=user.id,
                site_id=site.id,
                role_id=roles[role_name].id
            )
            db.session.add(association)
            current_app.logger.debug("Association de l'utilisateur %s au rôle %s sur le site %s", 
                                    user.login, role_name, site.name)

    # 4. Création du super-admin avec association au site par défaut
    superadmin_data = {'login': 'superadmin', 'password': 'superadmin_password'}
    superadmin = User.query.filter_by(login=superadmin_data['login']).first()

    if not superadmin:
        superadmin = User(login=superadmin_data['login'])
        superadmin.set_password(superadmin_data['password'])
        db.session.add(superadmin)
        current_app.logger.debug("Création de l'utilisateur super-admin")
        db.session.commit()

    # Association du super-admin au rôle super-admin avec le site par défaut
    # Note: Le super-admin a accès à tous les sites, mais nous devons l'associer à un site
    # car la colonne site_id ne peut pas être NULL (contrainte de clé primaire)
    superadmin_role = roles['super-admin']
    association = UserSiteRole.query.filter_by(
        user_id=superadmin.id,
        site_id=site.id,
        role_id=superadmin_role.id
    ).first()

    if not association:
        association = UserSiteRole(
            user_id=superadmin.id,
            site_id=site.id,  # Utilisation du site par défaut pour satisfaire la contrainte de clé primaire
            role_id=superadmin_role.id
        )
        db.session.add(association)
        current_app.logger.debug("Association de l'utilisateur super-admin au rôle super-admin avec le site par défaut")

    db.session.commit()
