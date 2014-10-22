from datetime import datetime
from flask import Flask, jsonify, request, abort, make_response, url_for, send_from_directory,send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text, literal_column, literal
from sqlalchemy import func, and_
from flask.ext.cache import Cache
from werkzeug.contrib.profiler import ProfilerMiddleware
from functools import wraps
from geoalchemy2 import Geometry
from geoalchemy2.elements import WKTElement
import time
import os
#from redis import Redis
 

#START_STATE = '2013-01'
#LAST_STRING = 'last'


app = Flask(__name__)

# cache = Cache(app, config={
#             'CACHE_TYPE': 'redis',
#             'CACHE_REDIS_URL': 'redis://127.0.0.1:16379',
#         })

app.config.from_pyfile('apihoyodecrimen.cfg')
cache = Cache(app, config={
         'CACHE_TYPE': 'filesystem',
         'CACHE_DIR': '/tmp',
         'CACHE_DEFAULT_TIMEOUT': 922337203685477580,
         'CACHE_THRESHOLD': 922337203685477580
     })
cache.init_app(app)
db = SQLAlchemy(app)

#from api import *
db.create_all()

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



def jsonp(func):
    """Wraps JSONified output for JSONP requests."""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            data = str(func(*args, **kwargs).data)
            content = str(callback) + '(' + data + ')'
            mimetype = 'application/javascript'
            return app.response_class(content, mimetype=mimetype)
        else:
            return func(*args, **kwargs)
    return decorated_function

def ResultProxy_to_json(results):
    json_results = []
    keys = results.keys()
    for result in results:
            d = {}
            for i, key in enumerate(keys):
                if key == "date":
                    d["year"] = int(result[key][0:4])
                    d["month"] = int(result[key][5:7])
                else:
                    d[key] = result[key]
            json_results.append(d)
    return jsonify(rows = json_results)


def results_to_array(results):
    json_results = []
    if len(results) > 0:
        keys = results[0].keys()
        for result in results:
            d = {}
            for i, key in enumerate(keys):
                if key == "date":
                    d["year"] = int(result[i][0:4])
                    d["month"] = int(result[i][5:7])
                else:
                    d[key] = result[i]
            json_results.append(d)
        return json_results
    else:
        return []

def results_to_json(results):
    # response = jsonify({'code': 404,'message': 'No found'})
    # response.status_code = 404
    # return response
    return jsonify(rows = results_to_array(results))

def month_sub(date, months):
    m = (int(date[5:7]) + months) % 12
    y = int(date[0:4]) + ((int(date[5:7])) + months - 1) // 12
    if not m: 
        m = 12
    d = str(y) + '-' + str(m).zfill(2) + '-01'
    return d

def month_diff(d1, d2):
    date1 = datetime.strptime(d1, '%Y-%m-01')
    date2 = datetime.strptime(d2, '%Y-%m-01')
    return (date1.year - date2.year) * 12 + date1.month - date2.month + 1

def check_date_month(str):
    try:
        time.strptime(str, '%Y-%m-01')
        valid = True
    except ValueError:
        valid = False
    return valid

def check_float(str):
    try:
        float(str)
        valid = True
    except ValueError:
        valid = False
    return valid


def check_dates(start_period, end_period):
    if end_period != '' or start_period != '':
        end_period += '-01'
        start_period += '-01'
        if not check_date_month(start_period):
            abort(abort(make_response('something is wrong with the start_period date you provided', 400)))
        if not check_date_month(end_period):
            abort(abort(make_response('something is wrong with the end_period date you provided', 400)))
        if time.strptime(start_period, '%Y-%m') > time.strptime(end_period, '%Y-%m'):
            abort(abort(make_response('date order not valid', 400)))
        if start_period < '2013-01':
            abort(abort(make_response('start_period must be greater than 2013-01', 400)))
        max_date = end_period
        start_date = start_period
    else:
        max_date = Cuadrantes.query. \
                filter(). \
                with_entities(func.max(Cuadrantes.date).label('date')). \
                scalar()
        start_date = month_sub(max_date, -11)
    return start_date, max_date

_basedir = os.path.abspath(os.path.dirname(__file__))
 


@app.route('/api/')
def api_html():
    return app.send_static_file(os.path.join('api', 'index.html'))

@app.route('/')
def index():
    return app.send_static_file(os.path.join('', 'index.html'))

@app.route('/api/_static/<path:filename>')
def static__api(filename):
    return send_from_directory(os.path.join(_basedir, 'static/api/_static'), filename)

@app.route('/css/<path:filename>')
def static_css(filename):
    return send_from_directory(os.path.join(_basedir, 'static/css'), filename)

