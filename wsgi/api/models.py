from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry

db = SQLAlchemy()

class Cuadrantes(db.Model):
    __tablename__ = 'cuadrantes'
    cuadrante = db.Column(db.String(20), primary_key=True)
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

class pgj(db.Model):
    __tablename__ = 'pgj'
    crime = db.Column(db.String(60), primary_key=True)
    date = db.Column(db.String(10))
    count = db.Column(db.Integer)

    def __init__(self, crime, date, count):
        self.crime = crime
        self.date = date
        self.count = count

class Cuadrantes_Poly(db.Model):
    __tablename__ = 'cuadrantes_poly'
    id = db.Column(db.String(60), primary_key=True)
    sector = db.Column(db.String(60))
    geom = db.Column(Geometry(geometry_type='MULTIPOLYGON', srid=4326))

    def __init__(self, id, sector, geom):
        self.id = id
        self.sector = sector
        self.geom = geom


class Crime_latlong(db.Model):
    __tablename__ = 'crime_latlong'
    id = db.Column(db.Integer, primary_key=True)
    cuadrante = db.Column(db.String(60))
    crime = db.Column(db.String(60))
    date = db.Column(db.String(10))
    hour = db.Column(db.String(10))
    year = db.Column(db.String(10))
    month = db.Column(db.String(10))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    geom = db.Column(Geometry(geometry_type='POINT', srid=4326))

    def __init__(self, cuadrante, crime, date, hour, year, month, latitude, longitude, geom):
        self.cuadrante = cuadrante
        self.crime = crime
        self.date = date
        self.hour = hour
        self.year = year
        self.month = month
        self.latitude = latitude
        self.longitude = longitude
        self.geom = geom

class Municipios(db.Model):
    __tablename__ = 'municipios'
    cuadrante = db.Column(db.String(15), primary_key=True)
    sector = db.Column(db.String(60))
    cvegeo = db.Column(db.String(5))
    municipio = db.Column(db.String(200))

    def __init__(self, cuadrante, sector, cvegeo, municipio):
        self.cuadrante = cuadrante
        self.sector = sector
        self.cvegeo = cvegeo
        self.municipio = municipio


class json_files(db.Model):
    __tablename__ = 'json_files'
    name = db.Column(db.String(25), primary_key=True)
    data = db.Column(db.LargeBinary)

    def __init__(self, cuadrante, sector, cvegeo, municipio):
        self.name = name
        self.data = data

# psql -d apihoyodecrimen -U $OPENSHIFT_POSTGRESQL_DB_USERNAME -W
# CREATE TABLE cuadrantes (
# 	cuadrante varchar (15),
# 	crime varchar (60),
# 	date  varchar (10),
# 	count int,
#        year int,
#        sector varchar(60),
#        population integer,
#        PRIMARY KEY(cuadrante, sector, crime, date)
# );
# COPY cuadrantes FROM '/var/lib/openshift/543fe7165973cae5d30000c1/app-root/repo/data/cuadrantes.csv' DELIMITER ',' NULL AS 'NA' CSV HEADER;


# CREATE TABLE municipios (
# 	cuadrante varchar (15),
# 	sector varchar (60),
# 	cvegeo  varchar (5),
# 	municipio varchar(200),
#     PRIMARY KEY(cuadrante)
# );
# COPY cuadrantes FROM '/var/lib/openshift/543fe7165973cae5d30000c1/app-root/repo/data/municipios.csv' DELIMITER ',' NULL AS 'NA' CSV HEADER;


#create index date on cuadrantes (date);
#create index sector on cuadrantes (sector);
#create index cuadrante on cuadrantes (cuadrante);
#create index crime on cuadrantes (crime);
#create index ds on cuadrantes (date, sector);
#create index dc on cuadrantes (date, cuadrante);
#create index date_crime on cuadrantes (date, crime);


# shp2pgsql -s 4326 -W "latin1" -I -D cuadrantes-sspdf-no-errors.shp cuadrantes_poly > cuadrantes_poly.sql
# ogr2ogr -f "GeoJSON" cuadrantes.geojson cuadrantes-sspdf-no-errors.shp
# scp *.sql 543fe7165973cae5d30000c1@apihoyodecrimen-valle.rhcloud.com:app-root/data/

#psql apihoyodecrimen -c "CREATE EXTENSION postgis;"
#psql -d apihoyodecrimen $OPENSHIFT_POSTGRESQL_DB_USERNAME  < cuadrantes_poly.sql

#create index geom on cuadrantes_poly using gist (geom);
#create index geom_cuad on cuadrantes_poly using gist (geom, id);
#create index sector on cuadrantes_poly (sector);
#create index cuad on cuadrantes_poly (id);
