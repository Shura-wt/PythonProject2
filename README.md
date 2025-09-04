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


---

## Pourquoi MSSQL marche en local mais pas en CI/serveur ?

Sur votre serveur, la VM dispose d’environ 2 Gio de RAM et 0 swap. SQL Server (Linux, image mcr.microsoft.com/mssql/server:2017-latest) a besoin d’au moins ~2 Gio de RAM et/ou d’un swap suffisant pour démarrer correctement. Sans cela, le processus `sqlservr` peut avorter (SIGABRT) au démarrage, ce que vous observez dans les logs CI. En local, votre machine a plus de mémoire/swap, donc le conteneur devient healthy.

Signes typiques dans les logs:
- "Waiting for SQL Server to start..." qui boucle
- Crash avec SIGABRT et génération d’un core dump sous /var/opt/mssql/log

Pré-requis côté hôte pour MSSQL:
- CPU avec AVX: `lscpu | grep -i avx` doit renvoyer AVX/AVX2.
- RAM disponible ≥ 2 Gio (plus confortable si possible).
- Swap activé (recommandé si RAM faible) pour amortir le pic mémoire au démarrage.

### Créer un fichier de swap (Ubuntu/Debian)
Exécuter en root sur le serveur:

```
# Créer 2 Gio de swap (méthode rapide si fallocate dispo)
fallocate -l 2G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=2048
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# Rendre persistant au redémarrage
printf '/swapfile none swap sw 0 0\n' | tee -a /etc/fstab

# Vérifications
free -h
swapon --show
```

Après ajout du swap (ou augmentation de la RAM), relancez le déploiement. Le service `mssql` devrait passer healthy, puis `api` démarrera.

Note: Pour ne pas bloquer l’émission TLS pendant vos réglages MSSQL, `edge` ne dépend plus de `api`. Les certificats sont donc obtenus même si la base n’est pas encore opérationnelle.
