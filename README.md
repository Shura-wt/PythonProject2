# Windows Server

Renommer DockerfileWindows en Dockerfile

```
docker build -t flutter-web-iis .

docker run -d -p 8080:80 --name mon-site-flutter flutter-web-iis
```

# Nginx

```
docker build -t baes_front .

docker run -d -p 80:80 --name baes_front baes_front
```

# Windows Server

Renommer DockerfileWindows en Dockerfile

```
docker build -t flutter-web-iis .

docker run -d -p 8080:80 --name mon-site-flutter flutter-web-iis
```

# Nginx

```
docker build -t baes_front .

docker run -d -p 80:80 --name baes_front baes_front
```

---

# Note: docker-compose v1.29.2 compatibility on Azure

Si vous voyez l'erreur suivante lors de `docker compose up` / `docker-compose up` sur Azure:

```
KeyError: 'ContainerConfig'
```

C'est dû à une incompatibilité connue entre docker-compose v1.29.2 et les versions récentes de Docker Engine/BuildKit. Pour contourner le problème dans ce projet:

- Les scripts d'assistance fournis (compose.sh / compose.ps1) détectent automatiquement l'utilisation de docker-compose v1 et définissent DOCKER_API_VERSION=1.41 avant d'exécuter la commande, ce qui évite l'erreur.
- Optionnel: un fichier `.env` à la racine peut aussi définir `DOCKER_API_VERSION=1.41`, mais ce n'est pas requis si vous lancez via les scripts.

Alternatives:
- Mettre à jour vers Docker Compose v2 (`docker compose` récent) qui ne présente pas ce bug.
- Exporter manuellement la variable d'environnement avant d'exécuter compose: `export DOCKER_API_VERSION=1.41` (ou PowerShell `$env:DOCKER_API_VERSION='1.41'`).

Après la mise à jour, relancez:

```
./compose.sh down -v
./compose.sh up -d --build
```


## How to run with Docker Compose (auto-detect v1/v2)

Si vous voyez l'erreur suivante en lançant `docker compose up -d --build` sur votre hôte (ex: Azure):

```
unknown shorthand flag: 'd' in -d
```

Cela signifie que la sous‑commande `docker compose` (plugin Compose v2) n'est pas disponible et que la commande `docker` interprète les options pour un autre sous‑commande. Pour éviter toute confusion entre Compose v2 (`docker compose`) et l'ancien Compose v1 (`docker-compose`), ce dépôt fournit des scripts d'assistance qui détectent automatiquement la version disponible et relaient les arguments.

- Linux/macOS:
  - Rendre le script exécutable une fois: `chmod +x ./compose.sh`
  - Utiliser: `./compose.sh up -d --build` puis `./compose.sh ps`

- Windows (PowerShell):
  - Utiliser: `.\compose.ps1 up -d --build` puis `.\compose.ps1 ps`

Note sur docker-compose v1: si votre système utilise encore `docker-compose` v1, ce projet inclut un fichier `.env` avec `DOCKER_API_VERSION=1.41` pour contourner le bug `KeyError: 'ContainerConfig'` avec des Engines récents. Vous pouvez garder ce fichier ou migrer vers Compose v2.


## Certificats Let's Encrypt (ACME) via OVH

Le conteneur edge intègre Certbot et le plugin DNS OVH. Il obtient automatiquement des certificats valides Let's Encrypt pour:
- frontbaes.isymap.com
- apibaes.isymap.com

Pré-requis:
- Les DNS des domaines ci-dessus doivent pointer vers l'IP publique du serveur (A/AAAA).
- Un compte OVH avec accès à la zone DNS et des identifiants API valides (application key/secret, consumer key) autorisés sur la zone.
- Un fichier secrets/ovh.ini sur l’hôte, monté en lecture seule dans le conteneur (déjà configuré dans docker-compose):
  
  Exemple de contenu (ne pas commiter ces secrets):
  
  dns_ovh_endpoint = ovh-eu
  dns_ovh_application_key = <APP_KEY>
  dns_ovh_application_secret = <APP_SECRET>
  dns_ovh_consumer_key = <CONSUMER_KEY>

