from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Importation des modèles une fois que db est défini
from .batiment import Batiment
from .role import Role
from .site import Site
from .carte import Carte
from .etage import Etage
from .baes import Baes
from .status import Status
from .user import User
from .user_site_role import UserSiteRole  # Nouveau modèle d'association
from .config import Config  # Modèle de configuration
