# BAES API – Documentation des routes avec schémas JSON

Dernière mise à jour: 2025-09-01 11:29

Cette documentation fournit, pour chaque route, l’URL appelée, les paramètres, les corps JSON envoyés/reçus et les types de données. Les types suivent la convention JSON: string, integer, number, boolean, object, array, null. Les dates sont des strings au format ISO 8601.

Notes importantes
- Authentification: certaines routes peuvent exiger une session utilisateur (ex: logout). Le login retourne un JWT dans la réponse pour usage côté client.
- Legacy: les routes de statut sont disponibles sous le préfixe principal "/status". Par compatibilité, elles existent aussi sous "/erreurs" (mêmes chemins relatifs et mêmes schémas).
- Formats: sauf mention contraire, Content-Type application/json pour requêtes et réponses.

Sommaire des sections
- Authentification (/auth)
- Utilisateurs (/users)
- Rôles Utilisateur-Site (/users/sites) et Assignations/Rôles globaux (/user_site_role)
- Sites (/sites)
- Bâtiments (/batiments)
- Étages (/etages)
- BAES (/baes)
- Statuts/Erreurs (/status)
- Cartes (/cartes), Cartes par Site (/sites/carte), Cartes par Étage (/etages/carte)
- Routes Générales (/general)
- Rôles (/roles)
- Configuration (/config)


## Authentification (/auth)
- POST /auth/login
  - Requête (body): { "login": string, "password": string }
  - Réponses:
    - 200 OK: {
        "message": string,
        "user_id": integer,
        "sites": [ { "id": integer, "name": string, "roles": [ { "id": integer, "name": string } ] } ],
        "global_roles"?: [ { "id": integer, "name": string } ],
        "token": string
      }
    - 400 Bad Request: { "error": string }
    - 401 Unauthorized: { "error": string }
- OPTIONS /auth/login (pré-vol CORS)
- POST /auth/logout (stateless)
  - Requête: header Authorization: Bearer <JWT> (optionnel)
  - Réponse 200 OK: { "message": string }
- GET /auth/logout (compat)
  - Réponse 200 OK: { "message": string }
- OPTIONS /auth/logout (pré-vol CORS)


## Utilisateurs (/users)
- GET /users/
  - Réponse 200: array d’utilisateurs. Typiquement: [ { "id": integer, "login": string, ... } ]
- GET /users/{user_id}
  - Paramètres path: user_id: integer
  - Réponse 200: { "id": integer, "login": string, ... } | 404: { "error": string }
- POST /users/
  - Requête: { "login": string, "password": string, ... }
  - Réponse 201: utilisateur créé { "id": integer, "login": string, ... }
- PUT /users/{user_id}
  - Requête: { champs à mettre à jour }
  - Réponse 200: utilisateur mis à jour | 404
- DELETE /users/{user_id}
  - Réponse 200: { "message": string } | 404
- POST /users/create-with-relations
  - Requête: {
      "user": { "login": string, "password": string, ... },
      "relations": [ { "site_id": integer|null, "role_id": integer } ]
    }
  - Réponse 201: { "user": { ... }, "relations": [ ... ] }
- PUT /users/{user_id}/update-with-relations
  - Requête: même structure que ci-dessus
  - Réponse 200: { "user": { ... }, "relations": [ ... ] }


## Rôles Utilisateur-Site (/users/sites)
- GET /users/sites/{user_id}/sites
  - Réponse 200: [ { "id": integer, "name": string, "roles": [ { id, name } ] } ]
- POST /users/sites/{user_id}/sites
  - Requête: { "site_id": integer, "role_id"?: integer }
  - Réponse 201: association créée { ... }
- DELETE /users/sites/{user_id}/sites/{site_id}
  - Réponse 200: { "message": string }

## Assignations et Rôles globaux (/user_site_role)
- GET /user_site_role
  - Réponse 200: [ { "id": integer, "user_id": integer, "site_id": integer|null, "role_id": integer, ... } ]
- GET /user_site_role/{id}
  - Réponse 200: { ... } | 404
- POST /user_site_role
  - Requête: { "user_id": integer, "site_id": integer|null, "role_id": integer }
  - Réponse 201: { ... }
- PUT|PATCH /user_site_role/{id}
  - Requête: { champs à modifier }
  - Réponse 200: { ... }
- DELETE /user_site_role/{id}
  - Réponse 200: { "message": string }
- GET /user_site_role/user/{user_id}/permissions
  - Réponse 200: { "sites": [ ... ], "global_roles": [ ... ] }
- GET /user_site_role/site/{site_id}/users
  - Réponse 200: [ { "user": { ... }, "roles": [ ... ] } ]
- DELETE /user_site_role/user/{user_id}/site/{site_id}
  - Réponse 200: { "deleted": integer }
