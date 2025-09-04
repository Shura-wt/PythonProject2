import os

from flask import Blueprint, request, jsonify ,url_for, current_app
from flasgger import swag_from
from ..models.user import User
from ..models.site import Site
from ..models.batiment import Batiment
from ..models.etage import Etage
from ..models.baes import Baes
from ..models.status import Status

general_routes_bp = Blueprint('general_routes_bp', __name__)


def status_to_dict(err: Status) -> dict:
    return {
        'id': err.id,
        'erreur': err.erreur,
        'temperature': err.temperature,
        'vibration': err.vibration,
        'timestamp': err.timestamp.isoformat(),
        'is_solved': err.is_solved,
        'is_ignored': err.is_ignored,
    }


def baes_to_dict(b: Baes) -> dict:
    return {
        'id': b.id,
        'name': b.name,
        'position': b.position,
        'statuses': [status_to_dict(e) for e in b.statuses] if b.statuses else [],
    }


def etage_to_dict(e: Etage) -> dict:
    carte_dict = None
    if e.carte:
        filename = os.path.basename(e.carte.chemin)
        # Générer l'URL complète en se basant sur la route 'uploaded_file'
        public_url = url_for('carte_bp.uploaded_file', filename=filename, _external=True)
        carte_dict = {
            'id': e.carte.id,
            'chemin': public_url,
            'site_id': e.carte.site_id,
            'etage_id': e.carte.etage_id,
            'center_lat': e.carte.centerLat if hasattr(e.carte, 'centerLat') else e.carte.center_lat,
            'center_lng': e.carte.centerLng if hasattr(e.carte, 'centerLng') else e.carte.center_lng,
            'zoom': e.carte.zoom
        }

    return {
        'id': e.id,
        'name': e.name,
        'baes': [baes_to_dict(b) for b in e.baes] if e.baes else [],
        'carte': carte_dict
    }


def batiment_to_dict(bat: Batiment) -> dict:
    return {
        'id': bat.id,
        'name': bat.name,
        'polygon_points': bat.polygon_points,
        'etages': [etage_to_dict(e) for e in bat.etages] if bat.etages else [],
    }


def site_to_dict(s: Site) -> dict:
    # Si le site a une carte, générer l'URL publique à partir du chemin stocké
    carte_dict = None
    if s.carte:
        # Récupérer le nom de fichier à partir du chemin stocké
        filename = os.path.basename(s.carte.chemin)
        # Générer l'URL complète en se basant sur la route 'uploaded_file'
        public_url = url_for('carte_bp.uploaded_file', filename=filename, _external=True)
        carte_dict = {
            'id': s.carte.id,
            'chemin': public_url,  # URL générée au lieu du chemin local
            'site_id': s.carte.site_id,
            'etage_id': s.carte.etage_id,  # Assurez-vous d'avoir la bonne valeur ici
            'center_lat': s.carte.centerLat if hasattr(s.carte, 'centerLat') else s.carte.center_lat,
            'center_lng': s.carte.centerLng if hasattr(s.carte, 'centerLng') else s.carte.center_lng,
            'zoom': s.carte.zoom,
        }
    return {
        'id': s.id,
        'name': s.name,
        'batiments': [batiment_to_dict(bat) for bat in s.batiments] if s.batiments else [],
        'carte': carte_dict,
    }


