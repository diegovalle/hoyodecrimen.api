from flask.ext.sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry

db = SQLAlchemy()

class Cuadrantes(db.Model):
    __tablename__ = 'cuadrantes'
    cuadrante = db.Column(db.String(10), primary_key=True)
    crime = db.Column(db.String(60))
    date = db.Column(db.String(10))
    count = db.Column(db.Integer)
    year = db.Column(db.Integer)
    sector = db.Column(db.String(60))
    population = db.Column(db.Integer)

    def __init__(self, cuadrante, crime, date, count, year, sector, population):
        self.cuadrante = cuadrante
        self.crime = crime
        self.date = date
        self.count = count
        self.year = year
        self.sector = sector
        self.population = population

class Cuadrantes_Poly(db.Model):
    __tablename__ = 'cuadrantes_poly'
    id = db.Column(db.String(60), primary_key=True)
    sector = db.Column(db.String(60))
    geom = db.Column(Geometry(geometry_type='MULTIPOLYGON', srid=4326))

    def __init__(self, id, sector, geom):
        self.id = id
        self.sector = sector
        self.geom = geom


# psql -d apihoyodecrimen -U $OPENSHIFT_POSTGRESQL_DB_USERNAME -W
# CREATE TABLE cuadrantes (
# 	cuadrante varchar (10),
# 	crime varchar (60),
# 	date  varchar (10),
# 	count int,
#        year int,
#        sector varchar(60),
#        population integer,
#        PRIMARY KEY(cuadrante, sector, crime, date)
# );
# COPY cuadrantes FROM '/var/lib/openshift/543fe7165973cae5d30000c1/app-root/repo/data/cuadrantes.csv' DELIMITER ',' NULL AS 'NA' CSV HEADER;


# shp2pgsql -s 4326 -W "latin1" -I -D cuadrantes-sspdf-no-errors.shp cuadrantes_poly > cuadrantes_poly.sql
# ogr2ogr -f "GeoJSON" cuadrantes.geojson cuadrantes-sspdf-no-errors.shp
# scp *.sql 543fe7165973cae5d30000c1@apihoyodecrimen-valle.rhcloud.com:app-root/data/

#psql apihoyodecrimen -c "CREATE EXTENSION postgis;"
#psql -d apihoyodecrimen $OPENSHIFT_POSTGRESQL_DB_USERNAME  < cuadrantes_poly.sql
