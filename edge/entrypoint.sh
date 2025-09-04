#!/bin/sh
set -e

# Configurable via environment
FRONT="${FRONT_DOMAIN:-frontbaes.0shura.fr}"
API="${API_DOMAIN:-apibaes.0shura.fr}"
ACME_EMAIL="${ACME_EMAIL:-mathisbatailler30@gmail.com}"
ACME_STAGING="${ACME_STAGING:-false}" # set to true to use Let's Encrypt staging
OVH_CRED_SRC=/run/secrets/ovh.ini
OVH_CRED_DST=/etc/letsencrypt/ovh.ini

log() { echo "[edge] $1"; }

# Prepare OVH credentials with safe permissions (certbot requires 0600)
prepare_creds() {
  if [ -f "$OVH_CRED_SRC" ]; then
    mkdir -p /etc/letsencrypt
    cp "$OVH_CRED_SRC" "$OVH_CRED_DST" || true
    chmod 600 "$OVH_CRED_DST" || true
  else
    log "OVH credentials not found at $OVH_CRED_SRC; refusing to proceed."
    exit 1
  fi
}

# Validate OVH credentials content (keys non-empty, not placeholders)
validate_creds() {
  REQUIRED_KEYS="dns_ovh_endpoint dns_ovh_application_key dns_ovh_application_secret dns_ovh_consumer_key"
  for k in $REQUIRED_KEYS; do
    LINE=$(grep -E "^$k\s*=\s*" "$OVH_CRED_DST" 2>/dev/null | head -n1)
    VALUE=$(echo "$LINE" | cut -d= -f2- | tr -d ' \t\r')
    if [ -z "$VALUE" ]; then
      log "Invalid or missing OVH credential: $k in $OVH_CRED_DST"
      exit 1
    fi
    # Reject obvious placeholders like <APP_KEY> or values containing angle brackets
    if echo "$VALUE" | grep -q "[<>]"; then
      log "OVH credential $k appears to be a placeholder in $OVH_CRED_DST; please set a real value."
      exit 1
    fi
  done
}

# Update nginx confs with domains from env to avoid mismatch
patch_nginx_confs() {
  sed -i "s/frontbaes.0shura.fr/${FRONT}/g" /etc/nginx/conf.d/front.conf || true
  sed -i "s/apibaes.0shura.fr/${API}/g" /etc/nginx/conf.d/api.conf || true
}

# Build common certbot flags
certbot_flags() {
  FLAGS="--dns-ovh --dns-ovh-credentials ${OVH_CRED_DST} --dns-ovh-propagation-seconds 900 --agree-tos --email ${ACME_EMAIL} --non-interactive"
  if [ "$ACME_STAGING" = "true" ]; then
    FLAGS="$FLAGS --staging"
  fi
  echo "$FLAGS"
}

# Try to obtain a real LE certificate for a domain
issue_cert() {
  DOMAIN="$1"
  if [ ! -f "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" ] || [ ! -f "/etc/letsencrypt/live/${DOMAIN}/privkey.pem" ]; then
    log "Attempting Let's Encrypt issuance for ${DOMAIN} (staging=$ACME_STAGING, email=${ACME_EMAIL})"
    if certbot certonly $(certbot_flags) -d "${DOMAIN}"; then
      log "Certificate obtained for ${DOMAIN}. Reloading nginx."
      nginx -s reload || true
    else
      log "Certbot failed for ${DOMAIN}."
    fi
  fi
}

# Verify that certificate files exist for a domain
have_cert() {
  DOMAIN="$1"
  [ -f "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" ] && [ -f "/etc/letsencrypt/live/${DOMAIN}/privkey.pem" ]
}

prepare_creds
validate_creds
patch_nginx_confs

# Obtain certificates before starting nginx (no self-signed fallback)
issue_cert "${FRONT}"
issue_cert "${API}"

if ! have_cert "${FRONT}" || ! have_cert "${API}"; then
  log "Failed to obtain required Let's Encrypt certificates. Refusing to start Nginx without valid ACME certs."
  exit 1
fi

# Renewal and retry loop in the background
(
  while :; do
    certbot renew \
      --dns-ovh-credentials "${OVH_CRED_DST}" \
      --quiet \
      --deploy-hook "nginx -s reload" || true
    sleep 12h
  done
) &

# Start nginx in the foreground
nginx -g 'daemon off;'