@swag_from({
    'tags': ['general'],
    'description': "Retourne pour un utilisateur donné l'ensemble des sites auxquels il a accès, "
                   "ainsi que pour chaque site, la liste de ses bâtiments, pour chaque bâtiment, la liste de ses étages, "
                   "pour chaque étage, la liste de ses BAES et, pour chaque BAES, l'historique de ses statuts. "
                   "Pour les cartes, seule l'id est retournée.",
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "L'ID de l'utilisateur"
        }
    ],
    'responses': {
        '200': {
            'description': "Données complètes de l'utilisateur",
            'schema': {
                'type': 'object',
                'properties': {
                    'sites': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer', 'example': 1},
                                'name': {'type': 'string', 'example': "Site par défaut"},
                                'batiments': {
                                    'type': 'array',
                                    'items': {
                                        'type': 'object',
                                        'properties': {
                                            'id': {'type': 'integer', 'example': 1},
                                            'name': {'type': 'string', 'example': "Batiment A"},
                                            'polygon_points': {'type': 'object'},
                                            'etages': {
                                                'type': 'array',
                                                'items': {
                                                    'type': 'object',
                                                    'properties': {
                                                        'id': {'type': 'integer', 'example': 1},
                                                        'name': {'type': 'string', 'example': "Etage 1"},
                                                        'baes': {
                                                            'type': 'array',
                                                            'items': {
                                                                'type': 'object',
                                                                'properties': {
                                                                    'id': {'type': 'integer', 'example': 1},
                                                                    'name': {'type': 'string', 'example': "BAES 1"},
                                                                    'position': {'type': 'object'},
                                                                    'erreurs': {
                                                                        'type': 'array',
                                                                        'items': {
                                                                            'type': 'object',
                                                                            'properties': {
                                                                                'id': {'type': 'integer', 'example': 1},
                                                                                'erreur': {'type': 'integer',
                                                                                                'example': 1},
                                                                                'timestamp': {'type': 'string',
                                                                                              'example': "2025-04-03T12:34:56Z"},
                                                                                'is_solved': {'type': 'boolean', 'example': False},
                                                                                'is_ignored': {'type': 'boolean', 'example': False},
                                                                                'temperature': {'type': 'number', 'example': 22.5},
                                                                                'vibration': {'type': 'boolean', 'example': True}
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        },
                                                        'carte': {
                                                            'type': 'object',
                                                            'properties': {
                                                                'id': {'type': 'integer', 'example': 1},
                                                                'chemin': {'type': 'string',
                                                                           'example': "/path/to/image.png"},
                                                                'etage_id': {'type': 'integer', 'example': 1},
                                                                'site_id': {'type': 'integer', 'example': 1},
                                                                'center_lat': {'type': 'number',
                                                                               'example': 48.8566},
                                                                'center_lng': {'type': 'number',
                                                                               'example': 2.3522},
                                                                'zoom': {'type': 'integer', 'example': 10}
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                },
                                'carte': {
                                    'type': 'object',
                                    'properties': {
                                        'id': {'type': 'integer', 'example': 1},
                                        'chemin': {'type': 'string',
                                                 'example': "/path/to/image.png", },
                                        'etage_id': {'type': 'integer', 'example': 1},
                                        'site_id': {'type': 'integer', 'example': 1},
                                        'center_lat': {'type': 'number',
                                                       'example': 48.8566},
                                        'center_lng': {'type': 'number',
                                                       'example': 2.3522},
                                        'zoom': {'type': 'integer', 'example': 10}

                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        '404': {
            'description': "Utilisateur non trouvé."
        }
    }
})
@general_routes_bp.route('/user/<int:user_id>/alldata', methods=['GET'])
def get_all_user_site_data(user_id):
    """
    Route qui retourne pour un utilisateur donné l'ensemble des sites auxquels il a accès,
    ainsi que la hiérarchie complète :
      Site -> Batiment -> Etage -> BAES -> HistoriqueErreur
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé.'}), 404

    # Récupération des sites distincts via l'association user_site_roles
    sites = []
    seen = set()
    for assoc in user.user_site_roles.all():
        site = assoc.site
        if site and site.id not in seen:
            seen.add(site.id)
            sites.append(site)

    sites_data = [site_to_dict(site) for site in sites]
    return jsonify({'sites': sites_data}), 200

@swag_from({
    'tags': ['general'],
    'description': "Retourne toutes les informations liées à un bâtiment : ses étages, les cartes associées et les BAES présents.",
    'parameters': [
        {
            'name': 'batiment_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': "L'ID du bâtiment"
        }
    ],
    'responses': {
        '200': {
            'description': "Données complètes du bâtiment",
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'name': {'type': 'string', 'example': "Batiment A"},
                    'polygon_points': {'type': 'object'},
                    'etages': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer', 'example': 1},
                                'name': {'type': 'string', 'example': "Etage 1"},
                                'baes': {
                                    'type': 'array',
                                    'items': {
                                        'type': 'object',
                                        'properties': {
                                            'id': {'type': 'integer', 'example': 1},
                                            'name': {'type': 'string', 'example': "BAES 1"},
                                            'position': {'type': 'object'},
                                            'erreurs': {
                                                'type': 'array',
                                                'items': {
                                                    'type': 'object',
                                                    'properties': {
                                                        'id': {'type': 'integer', 'example': 1},
                                                        'erreur': {'type': 'integer', 'example': 1},
                                                        'temperature': {'type': 'number', 'example': 22.5},
                                                        'vibration': {'type': 'boolean', 'example': True},
                                                        'timestamp': {'type': 'string', 'example': "2025-04-03T12:34:56Z"},
                                                        'is_solved': {'type': 'boolean', 'example': False},
                                                        'is_ignored': {'type': 'boolean', 'example': False}
                                                    }
                                                }
                                            }
                                        }
                                    }
                                },
                                'carte': {
                                    'type': 'object',
                                    'properties': {
                                        'id': {'type': 'integer', 'example': 1},
                                        'chemin': {'type': 'string', 'example': "/path/to/image.png"},
                                        'etage_id': {'type': 'integer', 'example': 1},
                                        'site_id': {'type': 'integer', 'example': 1},
                                        'center_lat': {'type': 'number', 'example': 48.8566},
                                        'center_lng': {'type': 'number', 'example': 2.3522},
                                        'zoom': {'type': 'integer', 'example': 10}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        '404': {
            'description': "Bâtiment non trouvé."
        }
    }
})
@general_routes_bp.route('/batiment/<int:batiment_id>/alldata', methods=['GET'])
def get_all_batiment_data(batiment_id):
    """
    Route qui retourne pour un bâtiment donné l'ensemble de ses étages,
    ainsi que pour chaque étage, sa carte et ses BAES avec leurs erreurs.
    """
    batiment = Batiment.query.get(batiment_id)
    if not batiment:
        return jsonify({'error': 'Bâtiment non trouvé.'}), 404

    batiment_data = batiment_to_dict(batiment)
    return jsonify(batiment_data), 200

@swag_from({
    'tags': ['general'],
    'description': "Retourne la version actuelle de l'API.",
    'responses': {
        '200': {
            'description': "Version de l'API",
            'schema': {
                'type': 'object',
                'properties': {
                    'version': {'type': 'string', 'example': "1.0"}
                }
            }
        }
    }
})
@general_routes_bp.route('/version', methods=['GET'])
def get_api_version():
    """
    Route qui retourne la version actuelle de l'API.
    """
    # Retourner la version de l'API (définie comme "1.0" dans app.py)
    return jsonify({'version': '1.0'}), 200
