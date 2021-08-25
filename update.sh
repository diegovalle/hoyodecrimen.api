#!/bin/bash
set -euo pipefail #exit on error, undefined and prevent pipeline errors
IFS=$'\n\t'

psql -d apihoyodecrimen -f update.sql

psql -d apihoyodecrimen -c "VACUUM ANALYZE crime_latlong;"
psql -d apihoyodecrimen -c "VACUUM ANALYZE cuadrantes;"
psql -d apihoyodecrimen -c "VACUUM ANALYZE pgj;"