Configuration (docker-compose, service edge):
- FRONT_DOMAIN et API_DOMAIN: domaines cibles (par défaut frontbaes.isymap.com et apibaes.isymap.com)
- ACME_EMAIL: email de contact ACME (facultatif; défaut: postmaster@<API_DOMAIN>)
- ACME_STAGING=true: activer l’environnement de test Let’s Encrypt pour éviter les limites de rate (à utiliser pour valider la configuration initiale)

Démarrage:
- Linux: ./compose.sh up -d --build edge
- Windows (PowerShell): .\compose.ps1 up -d --build edge

Le conteneur edge:
- N'UTILISE JAMAIS de certificat auto-signé. Il tente d'obtenir un certificat Let's Encrypt valide AVANT de démarrer Nginx. En cas d'échec, le conteneur s'arrête.
- À la réussite, Nginx démarre et utilise le certificat valide.
- Un cycle de renouvellement automatique (certbot renew) tourne en arrière-plan et recharge Nginx après renouvellement.

Changer les domaines:
- Définissez simplement les variables d’environnement FRONT_DOMAIN et API_DOMAIN dans docker-compose.yml.
- L'entrypoint met automatiquement à jour les fichiers Nginx au démarrage pour refléter ces domaines (pas besoin d'éditer les confs).

Passer de staging à production:
- D’abord, tester avec ACME_STAGING=true et vérifier les logs.
- Ensuite, retirer ACME_STAGING et redéployer edge. Certbot obtiendra un certificat de production.

### Dépannage (OVH 403 / zone introuvable)
Si vous voyez dans les logs edge une erreur type:
- "Error determining zone identifier ... 403 Client Error: Forbidden for url: https://eu.api.ovh.com/1.0/domain/zone/."

Vérifiez:
- secrets/ovh.ini monté en lecture seule dans edge (déjà défini dans docker-compose).
- Contenu ovh.ini exact et non vide:
  - dns_ovh_endpoint = ovh-eu
  - dns_ovh_application_key = <APP_KEY>
  - dns_ovh_application_secret = <APP_SECRET>
  - dns_ovh_consumer_key = <CONSUMER_KEY>
- Droits du fichier dans le conteneur: l’entrypoint applique chmod 600 automatiquement.
- Que l’APP_KEY/SECRET/CONSUMER_KEY ont bien les droits sur la zone DNS des domaines FRONT_DOMAIN et API_DOMAIN dans OVH (API "domain/zone").
- Que les domaines frontbaes.isymap.com / apibaes.isymap.com existent dans votre compte OVH et pointent vers l’IP du serveur.
- ACME_EMAIL est correctement défini (ex: mathisbatailler30@gmail.com) pour recevoir d’éventuelles notifications.

L’entrypoint vérifie désormais la présence et la validité de ovh.ini et s’arrête immédiatement si des clés manquent, pour éviter des boucles d’échec.

## Vérifier la connexion HTTPS (frontbaes.isymap.com)

Après déploiement, suivez ces étapes pour confirmer que la connexion fonctionne:

1) Rebuilder et redémarrer uniquement le reverse-proxy edge (après les changements Nginx):
   - Linux: ./compose.sh up -d --build edge
   - Windows (PowerShell): .\compose.ps1 up -d --build edge

2) Vérifier que le port 443 est bien publié et que le conteneur est Up:
   - ./compose.sh ps

3) Observer les logs de edge (Certbot & Nginx):
   - ./compose.sh logs -f edge
   Vous devriez voir "Attempting Let's Encrypt issuance for frontbaes.isymap.com" puis un reload nginx si l'émission réussit.

4) Inspecter la présence des certificats dans le conteneur:
   - docker exec -it edge-test sh -c "ls -l /etc/letsencrypt/live/frontbaes.isymap.com /etc/letsencrypt/live/apibaes.isymap.com"

