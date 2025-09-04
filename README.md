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


---

## Utilisation locale des identifiants OVH (sans committer de secrets)

Deux options équivalentes pour faire tourner le service edge en local avec Certbot DNS-OVH:

- Option A: Fichier secrets/ovh.ini (non commité)
  - Copiez secrets/ovh.example.ini vers secrets/ovh.ini
  - Renseignez des valeurs réelles pour:
    - dns_ovh_application_key
    - dns_ovh_application_secret
    - dns_ovh_consumer_key
  - L’entrypoint normalise le fichier (LF, espaces) et vérifie que les valeurs ne sont pas des placeholders.

- Option B: Fichier .env (non commité)
  - Copiez .env.example vers .env
  - Renseignez:
    - DNS_OVH_ENDPOINT=ovh-eu (par défaut)
    - DNS_OVH_APPLICATION_KEY=...
    - DNS_OVH_APPLICATION_SECRET=...
    - DNS_OVH_CONSUMER_KEY=...
  - Au démarrage, si secrets/ovh.ini est manquant ou contient des placeholders, l’entrypoint edge auto‑remplira /etc/letsencrypt/ovh.ini avec ces variables, puis validera le contenu.

Notes importantes:
- Ne laissez pas de valeurs placeholders (<APP_KEY>, etc.), sinon le conteneur edge refusera de démarrer (pas de certificat autosigné).
- .env est ignoré par Git (.gitignore) et ne doit jamais être poussé.
- En CI/CD, le fichier secrets/ovh.ini est régénéré à chaque déploiement à partir des GitHub Secrets; les variables .env locales ne sont pas utilisées côté serveur.


---

### Note: Démarrage d'edge indépendant de l'API pour l'émission TLS

- Afin de ne pas bloquer l’émission des certificats Let’s Encrypt en cas de panne de la base de données (ex: manque de RAM pour SQL Server), le service `edge` ne dépend plus du service `api` dans `docker-compose.yml`.
- `edge` peut ainsi démarrer et servir le front ainsi que gérer l’ACME (DNS-01 via OVH) même si `api`/`mssql` sont momentanément indisponibles.
- Les proxypass vers l’API répondront en erreur tant que l’API n’est pas démarrée, mais la couche TLS (certificats valides) sera opérationnelle, ce qui est requis par la CI.