@app.route('/js/<path:filename>')
def static_js(filename):
    return send_from_directory(os.path.join(_basedir, 'static/js'), filename)

@app.route('/font/<path:filename>')
def static_font(filename):
    return send_from_directory(os.path.join(_basedir, 'static/font'), filename)

@app.route('/images/<path:filename>')
def static_images(filename):
    return send_from_directory(os.path.join(_basedir, 'static/images'), filename)


@app.route('/v1/pip/'
          '<string:long>/'
          '<string:lat>',
          methods=['GET'])
@jsonp
def pip(long, lat):
    """Given a latitude and longitude determine the cuadrante they correspond to.

    :param long: longitude
    :param lat: longitude

    :status 200: when the cuadrante corresponding to the latitude and longitude is found
    :status 400: when the latitude or longitude where incorrectly specified

    **Example request**:

    .. sourcecode:: http

      GET /v1/pip/-99.13333/19.43 HTTP/1.1
      Host: hoyodecrimen.com
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.0 200 OK
      Content-Type: application/json

      {
      "pip": [
      {
          "cuadrante": "c-1.4.4",
          "geomery": "{\"type\":\"MultiPolygon\",\"coordinates\":[[[[-99.129543,19.436234],[-99.12966,19.435347],[-99.129766,19.43449],[-99.12994,19.433287],[-99.130025,19.432576],[-99.130206,19.431322],[-99.130576,19.428702],[-99.132613,19.428972],[-99.136883,19.429561],[-99.136343,19.433343],[-99.136008,19.435295],[-99.135754,19.437014],[-99.13479,19.436886],[-99.133691,19.436745],[-99.131628,19.436484],[-99.129543,19.436234]]]]}",
          "sector": "corredor - centro"
      }
      ]
      }

    """
    # sql_query = """SELECT ST_AsGeoJSON(geom) as geom,id,sector
    #                 FROM cuadrantes_poly
    #                 where ST_Contains(geom,ST_GeometryFromText('POINT(-99.13 19.43)',4326))=True;"""
    if request.method == 'GET':
        if not check_float(long):
            abort(abort(make_response('something is wrong with the longitude you provided', 400)))
        if not check_float(lat):
            abort(abort(make_response('something is wrong with the latitude you provided', 400)))
        point = WKTElement("POINT(%s %s)" % (long, lat), srid=4326)
        results_pip = Cuadrantes_Poly.query. \
            filter(func.ST_Contains(Cuadrantes_Poly.geom, point).label("geom")==True). \
            with_entities(func.lower(Cuadrantes_Poly.id.label("cuadrante")),
                          func.lower(Cuadrantes_Poly.sector).label("sector"),
                          func.ST_AsGeoJSON(Cuadrantes_Poly.geom).label("geom")). \
            first()
        if(results_pip is not None):
            json_results = []
            d = {}
            d['geomery'] = results_pip[2]
            d['cuadrante'] = results_pip[0]
            d['sector'] = results_pip[1]
            json_results.append(d)
        else:
            results_cuad=[]
            json_results=[]
            results_df_last_year=[]
            results_cuad_last_year=[]
        return jsonify(pip = json_results)


@app.route('/v1/pip/extras/'
          '<string:long>/'
          '<string:lat>',
          methods=['GET'])
