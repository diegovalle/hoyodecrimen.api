from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
 
app = Flask(__name__)
 
app.config.from_pyfile('todoapp.cfg')
db = SQLAlchemy(app)

#psql -d dbname -U username -W
#CREATE TABLE cuadrantes (
#	cuadrante varchar (10),
#	crime varchar (60),
#	date  varchar (10),
#	count int,
#        year int,
#        sector varchar(60),
#        population integer,
#        PRIMARY KEY(cuadrante, sector, crime, date)
#);
#COPY cuadrantes FROM '/var/lib/openshift/543fe7165973cae5d30000c1/app-root/repo/data/cuadrantes.csv' DELIMITER ',' NULL AS 'NA' CSV HEADER;

class Cuadrantes(db.Model):
    __tablename__ = 'cuadrantes'
    cuadrante = db.Column(db.String(7), primary_key=True)
    crime = db.Column(db.String(60))
    date = db.Column(db.String(10))
    count = db.Column(db.Integer)
    year = db.Column(db.Integer)
    sector = db.Column(db.String(60))
    population = db.Column(db.Integer)

    def __init__(self, cuadrante, crime, date, count, year, sector, population):
        self.cuadrante = title
        self.crime = text
        self.date = date
        self.count = count
        self.year = year
        self.sector = sector
        self.population = population
 
@app.route('/')
@app.route('/hello')
def index():
    return "Hello from OpenShift"
 
if __name__ == '__main__':
    app.run()

from api import *
db.create_all()
