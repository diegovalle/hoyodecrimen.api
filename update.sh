#!/bin/bash
#  ./update.sh postgres://deploy:xxxxx@hoyodecrimen.com:44765/apihoyodecrimen xxxx

set -euo pipefail #exit on error, undefined and prevent pipeline errors
IFS=$'\n\t'
URL="https://data.diegovalle.net/hoyodecrimen"

wget -N $URL/crime-lat-long-pgj.csv.zip $URL/cuadrantes-pgj.csv.zip $URL/pgj.csv.zip -P "$TMPDIR"
(cd "$TMPDIR" && unzip -o -d "$TMPDIR/$(date +%Y-%m)" -j '*csv.zip')
cp "$TMPDIR"/"$(date +%Y-%m)"/*.csv "/tmp"


psql -d "$1" --set=temp="/tmp" -f update.sql
psql -d "$1" -c "VACUUM ANALYZE crime_latlong;"
psql -d "$1" -c "VACUUM ANALYZE cuadrantes;"
psql -d "$1" -c "VACUUM ANALYZE pgj;"

curl -X POST -d "CACHE_SECRET=$2" https://hoyodecrimen.com/clear-cache
xargs -I % wget -q --show-progress --wait=14 --tries=3 -O /dev/null https://hoyodecrimen.com% < urllist.txt

# backup
# /usr/lib/postgresql/14/bin/pg_dump -d "$POSTGRES_DB" | gzip > apihoyodecrimen-$(date +%Y-%m-%d_%H-%M).sql.gz
# restore
# gunzip -c apihoyodecrimen-<DATE>.sql.gz | /usr/lib/postgresql/14/bin/psql -d "$POSTGRES_DB"
