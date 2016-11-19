#!/bin/bash
if [[ -z $1 ]]; then
  echo "Usage: $0 domain_name /path/to/certificates/"
fi
if [[ -z $2 ]]; then
  echo "Usage: $0 domain_name /path/to/certificates/"
fi
echo "$1_domain_csr: |"
cat "$2domain.csr" | sed  's/^/   /'
echo "$1_domain_key: |"
cat "$2domain.key" | sed  's/^/   /'
echo "$1_account_key: |"
cat "$2account.key" | sed  's/^/   /'
echo "$1_chained_pem: |"
cat "$2chained.pem" | sed  's/^/   /'
