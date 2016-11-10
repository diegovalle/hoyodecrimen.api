#!/bin/bash
set -e

if [ -z "$1" ]
then
    echo "Usage: ./create_csr.sh sitename"
    exit 1
fi
SITENAME="$1"
DIRNAME="/etc/nginx/ssl/$SITENAME"
ACMEPY=/opt/ssl/acme_tiny.py

[ -f $ACMEPY ] || echo -e "acme-tiny not found"; exit 1
[ -f "$DIRNAME"/account.key ] && echo -e "account key already exists"; exit 1
[ -f "$DIRNAME"/domain.key ] && echo -e "domain key already exists"; exit 1

mkdir -p "$DIRNAME"
cd "$DIRNAME"
openssl genrsa  2048 > account.key
openssl genrsa  2048 > domain.key

# for a single domain
openssl req -new -sha256 -key domain.key -subj "/CN=$SITENAME" > domain.csr


#openssl req -new -sha256 -key domain.key -subj "/C=US/ST=CA/O=ilsevalle.com/CN=ilsevalle.com" -reqexts SAN  -config <(cat /etc/ssl/openssl.cnf <(printf "[SAN]\nsubjectAltName=DNS:ilsevalle.com\,DNS:www.ilsevalle.com,DNS:personal.ilsevalle.com")) > domain.csr
# openssl req -new -sha256 -key domain.key -subj "/C=US/ST=CA/O=diegovalle.net/CN=diegovalle.net" -reqexts SAN  -config <(cat /etc/ssl/openssl.cnf <(printf "[SAN]\nsubjectAltName=DNS:diegovalle.net,DNS:blog.diegovalle.net,DNS:data.diegovalle.net,DNS:crimenmexico.diegovalle.net,DNS:bcrimenmexico.diegovalle.net,DNS:calendar.diegovalle.net,DNS:docs.diegovalle.net,DNS:mail.diegovalle.net,DNS:sites.diegovalle.net")) > domain.csr

# for multiple domains (use this one if you want both www.yoursite.com
# and yoursite.com)
#openssl req -new -sha256 -key domain.key -subj "/C=US/ST=CA/O=$SITENAME/CN=$SITENAME" \
#        -reqexts SAN \
#        -config <(cat /etc/ssl/openssl.cnf \
#                      <(printf "[SAN]\nsubjectAltName=DNS:$SITENAME\,DNS:www.$SITENAME")) > \
#        domain.csr