@jsonp
def frontpage(long, lat):
    """Given a latitude and longitude determine the cuadrante they correspond to. Include extra crime info

    Returns a list containg the cuadrante polygon as GeoJSON, all the crimes that occurred in the cuadrante
    by date, the sum of crime counts that occurred in the DF, and in the cuadrante during the last year

    :param long: long
    :param lat: lat

    :status 200: when the cuadrante corresponding to the latitude and longitude is found
    :status 400: when the latitude or longitude where incorrectly specified

    **Example request**:

    .. sourcecode:: http

      GET /v1/pip/extras/-99.13333/19.43 HTTP/1.1
      Host: hoyodecrimen.com
      Accept: application/json
    """
    # sql_query = """SELECT ST_AsGeoJSON(geom) as geom,id,sector
    #                 FROM cuadrantes_poly
    #                 where ST_Contains(geom,ST_GeometryFromText('POINT(-99.13 19.43)',4326))=True;"""
    if request.method == 'GET':
        if not check_float(long):
            abort(abort(make_response('something is wrong with the longitude you provided', 400)))
        if not check_float(lat):
            abort(abort(make_response('something is wrong with the latitude you provided', 400)))
        point = WKTElement("POINT(%s %s)" % (long, lat), srid=4326)
        results_pip = Cuadrantes_Poly.query. \
            filter(func.ST_Contains(Cuadrantes_Poly.geom, point).label("geom")==True). \
            with_entities(func.lower(Cuadrantes_Poly.id.label("cuadrante")),
                          func.lower(Cuadrantes_Poly.sector).label("sector"),
                          func.ST_AsGeoJSON(Cuadrantes_Poly.geom).label("geom")). \
            first()
        if(results_pip is not None):
            results_cuad = Cuadrantes.query. \
                    filter(func.lower(Cuadrantes.cuadrante) == results_pip[0]). \
                    with_entities(func.lower(Cuadrantes.cuadrante).label('cuadrante'),
                                  func.lower(Cuadrantes.sector).label('sector'),
                                  func.lower(Cuadrantes.crime).label('crime'),
                                  Cuadrantes.date,
                                  Cuadrantes.count,
                                  Cuadrantes.population) \
                    .order_by(Cuadrantes.crime, Cuadrantes.date) \
                    .all()

            # compare the cuadrante with the rest of the DF (last 12 months)
            max_date = Cuadrantes.query. \
                with_entities(func.max(Cuadrantes.date).label('date')). \
                scalar()
            start_date = month_sub(max_date, -11)
            results_df_last_year = Cuadrantes.query. \
                filter(and_(Cuadrantes.date <= max_date, Cuadrantes.date >= start_date)). \
                with_entities(func.lower(Cuadrantes.crime).label('crime'),
                              func.sum(Cuadrantes.count).label('count'),
                              func.sum(Cuadrantes.population).op("/")(12).label('population')). \
                group_by(Cuadrantes.crime). \
                order_by(Cuadrantes.crime). \
                all()
            results_cuad_last_year = Cuadrantes.query. \
                filter(and_(Cuadrantes.date <= max_date, Cuadrantes.date >= start_date),
                       func.lower(Cuadrantes.cuadrante) == results_pip[0]). \
                with_entities(func.lower(Cuadrantes.crime).label('crime'),
                              func.sum(Cuadrantes.count).label('count'),
                              func.sum(Cuadrantes.population).label('population')). \
                group_by(Cuadrantes.crime). \
                order_by(Cuadrantes.crime). \
                all()

            json_results = []
            d = {}
            d['geomery'] = results_pip[2]
            d['cuadrante'] = results_pip[0]
            d['sector'] = results_pip[1]
            json_results.append(d)
        else:
            results_cuad=[]
            json_results=[]
            results_df_last_year=[]
            results_cuad_last_year=[]
        return jsonify(pip = json_results,
                       cuadrante = results_to_array(results_cuad),
                       df_last_year = results_to_array(results_df_last_year),
                       cuadrante_last_year = results_to_array(results_cuad_last_year))



@cache.cached(timeout=None)
@app.route('/v1/series/df/'
          '<string:crime>',
          methods=['GET'])
@jsonp
def df_all(crime):
    """Return the sum of crimes that occurred in the Federal District

    :param crime: the name of crime or the keyword ``all``

    :status 200: when the sum of all crimes is found

    **Example request**:

    .. sourcecode:: http

      GET /v1/series/df/violacion HTTP/1.1
      Host: hoyodecrimen.com
      Accept: application/json
    """
    if request.method == 'GET':
        crime = crime.lower()
        if crime == "all":
            filters = [True]
        else:
            filters = [func.lower(Cuadrantes.crime) == crime]
        results = Cuadrantes.query. \
            filter(*filters). \
            with_entities(func.lower(Cuadrantes.crime).label('crime'),
                          Cuadrantes.date,
                          func.sum(Cuadrantes.count).label('count'),
                          func.sum(Cuadrantes.population).label('population')). \
            group_by(Cuadrantes.date, Cuadrantes.crime). \
            order_by(Cuadrantes.date, Cuadrantes.crime). \
            all()
        return results_to_json(results)




@app.route('/v1/series/cuadrantes/'
          '<string:crime>/'
          '<string:cuadrante>',
          methods=['GET'])