- POST /user_site_role/user/{user_id}/global-role
  - Requête: { "role_id": integer }
  - Réponse 201: { ... }


## Sites (/sites)
- GET /sites/
  - Réponse 200: [ { "id": integer, "name": string } ]
- GET /sites/{site_id}
  - Réponse 200: { "id": integer, "name": string } | 404
- POST /sites/
  - Requête: { "name": string }
  - Réponse 201: { "id": integer, "name": string } | 400
- PUT /sites/{site_id}
  - Requête: { "name"?: string }
  - Réponse 200: { "id": integer, "name": string } | 404
- DELETE /sites/{site_id}
  - Réponse 200: {
      "message": string,
      "batiments_deleted": integer,
      "etages_deleted": integer,
      "baes_deleted": integer,
      "statuses_deleted": integer,
      "cartes_deleted": integer,
      "user_site_roles_preserved": integer
    } | 404


## Bâtiments (/batiments)
- GET /batiments/
  - Réponse 200: [ { "id": integer, "name": string, "polygon_points": object|null, "site_id": integer|null } ]
- GET /batiments/{batiment_id}
  - Réponse 200: { id, name, polygon_points, site_id } | 404
- POST /batiments/
  - Requête: { "name": string, "polygon_points"?: object, "site_id"?: integer }
  - Réponse 201: { id, name, polygon_points, site_id } | 400
- PUT /batiments/{batiment_id}
  - Requête: { "name"?: string, "polygon_points"?: object, "site_id"?: integer|null }
  - Réponse 200: { id, name, polygon_points, site_id } | 404
- DELETE /batiments/{batiment_id}
  - Réponse 200: { "message": string } | 404
- GET /batiments/{batiment_id}/floors
  - Réponse 200: [ { "id": integer, "name": string } ]


## Étages (/etages)
- GET /etages/
  - Réponse 200: [ { "id": integer, "name": string, "batiment_id": integer } ]
- GET /etages/{etage_id}
  - Réponse 200: { "id": integer, "name": string, "batiment_id": integer } | 404
- POST /etages/
  - Requête: { "name": string, "batiment_id": integer }
  - Réponse 201: { id, name, batiment_id } | 400
- PUT /etages/{etage_id}
  - Requête: { "name"?: string }
  - Réponse 200: { id, name, batiment_id } | 404
- DELETE /etages/{etage_id}
  - Réponse 200: { "message": string } | 404
- GET /etages/{etage_id}/baes
  - Réponse 200: [ { "id": integer, "name": string, "label"?: string, "position"?: object, "etage_id": integer } ]


## BAES (/baes)
- GET /baes/
  - Réponse 200: [ { "id": integer, "name": string, "label"?: string, "position"?: object, "etage_id": integer|null } ]
- GET /baes/{baes_id}
  - Réponse 200: { id, name, label?, position?, etage_id?, created_at, updated_at } | 404
- POST /baes/
  - Requête: { "name": string, "label"?: string, "position"?: object, "etage_id"?: integer|null }
  - Réponse 201: { id, name, label?, position?, etage_id? }
- PUT /baes/{baes_id}
  - Requête: { champs BAES à modifier }
  - Réponse 200: { ... } | 404
- DELETE /baes/{baes_id}
  - Réponse 200: { "message": string } | 404
- GET /baes/without-etage
  - Réponse 200: [ BAES sans etage_id ]
- GET /baes/user/{user_id}
  - Réponse 200: [ BAES visibles pour l’utilisateur ]


## Statuts / Erreurs (/status) [alias: /erreurs]
Les mêmes schémas s’appliquent à /erreurs/...
- GET /status/
  - Réponse 200: [ {
      "id": integer,
      "baes_id": integer,
      "erreur": integer,
      "is_solved": boolean,
      "is_ignored": boolean,
      "temperature"?: number|null,
      "vibration"?: boolean|null,
      "timestamp"?: string|null,
      "updated_at"?: string|null
    } ]
- GET /status/{status_id}
  - Réponse 200: { ... comme ci-dessus ... } | 404
- GET /status/after/{updated_at}
  - Param path: updated_at: string (ISO 8601)
  - Réponse 200: [ { ... } ]
- GET /status/baes/{baes_id}
  - Réponse 200: [ { ... } ]
- POST /status/
  - Requête: {
      "baes_id": integer,
      "erreur": integer,
      "temperature"?: number,
      "vibration"?: boolean,
      "timestamp"?: string
    }
  - Réponse 201: { statut créé (mêmes champs + id, created/updated) }
- PUT /status/{status_id}/status
  - Requête: { "is_solved"?: boolean, "is_ignored"?: boolean, "acknowledged_by_user_id"?: integer|null, "acknowledged_at"?: string|null }
  - Réponse 200: { ... }
