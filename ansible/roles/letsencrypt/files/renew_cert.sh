#!/usr/bin/env bash
set -e

DOMAIN="$1"
if [ -z "$DOMAIN" ]
then
    echo "Usage: ./renew_cert.sh domain"
    exit 1
fi

ACMEPY=/opt/ssl/acme_tiny.py
CERTDIR=/etc/nginx/ssl/$DOMAIN
CHALLENGEDIR=/var/www/challenges/

[ -f $ACMEPY ] || { echo -e "acme-tiny not found"; exit 1; }
[ -f "$CERTDIR"/account.key ] || { echo -e "account key missing. Create one with create_csr.sh "; exit 1; }
[ -f "$CERTDIR"/domain.key ] || { echo -e "domain key missing. Create in with create_csr.sh "; exit 1; }
[ -f "$CERTDIR"/domain.csr ] || { echo -e "domain signing request missing. Create in with create_csr.sh "; exit 1; }

if [ -f "$CERTDIR"/signed.crt ]
then
    cp "$CERTDIR"/signed.crt "$CERTDIR/$(date -I)signed.crt"
fi
if [ -f "$CERTDIR"/chained.pem ]
then
    cp "$CERTDIR"/chained.pem "$CERTDIR/$(date -I)chained.pem"
fi
python3 $ACMEPY --account-key \
        "$CERTDIR"/account.key \
        --csr "$CERTDIR"/domain.csr \
        --acme-dir $CHALLENGEDIR > "$CERTDIR"/signed.crt
curl https://letsencrypt.org/certs/lets-encrypt-x3-cross-signed.pem > \
     "$CERTDIR"/letsencrypt_intermediate.pem
cat "$CERTDIR"/signed.crt \
    "$CERTDIR"/letsencrypt_intermediate.pem > \
    "$CERTDIR"/chained.pem

# Make sure this command can be exed by non-root user
sudo /usr/sbin/nginx -s reload


#To revoke a certificate you have to use https://github.com/diafygi/letsencrypt-nosudo#how-to-use-the-revocation-script
