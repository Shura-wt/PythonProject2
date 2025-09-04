from .batiment_routes import batiment_bp
from .etage_carte_routes import etage_carte_bp
from .etage_routes import etage_bp
from .site_carte_routes import site_carte_bp
from .site_routes import site_bp
from .carte_routes import carte_bp
from .user_routes import user_bp
from .user_site_routes import user_site_bp
from .baes_routes import baes_bp
from .status_routes import status_bp
from .auth import auth_bp
from .role_routes import role_bp
from .user_site_role_routes import user_site_role_bp
from .general_routes import general_routes_bp
from .config_routes import config_bp

def init_app(app):
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(role_bp, url_prefix='/roles')
    app.register_blueprint(carte_bp, url_prefix='/cartes')
    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(user_site_bp, url_prefix='/users/sites')
    app.register_blueprint(site_bp, url_prefix='/sites')
    app.register_blueprint(batiment_bp, url_prefix='/batiments')
    app.register_blueprint(etage_bp, url_prefix='/etages')
    app.register_blueprint(etage_carte_bp, url_prefix='/etages/carte')
    app.register_blueprint(site_carte_bp, url_prefix='/sites/carte')
    app.register_blueprint(baes_bp, url_prefix='/baes')
    # Register status_bp with both URL prefixes for backward compatibility
    app.register_blueprint(status_bp, url_prefix='/erreurs')
    # Register the same blueprint with the new URL prefix, using a unique name
    app.register_blueprint(status_bp, url_prefix='/status', name='status_bp_new')
    app.register_blueprint(user_site_role_bp, url_prefix='/user_site_role')
    app.register_blueprint(general_routes_bp, url_prefix='/general')
    app.register_blueprint(config_bp, url_prefix='/config')