- PUT /status/baes/{baes_id}/type/{_erreur}
  - Requête: { "is_solved"?: boolean, "is_ignored"?: boolean }
  - Réponse 200: { ... }
- GET /status/acknowledged
  - Réponse 200: [ { ... } ]
- GET /status/etage/{etage_id}
  - Réponse 200: [ { ... } ]
- GET /status/latest
  - Réponse 200: [ { ... } ]
- DELETE /status/{status_id}
  - Réponse 200: { "message": string } | 404
- GET /status/user/{user_id}
  - Réponse 200: [ { ... } ]


## Cartes (/cartes)
- POST /cartes/upload-carte
  - FormData (multipart): file (image png/jpg/jpeg), champs JSON/numériques optionnels: center_lat: number, center_lng: number, zoom: number, site_id: integer|null, etage_id: integer|null
  - Réponse 201: { "id": integer, "chemin": string, "site_id"?: integer|null, "etage_id"?: integer|null, "center_lat"?: number, "center_lng"?: number, "zoom"?: number, "created_at": string, "updated_at": string }
- GET /cartes/uploads/{filename}
  - Réponse 200: fichier image (image/png ou image/jpeg)
- GET /cartes/carte/{carte_id}
  - Réponse 200: { id, chemin, site_id?, etage_id?, center_lat, center_lng, zoom, created_at, updated_at } | 404
- PUT /cartes/carte/{carte_id}
  - Requête: { "center_lat"?: number, "center_lng"?: number, "zoom"?: number, "site_id"?: integer|null, "etage_id"?: integer|null }
  - Réponse 200: { ... } | 404

### Cartes par Site (/sites/carte)
- POST /sites/carte/{site_id}/assign
  - Requête: { "chemin"?: string, "center_lat"?: number, "center_lng"?: number, "zoom"?: number }
  - Réponse 201: { carte: { ... } }
- GET /sites/carte/get_by_site/{site_id}
  - Réponse 200: { carte: { ... } } | 404
- GET /sites/carte/get_by_floor/{floor_id}
  - Réponse 200: { carte: { ... } } | 404
- PUT /sites/carte/update_by_site/{site_id}
  - Requête: { "center_lat"?: number, "center_lng"?: number, "zoom"?: number }
  - Réponse 200: { carte: { ... } } | 404

### Cartes par Étage (/etages/carte)
- POST /etages/carte/{etage_id}/assign
  - Requête: { "chemin"?: string, "center_lat"?: number, "center_lng"?: number, "zoom"?: number }
  - Réponse 201: { carte: { ... } }
- PUT /etages/carte/update_by_site_etage/{site_id}/{etage_id}
  - Requête: { "center_lat"?: number, "center_lng"?: number, "zoom"?: number }
  - Réponse 200: { carte: { ... } }


## Routes Générales (/general)
- GET /general/user/{user_id}/alldata
  - Réponse 200: {
      "sites": [ { "id": integer, "name": string, "batiments": [ { "id": integer, "name": string, ... } ], ... } ]
    }
- GET /general/batiment/{batiment_id}/alldata
  - Réponse 200: {
      "id": integer,
      "name": string,
      "polygon_points": object|null,
      "etages": [ {
        "id": integer,
        "name": string,
        "carte"?: { id, chemin, etage_id, site_id, center_lat, center_lng, zoom },
        "baes": [ {
          "id": integer,
          "name": string,
          "position"?: object,
          "erreurs": [ { "id": integer, "erreur": integer, "temperature"?: number, "vibration"?: boolean, "timestamp"?: string, "is_solved": boolean, "is_ignored": boolean } ]
        } ]
      } ]
    } | 404
- GET /general/version
  - Réponse 200: { "version": string }


## Rôles (/roles)
- POST /roles/
  - Requête: { "name": string }
  - Réponse 201: { "id": integer, "name": string }
- GET /roles/
  - Réponse 200: [ { "id": integer, "name": string } ]
- DELETE /roles/{id}
  - Réponse 200: { "message": string } | 404


## Configuration (/config)
- GET /config/
  - Réponse 200: [ { "id": integer, "key": string, "value": string|number|boolean|object|null } ] ou { ... état global ... }
- POST /config/
  - Requête: { "key": string, "value": any JSON }
  - Réponse 201: { "id": integer, "key": string, "value": any JSON }
- PUT /config/{config_id}
  - Requête: { "key"?: string, "value"?: any JSON }
  - Réponse 200: { ... } | 404
- GET /config/key/{key}
  - Réponse 200: { "id": integer, "key": string, "value": any JSON } | 404


Références
- Swagger UI: /swagger/
- Spécification JSON: /apispec.json (les routes legacy /erreurs sont exclues de la spec pour éviter les doublons)