@jsonp
def cuadrantes(crime, cuadrante):
    """Return the count of crimes that occurred in a cuadrante, by date

    :param crime: the name of crime or the keyword ``all`` to return all crimes
    :param cuadrante: the name of the cuadrante from which to return the time series

    :status 200: when the sum of all crimes is found

    **Example request**:

    .. sourcecode:: http

      GET /v1/series/cuadrantes/violacion/c-1.1.1 HTTP/1.1
      Host: hoyodecrimen.com
      Accept: application/json
    """
    if request.method == 'GET':
        cuadrante = cuadrante.lower()
        crime = crime.lower()

        start_period = request.args.get('start_period', '', type=str)
        end_period = request.args.get('end_period', '', type=str)
        start_date, max_date = check_dates(start_period, end_period)

        if crime == "all":
            filters = [func.lower(Cuadrantes.cuadrante) == cuadrante,
                       func.lower(Cuadrantes.crime) == crime]
        else:
            filters = [func.lower(Cuadrantes.cuadrante) == cuadrante]

        results = Cuadrantes.query. \
            filter(*filters). \
            with_entities(func.lower(Cuadrantes.cuadrante).label('cuadrante'),
                          func.lower(Cuadrantes.sector).label('sector'),
                          func.lower(Cuadrantes.crime).label('crime'),
                          Cuadrantes.date,
                          Cuadrantes.count,
                          Cuadrantes.population) \
            .order_by(Cuadrantes.crime, Cuadrantes.date) \
            .all()
        #results = db.session.execute("select cuadrante, sector, crime, date, count, population from cuadrantes order by crime, date, cuadrante, sector where cuadrante = ?", (cuadrante_id,))
        return results_to_json(results)

@cache.cached(timeout=None)
@app.route('/v1/series/sectores/'
          '<string:crime>/'
          '<string:sector>',
          methods=['GET'])
@jsonp
def sectors(crime, sector):
    """Return the count of crimes that occurred in a sector, by date

    :param crime: the name of crime or the keyword ``all`` to return all crimes
    :param cuadrante: the name of the cuadrante from which to return the time series

    :status 200: when the sum of all crimes is found

    **Example request**:

    .. sourcecode:: http

      GET /v1/series/sectores/violacion/angel%20-%20zona%20rosa HTTP/1.1
      Host: hoyodecrimen.com
      Accept: application/json
    """
    if request.method == 'GET':
        sector = sector.lower()
        crime = crime.lower()
        if crime == "all":
            filters = [func.lower(Cuadrantes.sector) == sector,
                       func.lower(Cuadrantes.crime) == crime]
        else:
            filters = [func.lower(Cuadrantes.sector) == sector]
        results = Cuadrantes.query. \
            filter(*filters). \
            with_entities(func.lower(Cuadrantes.sector).label('sector'),
                          func.lower(Cuadrantes.crime).label('crime'),
                          Cuadrantes.date,
                          func.sum(Cuadrantes.count).label('count'),
                          func.sum(Cuadrantes.population).label('population')). \
            group_by(Cuadrantes.crime, Cuadrantes.date, Cuadrantes.sector). \
            order_by(Cuadrantes.crime, Cuadrantes.date). \
            all()
        return results_to_json(results)



@cache.cached(timeout=None)
@app.route('/v1/list/cuadrantes/<string:crime>',
          methods=['GET'])
@jsonp
def cuadrantes_sum_all(crime):
    """Return the sum of crimes that occurred in each cuadrante for a specified period of time

    By default it returns the sum of crimes during the last 12 months

    :param crime: the name of crime or the keyword ``all`` to return all crimes

    :status 200: when the sum of all crimes is found

    **Example request**:

    .. sourcecode:: http

      GET /v1/list/cuadrantes/all HTTP/1.1
      Host: hoyodecrimen.com
      Accept: application/json

    :query start_period: Start of the period from which to start aggregating in the ``%Y-%m`` format (e.g. 2013-01)
    :query end_period: End of the period to analyze in the ``%Y-%m`` format (e.g. 2013-06). Must be greater or equal to start_period
    """
    if request.method == 'GET':
        crime = crime.lower()
        start_period = request.args.get('start_period', '', type=str)
        end_period = request.args.get('end_period', '', type=str)
        start_date, max_date = check_dates(start_period, end_period)
        if crime == "all":
            filters = [and_(Cuadrantes.date >= start_date, Cuadrantes.date <= max_date)]
        else:
            filters = [and_(Cuadrantes.date >= start_date, Cuadrantes.date <= max_date),
                       func.lower(Cuadrantes.crime) == crime]
        results = Cuadrantes.query. \
            filter(*filters). \
            with_entities(literal(start_date, type_=db.String).label('start_date'),
                          literal(max_date, type_=db.String).label('end_date'),
                          func.lower(Cuadrantes.cuadrante).label('cuadrante'),
                          func.lower(Cuadrantes.sector).label('sector'),
                          func.lower(Cuadrantes.crime).label('crime'),
                          func.sum(Cuadrantes.count).label("count"),
                          func.sum(Cuadrantes.population).op("/")(month_diff(max_date, start_date)).label("population")) \
            .group_by(Cuadrantes.crime, Cuadrantes.sector, Cuadrantes.cuadrante) \
            .order_by(Cuadrantes.crime, Cuadrantes.cuadrante) \
            .all()
        #results = db.session.execute("select cuadrante, sector, crime, date, count, population from cuadrantes order by crime, date, cuadrante, sector where cuadrante = ?", (cuadrante_id,))
        return results_to_json(results)