5) Tester depuis le serveur (Azure) la réponse HTTPS et le certificat:
   - curl -vkI https://frontbaes.isymap.com/
   - openssl s_client -connect frontbaes.isymap.com:443 -servername frontbaes.isymap.com -showcerts | openssl x509 -noout -subject -issuer -dates

6) Vérifications DNS / Réseau:
   - Assurez-vous que frontbaes.isymap.com et apibaes.isymap.com pointent (A/AAAA) vers l'IP publique du serveur hébergeant edge.
   - Ouvrez le port 443 en entrée sur le pare-feu/NSG du serveur.

Notes:
- Le conteneur edge refuse de démarrer sans certificats Let's Encrypt valides. Il n'y a aucun fallback auto-signé.
- Les fichiers de configuration Nginx ont été alignés sur les domaines .com: frontbaes.isymap.com et apibaes.isymap.com.


### Secrets OVH (création du fichier)

- Copiez le fichier d’exemple vers le fichier réel attendu par le conteneur:
  - Windows/PowerShell: copy .\secrets\ovh.example.ini .\secrets\ovh.ini
  - Linux/macOS: cp ./secrets/ovh.example.ini ./secrets/ovh.ini
- Remplissez les valeurs réelles pour dns_ovh_application_key, dns_ovh_application_secret et dns_ovh_consumer_key. L’endpoint recommandé pour l’Europe est: dns_ovh_endpoint = ovh-eu
- Ne commitez jamais secrets/ovh.ini: ce fichier est ignoré par git (.gitignore) et doit rester uniquement sur votre hôte/serveur.
- Le fichier est monté en lecture seule dans le conteneur (voir docker-compose.yml), et l’entrypoint applique automatiquement les permissions requises (chmod 600) et vérifie que les valeurs ne sont pas vides ni des placeholders.

#### Automatisation via GitHub Actions

Si vous utilisez le déploiement CI/CD fourni (voir section "CI/CD: Déploiement automatique"), le fichier `secrets/ovh.ini` est généré automatiquement sur le serveur à chaque déploiement à partir des Secrets du dépôt GitHub:
- `DNS_OVH_APPLICATION_KEY`
- `DNS_OVH_APPLICATION_SECRET`
- `DNS_OVH_CONSUMER_KEY`

Comportement:
- Le workflow crée (ou écrase) `secrets/ovh.ini` dans `${{ secrets.DEPLOY_WORKDIR }}` avant d'exécuter `scripts/deploy.sh`.
- Les valeurs ne sont jamais commitées dans le dépôt.
- Assurez-vous d’avoir défini ces Secrets dans GitHub > Settings > Secrets and variables > Actions.
- Si vous n’utilisez pas le workflow CI (exécution manuelle locale), vous devez créer `secrets/ovh.ini` vous-même sur la machine qui exécute Docker.


---

## CI/CD: Déploiement automatique via GitHub Actions (SSH)

Ce dépôt inclut un workflow GitHub Actions qui déploie automatiquement sur votre serveur par SSH, nettoie les anciens conteneurs/volumes et relance une version propre via `scripts/deploy.sh`.

Déclencheurs:
- Push sur la branche `master`
- Lancement manuel (workflow_dispatch)

Pré-requis côté serveur:
- Docker installé (Compose v2 via `docker compose`, ou `docker-compose` v1).
- Le dépôt cloné une première fois dans un dossier fixe (ex: `/opt/baes_docker_shura` sous Linux, ou `C:\\baes_docker_shura` sous Windows).
- L’utilisateur SSH a le droit d’exécuter Docker (ajouté au groupe `docker` sous Linux, ou utilisez `sudo` si nécessaire).

Secrets GitHub à configurer (Settings > Secrets and variables > Actions):
- `DEPLOY_HOST`: IP ou DNS du serveur (ex: `90.113.56.213`).
- `DEPLOY_USER`: utilisateur SSH (ex: `userssh`).
- `DEPLOY_SSH_KEY`: contenu de la clé privée (ex: contenu du fichier `sshMathis.pem`).
- `DEPLOY_WORKDIR`: chemin absolu du dépôt déjà cloné sur le serveur (ex: `/opt/baes_docker_shura`).
- `DEPLOY_PORT` (optionnel): port SSH (défaut: 22).

