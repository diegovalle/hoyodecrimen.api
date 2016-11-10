#!/usr/bin/env bash

MONTHS=1

check_cert() {
    CERT_EXPIRATION=$(openssl x509 -enddate -noout -in "$1" | sed s/notAfter=//)

    CERT_EXPIRATION_S=$(date --date="$CERT_EXPIRATION" +"%s")
    TODAY_PLUS_MONTH_S=$(date --date="now + $MONTHS month" +"%s")

    echo "$CERT_EXPIRATION"
    echo "$TODAY_PLUS_MONTH_S"

    if [ "$TODAY_PLUS_MONTH_S" -gt "$CERT_EXPIRATION_S" ]; then
        exit 1
    fi
}

export -f check_cert
find . -iname '*.pem' -exec bash -c 'check_cert {}' \;