@cache.cached(timeout=50)
@app.route('/v1/list/sectores/<string:crime>',
          methods=['GET'])
@jsonp
def sectores_sum_all(crime):
    """Return the sum of crimes that occurred in each sectore for a specified period of time

    By default it returns the sum of crimes during the last 12 months

    :param crime: the name of crime or the keyword ``all`` to return all crimes

    :status 200: when the sum of all crimes is found

    **Example request**:

    .. sourcecode:: http

      GET /v1/list/sectores/all HTTP/1.1
      Host: hoyodecrimen.com
      Accept: application/json

    :query start_period: Start of the period from which to start aggregating in the ``%Y-%m`` format (e.g. 2013-01)
    :query end_period: End of the period to analyze in the ``%Y-%m`` format (e.g. 2013-06). Must be greater or equal to start_period
    """
    if request.method == 'GET':
        crime = crime.lower()
        start_period = request.args.get('start_period', '', type=str)
        end_period = request.args.get('end_period', '', type=str)
        start_date, max_date = check_dates(start_period, end_period)
        if crime == "all":
            filters = [and_(Cuadrantes.date >= start_date, Cuadrantes.date <= max_date)]
        else:
            filters = [and_(Cuadrantes.date >= start_date, Cuadrantes.date <= max_date),
                       func.lower(Cuadrantes.crime) == crime]
        results = Cuadrantes.query. \
            filter(*filters). \
            with_entities(literal(start_date, type_=db.String).label('start_date'),
                          literal(max_date, type_=db.String).label('end_date'),
                          func.lower(Cuadrantes.sector).label('sector'),
                          func.lower(Cuadrantes.crime).label('crime'),
                          func.sum(Cuadrantes.count).label("count"),
                          func.sum(Cuadrantes.population).op("/")(month_diff(max_date, start_date)).label("population")) \
            .group_by(Cuadrantes.crime, Cuadrantes.sector) \
            .order_by(Cuadrantes.crime, Cuadrantes.sector) \
            .all()
        return results_to_json(results)



@cache.cached(timeout=50)
@app.route('/v1/list/change/cuadrantes/<string:crime>',
          methods=['GET'])
