#!/bin/bash

#######################################
# Certificate request through Certbot #
#######################################

local rsa_key_size=4096
local data_path="./data/certbot"

##############################
# Requesting base parameters #
##############################

print "Copying certificate files..."
if [ "$(file_is_present $data_path/conf/options-ssl-nginx.conf)" = "0" ] ||
   [ "$(file_is_present "$data_path/conf/ssl-dhparams.pem" )" = "0" ]; then
    curl \
    -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf \
    >"$data_path/conf/options-ssl-nginx.conf"
    curl \
    -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem \
    >"$data_path/conf/ssl-dhparams.pem"
fi

###############################
# Creating dummy certificates #
###############################

local cert_path="/etc/letsencrypt/live/$DOMAIN_NAME"
mkdir -p "$data_path/conf/live/$DOMAIN_NAME"

# self-signed certificate for the porxy to start
print "Creating dummy certificate for $DOMAIN_NAME..."
docker compose -f "docker-compose.yaml" run --rm --entrypoint "\
  openssl req -x509 -nodes -newkey rsa:$rsa_key_size -days 10\
    -keyout '$cert_path/privkey.pem' \
    -out '$cert_path/fullchain.pem' \
    -subj '/CN=localhost'" ca-auth

print "Starting proxy ..."
docker compose  -f "docker-compose.yaml" up --force-recreate -d proxy

################################
# Creating actual certificates #
################################

# delete dummy certificates
print "Deleting dummy certificate for $DOMAIN_NAME..."
docker compose  -f "docker-compose.yaml" run --rm --entrypoint "\
  rm -Rf /etc/letsencrypt/live/$DOMAIN_NAME && \
  rm -Rf /etc/letsencrypt/archive/$DOMAIN_NAME && \
  rm -Rf /etc/letsencrypt/renewal/$DOMAIN_NAME.conf" ca-auth

# create a request for a cetificate for the current domain
print "Requesting Let's Encrypt certificate for $DOMAIN_NAME ..."
docker compose -f "docker-compose.yaml" run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
    --domain $DOMAIN_NAME \
    --rsa-key-size $rsa_key_size \
    --non-interactive \
    --agree-tos \
    --force-renewal" ca-auth

# reload the proxy for the certificates to take effect
docker compose -f "docker-compose.yaml" exec proxy nginx -s reload
