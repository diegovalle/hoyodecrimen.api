# cloudflare ns: 
# emma.ns.cloudflare.com
# tony.ns.cloudflare.com

server {
    listen [::]:80;
    listen 80;
    server_name hoyodecrimen.com;

    #Specify a charset
    charset utf-8;
    location / {
        return 301 https://hoyodecrimen.com$request_uri;
    }
    include snippets/acme-challenge.conf;
}

server {
    listen [::]:80;
    listen 80;
    server_name www.hoyodecrimen.com;

    #Specify a charset
    charset utf-8;
    location / {
        return 301 https://hoyodecrimen.com$request_uri;
    }
    include snippets/acme-challenge.conf;
}


server {
    listen [::]:443 ssl http2;  # for Linux
    listen 443 ssl http2;  # for Linux
    
    #Specify a charset
    charset utf-8;

    server_name hoyodecrimen.com;

    #ssl on;
    ssl_certificate /etc/nginx/ssl/hoyodecrimen.com/chained.pem;
    ssl_certificate_key /etc/nginx/ssl/hoyodecrimen.com/domain.key;
    ## verify chain of trust of OCSP response using Root CA and Intermediate certs
    ssl_trusted_certificate /etc/nginx/ssl/hoyodecrimen.com/chained.pem;

    include h5bp/directive-only/ssl.conf;
    include h5bp/directive-only/ssl-stapling.conf;
    add_header Strict-Transport-Security "max-age=31536000";

    include snippets/acme-challenge.conf;
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }

    # Block referral spam for Google Analytics
    if ($bad_referer) {
        return 444;
    }

    # Include the basic h5bp config set
    #include h5bp/basic.conf;
    include h5bp/directive-only/x-ua-compatible.conf;
    #include h5bp/location/expires.conf;
    #include h5bp/location/cross-domain-fonts.conf;
    #include h5bp/location/protect-system-files.conf;
    #include h5bp/directive-only/extra-security.conf;
    location = /favicon.ico {
       alias /var/www/hoyodecrimen.com/hoyodecrimen.api/wsgi/static/images/favicon.ico;
       expires 1M;
       access_log off;
    }
    location = /google055ef027e7764e4d.html {
       alias /var/www/hoyodecrimen.com/hoyodecrimen.api/wsgi/static/google055ef027e7764e4d.html;
       expires 1M;
       access_log off;
    }
    location = /mu-01188fe9-0b813050-b0f51076-c96f41fb.txt {
       alias /var/www/hoyodecrimen.com/hoyodecrimen.api/wsgi/static/mu-01188fe9-0b813050-b0f51076-c96f41fb.txt;
       expires 1M;
       access_log off;
    }
    location = /robots.txt {
       alias /var/www/hoyodecrimen.com/hoyodecrimen.api/wsgi/static/robots.txt;
    }
    location = /sitemap.xml {
       alias /var/www/hoyodecrimen.com/hoyodecrimen.api/wsgi/static/sitemap.xml;
    }
    # location ~ ^/(apple-touch-icon|browserconfig|favicon|mstile|manifest)(.*)\.(png|xml|ico|json)$ {
    #    alias /var/www/hoyodecrimen.com/hoyodecrimen.api/wsgi/static/images/;
    #    expires 1M;
    #    access_log off;
    # }
    # favicon stuff
    location = /apple-touch-icon.png {
       alias /var/www/hoyodecrimen.com/hoyodecrimen.api/wsgi/static/images/apple-touch-icon.png;
    }
    location ^~ /apple-touch-icon {
       root /var/www/hoyodecrimen.com/hoyodecrimen.api/wsgi/static/images/;
       expires 1M;
       access_log off;
    }
    location ^~ /favicon {
       root /var/www/hoyodecrimen.com/hoyodecrimen.api/wsgi/static/images/;
       expires 1M;
       access_log off;
    }
    location ^~ /browserconfig {
       root /var/www/hoyodecrimen.com/hoyodecrimen.api/wsgi/static/images/;
       expires 1M;
       access_log off;
    }
    location ^~ /mstile {
        root /var/www/hoyodecrimen.com/hoyodecrimen.api/wsgi/static/images/;
       expires 1M;
       access_log off;
    }
    location ^~ /manifest {
        root /var/www/hoyodecrimen.com/hoyodecrimen.api/wsgi/static/images/;
        expires 1M;
        access_log off;
    }
    
    location ^~ /css {
       root /var/www/hoyodecrimen.com/hoyodecrimen.api/wsgi/static;
       expires 1M;
       access_log off;
    }
    location ^~ /js {
       root /var/www/hoyodecrimen.com/hoyodecrimen.api/wsgi/static;
       expires 1M;
       access_log off;
    }
    location ^~ /static/css {
       root /var/www/hoyodecrimen.com/hoyodecrimen.api/wsgi/;
       expires 1M;
       access_log off;
    }
    location ^~ /static/js {
       root /var/www/hoyodecrimen.com/hoyodecrimen.api/wsgi/;
       expires 1M;
       access_log off;
    }
    location ^~ /images {
       root /var/www/hoyodecrimen.com/hoyodecrimen.api/wsgi/static;
       expires 1M;
       access_log off;
    }
    location ^~ /fonts {
       root /var/www/hoyodecrimen.com/hoyodecrimen.api/wsgi/static;
       expires 1M;
       access_log off;
    }    
    location ^~ /font {
       root /var/www/hoyodecrimen.com/hoyodecrimen.api/wsgi/static;
       expires 1M;
       access_log off;
    }
    location = /api/v1/cuadrantes/geojson {
       alias /var/www/hoyodecrimen.com/hoyodecrimen.api/wsgi/static/geojson/cuadrantes.json;
       default_type application/json;

    }
    location = /api/v1/sectores/geojson {
       alias /var/www/hoyodecrimen.com/hoyodecrimen.api/wsgi/static/geojson/sectores.json;
       default_type application/json;

    }
    location = /api/v1/municipios/geojson {
       alias /var/www/hoyodecrimen.com/hoyodecrimen.api/wsgi/static/geojson/municipios.json;
       default_type application/json;
    }
    location / {
        include uwsgi_params;
        uwsgi_pass unix:/tmp/hoyodecrimen.sock;
    }
}