@jsonp
def cuadrantes_change_sum_all(crime):
    """Return the change in crime counts for a specified period of time at the cuadrante level

    By default it returns the sum of crimes during the last 12 months

    :param crime: the name of crime or the keyword ``all`` to return all crimes

    :status 200: when the  change in crime counts is found

    **Example request**:

    .. sourcecode:: http

      GET /v1/list/change/cuadrantes/all HTTP/1.1
      Host: hoyodecrimen.com
      Accept: application/json

    :query start_period: Start of the period from which to start aggregating in the ``%Y-%m`` format (e.g. 2013-01)
    :query end_period: End of the period to analyze in the ``%Y-%m`` format (e.g. 2013-06). Must be greater or equal to start_period
    """
    if request.method == 'GET':
        crime = crime.lower()
        start_period1 = request.args.get('start_period1', '', type=str)
        start_period2 = request.args.get('start_period2', '', type=str)
        end_period1 = request.args.get('end_period1', '', type=str)
        end_period2 = request.args.get('end_period2', '', type=str)

        # if crime == "all":
        #     filters = [and_(Cuadrantes.date >= start_date, Cuadrantes.date <= max_date)]
        # else:
        #     filters = [and_(Cuadrantes.date >= start_date, Cuadrantes.date <= max_date),
        #                func.lower(Cuadrantes.crime) == crime]
        if end_period1 != '' or end_period2 != '' or start_period1 != '' or start_period2 != '':
            if not check_date_month(end_period1):
                abort(abort(make_response('something is wrong with the end_period1 date you provided', 400)))
            if not check_date_month(end_period2):
                abort(abort(make_response('something is wrong with the end_period2 date you provided', 400)))
            if not check_date_month(start_period1):
                abort(abort(make_response('something is wrong with the start_period1 date you provided', 400)))
            if not check_date_month(start_period2):
                abort(abort(make_response('something is wrong with the start_period2 date you provided', 400)))
            if time.strptime(end_period2, '%Y-%m') >= time.strptime(start_period2, '%Y-%m') or \
               time.strptime(end_period1, '%Y-%m') >= time.strptime(start_period1, '%Y-%m') or \
               time.strptime(end_period2, '%Y-%m') >= time.strptime(start_period1, '%Y-%m'):
                abort(abort(make_response('date order not valid', 400)))
            max_date = end_period2
            max_date_minus3 = start_period2
            max_date_last_year = end_period1
            max_date_last_year_minus3 = start_period1
        else:
            max_date = Cuadrantes.query. \
                        filter(). \
                        with_entities(func.max(Cuadrantes.date).label('date')). \
                        scalar()
            max_date_minus3 = month_sub(max_date, -2)
            max_date_last_year = month_sub(max_date, -12)
            max_date_last_year_minus3 = month_sub(max_date, -14)
        sql_query1 = """select lower(crime) as crime, lower(cuadrante) as cuadrante,
                               lower(sector) as sector, max(population) as population,
                               :max_date_minus3 as start_period2, :max_date as end_period2,
                               :max_date_last_year as end_period1, :max_date_last_year_minus3 as start_period1,
                                                   sum(case when date <= :max_date and date >= :max_date_minus3
                                                   THEN count ELSE 0 END) as period2_count,
                                                   sum(case when date <= :max_date_last_year and date >= :max_date_last_year_minus3
                                                   THEN count ELSE 0 END) as period1_count,
                                                   sum(case when date <= :max_date and date >= :max_date_minus3
                                                   THEN count ELSE 0 END) -
                                                   sum(case when date <= :max_date_last_year and date >= :max_date_last_year_minus3
                                                   THEN count ELSE 0 END) as difference
                                            from cuadrantes
                                            """
        sql_query2 = "" if crime == "all" else " where lower(crime) = :crime "
        sql_query3 = """group by cuadrante, sector, crime
                        order by crime asc, difference desc, cuadrante asc"""
        results = db.session.execute(sql_query1 + sql_query2 + sql_query3, {'max_date':max_date,
                                                 'max_date_minus3':max_date_minus3,
                                                 'max_date_last_year':max_date_last_year,
                                                 'max_date_last_year_minus3': max_date_last_year_minus3,
                                                 'crime': crime})
        return ResultProxy_to_json(results)
        # results = Cuadrantes.query. \
        #     filter(*filters). \
        #     with_entities(literal(start_date, type_=db.String).label('start_date'),
        #                   literal(max_date, type_=db.String).label('end_date'),
        #                   func.lower(Cuadrantes.sector).label('sector'),
        #                   func.lower(Cuadrantes.crime).label('crime'),
        #                   func.sum(Cuadrantes.count).label("count"),
        #                   func.sum(Cuadrantes.population).op("/")(month_diff(start_date, max_date)).label("population")) \
        #     .group_by(Cuadrantes.crime, Cuadrantes.sector) \
        #     .order_by(Cuadrantes.crime, Cuadrantes.sector) \
        #     .all()
        return results_to_json(results)



@app.route('/v1/enumerate/crimes')
@jsonp
def listcrimes():
    """Enumerate all the crimes in the database

   :status 200: when all the crimes were found

   **Example request**:

   .. sourcecode:: http

      GET /v1/enumerate/crimes HTTP/1.1
      Host: hoyodecrimen.com
      Accept: application/json
"""
    if request.method == 'GET':
        results = Cuadrantes.query. \
                  with_entities(func.lower(Cuadrantes.crime).label('crime')).\
                  distinct().\
                  all()
        return results_to_json(results)


@app.route('/v1/enumerate/cuadrantes')
@jsonp
def listcuadrantes():
    """Enumerate all the cuadrantes in the database

    :status 200: when all the cuadrantes were found

    **Example request**:

    .. sourcecode:: http

       GET /v1/enumerate/cuadrantes HTTP/1.1
       Host: hoyodecrimen.com
       Accept: application/json
    """
    if request.method == 'GET':
        results = Cuadrantes.query. \
                  with_entities(func.lower(Cuadrantes.sector).label('sector'),
                                func.lower(Cuadrantes.cuadrante).label('cuadrante')).\
                  distinct().\
                  all()
        return results_to_json(results)


@app.route('/v1/enumerate/sectores')
@jsonp
def listsectores():
    """Enumerate all the sectores in the database

   :status 200: when all the sectores were found

   **Example request**:

   .. sourcecode:: http

      GET /v1/enumerate/sectores HTTP/1.1
      Host: hoyodecrimen.com
      Accept: application/json
    """
    if request.method == 'GET':
        results = Cuadrantes.query. \
                  with_entities(func.lower(Cuadrantes.sector).label('sector')).\
                  distinct().\
                  all()
        return results_to_json(results)



