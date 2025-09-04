FROM nginx:alpine

# Install Certbot and OVH DNS plugin from Alpine packages (PEP 668 compliant)
# No self-signed fallback: openssl not required
RUN apk add --no-cache certbot certbot-dns-ovh bash coreutils

# TLS raisonnable par défaut
RUN mkdir -p /etc/nginx/conf.d
COPY nginx/conf.d/ /etc/nginx/conf.d/

COPY ovh.ini /etc/letsencrypt/ovh.ini
RUN chmod 600 /etc/letsencrypt/ovh.ini

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh



EXPOSE 443
CMD ["/entrypoint.sh"]
