#Ansible setup for hoyodecrimen.com

The structure of the secrets.yml file:

```
# mkpasswd --method=SHA-512
ROOT_PASSWORD:
DEPLOY_PASSWORD:

DB_PASSWORD: 
SENTRY_DSN: 

# deadmansnitch url to check the certs are renewed
health_check_renew_hoyodecrimen_com:

# letsencrypt certificates
hoyodecrimen_com_domain_csr:
hoyodecrimen_com_domain_key:
hoyodecrimen_com_account_key:
hoyodecrimen_com_chained_pem:
```