Ce que fait le workflow (`.github/workflows/deploy.yml`):
1. Se connecte en SSH au serveur avec la clé privée.
2. `cd` vers `DEPLOY_WORKDIR` puis récupère la dernière version du code: `git fetch --all --prune && git reset --hard origin/master`. 
3. Rend exécutable `scripts/deploy.sh`.
4. Exécute `scripts/deploy.sh` qui effectue:
   - `docker compose down -v` (ou `docker-compose down -v`) pour arrêter et supprimer conteneurs et volumes du projet.
   - Nettoyage additionnel des conteneurs/volumes étiquetés du projet, prune réseaux/images.
   - `compose build --pull` pour reconstruire en tirant les dernières bases.
   - `compose up -d` pour redémarrer proprement la stack.

Étapes d’initialisation (une seule fois):
- Cloner le dépôt sur le serveur à l’emplacement choisi (ex):
  - Linux: `git clone <URL_GITHUB> /opt/baes_docker_shura`
  - Windows: `git clone <URL_GITHUB> C:\\baes_docker_shura`
- Vérifier l’origin: `git -C <WORKDIR> remote -v`
- Tester un déploiement manuel sur le serveur: `bash scripts/deploy.sh` (Linux) ou via WSL; sous Windows sans WSL, exécutez la commande depuis un shell compatible (Git Bash) ou adaptez un script PowerShell équivalent.

Sécurité:
- Ne commitez jamais de mots de passe ni de clés privées. Utilisez exclusivement les Secrets GitHub.
- Vous pouvez restreindre l’accès SSH de la clé à l’IP de GitHub Actions si nécessaire.


## Droits Docker/Compose pour l'utilisateur `userssh`

Sur un serveur Ubuntu/Debian typique:

1) Installer Docker (si absent) et démarrer le service:
   - sudo apt-get update
   - sudo apt-get install -y docker.io
   - sudo systemctl enable --now docker

2) Ajouter `userssh` au groupe docker pour exécuter Docker sans sudo:
   - sudo groupadd docker 2>/dev/null || true
   - sudo usermod -aG docker userssh
   - newgrp docker    # ou déconnectez-vous/reconnectez-vous pour appliquer le groupe

3) Vérifier Docker et un conteneur de test:
   - docker --version
   - docker run --rm hello-world

4) Vérifier Docker Compose:
   - docker compose version   # Compose v2 (recommandé)
   - Si non présent, vous pouvez installer docker-compose v1 : `sudo apt-get install -y docker-compose`
     (le script `scripts/deploy.sh` gère automatiquement `docker compose` v2 ou `docker-compose` v1)

Important:
- `DEPLOY_WORKDIR` doit pointer vers la racine du dépôt cloné (par ex. `/home/userssh/PythonProject2`).
  Si vous avez seulement `/home/userssh`, clonez le dépôt dedans et utilisez le chemin complet du dossier du dépôt.


### Note importante: ovh.ini et le service edge

- Il n'est ni utile ni recommandé de garder un fichier `ovh.ini` dans le dossier `edge/` ni de le copier dans l'image via le Dockerfile.
- Le Dockerfile du service edge ne copie plus `ovh.ini`. Les identifiants OVH sont fournis au runtime via le montage `./secrets/ovh.ini` -> `/run/secrets/ovh.ini` et sont sécurisés par l'entrypoint (chmod 600).
- N'ajoutez jamais de secrets sous `edge/`. Le fichier `edge/ovh.ini` est ignoré par Git et ne doit contenir aucune donnée sensible.
- Pour un usage local, partez de `secrets/ovh.example.ini` et créez un `secrets/ovh.ini` non commité. En CI/CD, le fichier `secrets/ovh.ini` est généré automatiquement à chaque déploiement depuis les Secrets GitHub.
- Si des clés OVH ont été commitées par le passé, révoquez/regénérez-les dans votre compte OVH.