@app.route('/v1/top/counts/cuadrante/<string:crime>')
@jsonp
def top5cuadrantes(crime):
    """Return the top ranked cuadrantes with the highest crime **counts** for a given period of time.

    When no date parameters are specified the top 5 cuadrantes are returned for the last 12 months
    (e.g. If July is the last date in the database, then the period July 2014 to Aug 2013 will be analyzed).
    All population data returned by this call is in persons/year and comes from the 2010 census

    :param crime: the name of a crime or the keyword ``all``

    :status 200: when the top 5 cuadrantes are found
    :status 400: when the one of the dates was incorrectly specified or the periods overlap

    **Example request**:

    .. sourcecode:: http

      GET /v1/top5/counts/cuadrante/homicidio%20doloso HTTP/1.1
      Host: hoyodecrimen.com
      Accept: application/json

    :query start_period: Start of the period from which to start counting
    :query end_period: End of the period to analyze. Must be greater or equal to start_period
    :query rank: Return all cuadrantes ranked higher. Defaults to `5`
    """
    if request.method == 'GET':
        crime = crime.lower()
        start_period = request.args.get('start_period', '', type=str)
        end_period = request.args.get('end_period', '', type=str)
        start_date, max_date = check_dates(start_period, end_period)
        rank = request.args.get('rank', 5, type=int)
        if rank <= 0:
             abort(abort(make_response('No negative numbers', 400)))
        sql_query = """with crimes as
                          (select sum(count) as count,sector,cuadrante,max(population)as population, crime
                          from cuadrantes
                          where date >= :start_date and date <= :max_date"""
        sql_query2 = "" if crime == "all" else " and lower(crime) = :crime "
        sql_query3 =             """
                          group by cuadrante, sector, crime)
                       SELECT *
                       from
                          (SELECT :start_date as start_period, :max_date as end_period, count,lower(crime) as crime,
                                  lower(sector) as sector,lower(cuadrante) as cuadrante,
                                  rank() over (partition by crime order by count desc) as rank,population
                          from crimes group by count,crime,sector,cuadrante,population) as temp2
                          where rank <= :rank
                          order by crime, rank, cuadrante, sector asc"""
        results = db.session.execute(sql_query + sql_query2 + sql_query3, {'start_date':start_date,
                                                 'max_date':max_date,
                                                 'crime': crime,
                                                 'rank': rank})
        return ResultProxy_to_json(results)


@app.route('/v1/top/rates/sector/<string:crime>')
@jsonp
def top5sectores(crime):
    """Return the top ranked sectors with the highest crime **rates** for a given period of time.

    When no date parameters are specified the top 5 cuadrantes are returned for the last 12 months
    (e.g. If July is the last date in the database then the period July 2014 to Aug 2013 will be analyzed).
    All population data returned by this call is in persons/year and comes from the 2010 census

    :param crime: the name of a crime or the keyword ``all``
    :status 200: when the top 5 cuadrantes are found
    :status 400: when the one of the dates was incorrectly specified or the periods overlap

    **Example request**:

    .. sourcecode:: http

      GET /v1/top/rates/sector/homicidio%20doloso HTTP/1.1
      Host: hoyodecrimen.com
      Accept: application/json

    :query start_period: Start of the period from which to start counting
    :query end_period: End of the period to analyze. Must be greater or equal to start_period
    :query rank: Return all sectores with a rate ranked higher. Defaults to `5`
    """
    if request.method == 'GET':
        crime = crime.lower()
        start_period = request.args.get('start_period', '', type=str)
        end_period = request.args.get('end_period', '', type=str)
        start_date, max_date = check_dates(start_period, end_period)
        rank = request.args.get('rank', 5, type=int)
        if rank <= 0:
             abort(abort(make_response('No negative numbers', 400)))
        sql_query = """with crimes as
                           (select (sum(count) / (sum(population::float) / :num_months )* 100000) as rate,sum(count) as count,
                           sector,sum(population) / :num_months as population, crime
                           from cuadrantes
                           where date >= :start_date and date <= :max_date"""
        sql_query2 = "" if crime == "all" else " and lower(crime) = :crime "
        sql_query3 =             """   group by sector, crime)
                       SELECT * from
                           (SELECT :start_date as start_period, :max_date as end_period, count,rate,lower(crime) as crime,
                                   lower(sector) as sector,
                                   rank() over (partition by crime order by rate desc) as rank,population
                           from crimes
                           group by count,crime,sector,population, rate) as temp2
                           where rank <= :rank"""
        results = db.session.execute(sql_query + sql_query2 + sql_query3, {'start_date':start_date,
                                                 'max_date':max_date,
                                                 'crime': crime,
                                                 'num_months': month_diff(max_date, start_date),
                                                 'rank': rank})
        return ResultProxy_to_json(results)


@app.route('/v1/top/counts/change/cuadrantes/<string:crime>')
@jsonp
def top5changecuadrantes(crime):
    """Return the top ranked cuadrantes were crime **counts** increased the most.

    When no date parameters are specified the top 5 cuadrantes are returned for the last 3 months compared
    with the same period during the previous year (e.g. July-May 2014 compared with July-May 2013).
    All population data returned by this call is in persons/year and comes from the 2010 census

    :param crime: the name of a crime or the keyword ``all``
    :status 200: when the top 5 cuadrantes are found
    :status 400: when the one of the dates was incorrectly specified or the periods overlap

    **Example request**:

    .. sourcecode:: http

       GET /v1/top/counts/change/cuadrantes/homicidio%20doloso HTTP/1.1
       Host: hoyodecrimen.com
       Accept: application/json

    :query start_period1: Start of the period from which to start counting. Together with end_period1 this will specify the first period
    :query end_period1: End of the first period
    :query start_period2: Start of the period from which to start counting. Together with end_period2 this will specify the second period
    :query end_period2: End of the second period
    :query rank: Return the top X ranked cuadrantes
    """
    if request.method == 'GET':
        crime = crime.lower()
        start_period1 = request.args.get('start_period1', '', type=str)
        start_period2 = request.args.get('start_period2', '', type=str)
        end_period1 = request.args.get('end_period1', '', type=str)
        end_period2 = request.args.get('end_period2', '', type=str)
        rank = request.args.get('rank', 5, type=int)
        if rank <= 0:
             abort(abort(make_response('No negative numbers', 400)))
        if end_period1 != '' or end_period2 != '' or start_period1 != '' or start_period2 != '':
            if not check_date_month(end_period1):
                abort(abort(make_response('something is wrong with the end_period1 date you provided', 400)))
            if not check_date_month(end_period2):
                abort(abort(make_response('something is wrong with the end_period2 date you provided', 400)))
            if not check_date_month(start_period1):
                abort(abort(make_response('something is wrong with the start_period1 date you provided', 400)))
            if not check_date_month(start_period2):
                abort(abort(make_response('something is wrong with the start_period2 date you provided', 400)))
            if time.strptime(end_period2, '%Y-%m') >= time.strptime(start_period2, '%Y-%m') or \
               time.strptime(end_period1, '%Y-%m') >= time.strptime(start_period1, '%Y-%m') or \
               time.strptime(end_period2, '%Y-%m') >= time.strptime(start_period1, '%Y-%m'):
                abort(abort(make_response('date order not valid', 400)))
            max_date = end_period2
            max_date_minus3 = start_period2
            max_date_last_year = end_period1
            max_date_last_year_minus3 = start_period1
        else:
            max_date = Cuadrantes.query. \
                        filter(). \
                        with_entities(func.max(Cuadrantes.date).label('date')). \
                        scalar()
            max_date_minus3 = month_sub(max_date, -2)
            max_date_last_year = month_sub(max_date, -12)
            max_date_last_year_minus3 = month_sub(max_date, -14)
        sql_query1 = """with difference as
                                           (select crime, cuadrante, sector, max(population) as population,
                                                   sum(case when date <= :max_date and date >= :max_date_minus3
                                                   THEN count ELSE 0 END) as period2_count,
                                                   sum(case when date <= :max_date_last_year and date >= :max_date_last_year_minus3
                                                   THEN count ELSE 0 END) as period1_count,
                                                   sum(case when date <= :max_date and date >= :max_date_minus3
                                                   THEN count ELSE 0 END) -
                                                   sum(case when date <= :max_date_last_year and date >= :max_date_last_year_minus3
                                                   THEN count ELSE 0 END) as difference
                                            from cuadrantes
                                            """
        sql_query2 = "" if crime == "all" else " where lower(crime) = :crime "
        sql_query3 = """
                                            group by cuadrante, sector, crime)
                                        SELECT *
                                        from (
                                            SELECT rank() over (partition by crime order by difference desc) as rank,
                                                   lower(crime) as crime, lower(cuadrante) as cuadrante,
                                                   lower(sector) as sector,population, period1_count, period2_count,
                                                   difference from difference
                                            group by difference,crime,sector,cuadrante, population,  period1_count, period2_count)
                                        as temp
                                        where rank <= :rank
                                        order by crime, rank, cuadrante, sector asc"""
        results = db.session.execute(sql_query1 + sql_query2 + sql_query3, {'max_date':max_date,
                                                 'max_date_minus3':max_date_minus3,
                                                 'max_date_last_year':max_date_last_year,
                                                 'max_date_last_year_minus3': max_date_last_year_minus3,
                                                 'crime': crime,
                                                 'rank': rank})
        return ResultProxy_to_json(results)


 
if __name__ == '__main__':
    app.config['PROFILE'] = True
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
    app.run(debug=True)

