from datetime import datetime
from flask import Flask, jsonify, request, abort, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from sqlalchemy import func, and_
from flask.ext.cache import Cache
from werkzeug.contrib.profiler import ProfilerMiddleware
from functools import wraps
from geoalchemy2 import Geometry
from geoalchemy2.elements import WKTElement
#from redis import Redis
 

START_STATE = '2013-01'
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

# class Cuadrantes_Poly(db.Model):
#     __tablename__ = 'cuadrantes_poly'
#     id = db.Column(db.String(60), primary_key=True)
#     sector = db.Column(db.String(60))
#     geom = db.Column(Geometry(geometry_type='MULTIPOLYGON', srid=4326))
#
#     def __init__(self, id, sector, geom):
#         self.id = id
#         self.sector = sector
#         self.geom = geom

def jsonp(f):
    """Wraps JSONified output for JSONP"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            content = str(callback) + '(' + str(f(*args, **kwargs).data) + ')'
            return current_app.response_class(content, mimetype='application/javascript')
        else:
            return f(*args, **kwargs)

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

def results_to_json(results, n = 1):
    json_results = []
    if len(results) > 0:
        keys = results[0].keys()
        for result in results:
            d = {}
            for i, key in enumerate(keys):
                if key == "date":
                    d["year"] = int(result[i][0:4])
                    d["month"] = int(result[i][5:7])
                elif key == "population" and n != 1:
                    d["population"] = result[i] / n if result[i] is not None else result[i]
                else:
                    d[key] = result[i]
            json_results.append(d)

        return jsonify(rows=json_results) #Response(json.dumps(json_results),  mimetype='application/json')#
    else:
        return jsonify(rows=[])

def monthsub(date, months):
    m = (int(date[5:7]) + months) % 12
    y = int(date[0:4]) + ((int(date[5:7])) + months - 1) // 12
    if not m: 
        m = 12
    return str(y) + '-' + str(m).zfill(2) + '-01'

def check_date_month(str):
    try:
        time.strptime(str, '%Y-%m')
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
 
@app.route('/')
def index():
    return "Hello from API"

# @jsonp
# @app.route('/v1/pip/'
#           '<string:long>/'
#           '<string:lat>',
#           methods=['GET'])
# def pip(long, lat):
#     # sql_query = """SELECT ST_AsGeoJSON(geom) as geom,id,sector
#     #                 FROM cuadrantes_poly
#     #                 where ST_Contains(geom,ST_GeometryFromText('POINT(-99.13 19.43)',4326))=True;"""
#     if not check_float(long):
#         abort(abort(make_response('something is wrong with the longitude you provided', 400)))
#     if not check_float(lat):
#         abort(abort(make_response('something is wrong with the latitude you provided', 400)))
#     point = WKTElement("POINT(%s %s)" % (long, lat), srid=4326)
#     results = Cuadrantes_Poly.query. \
#         filter(func.ST_Contains(Cuadrantes_Poly.geom, point).label("geom")==True). \
#         with_entities(func.lower(Cuadrantes_Poly.id.label("cuadrante")),
#                       Cuadrantes_Poly.sector,
#                       func.ST_AsGeoJSON(Cuadrantes_Poly.geom).label("geom")). \
#         first()
#     return jsonify(rows=results)


@jsonp
@app.route('/v1/df/'
          'all',
          methods=['GET'])
def df_all_crime():
    if request.method == 'GET':
        results = Cuadrantes.query. \
            with_entities(func.lower(Cuadrantes.crime).label('crime'),
                          Cuadrantes.date,
                          func.sum(Cuadrantes.count).label('count'),
                          func.sum(Cuadrantes.population).label('population')). \
            group_by(Cuadrantes.crime, Cuadrantes.date). \
            order_by(Cuadrantes.crime, Cuadrantes.date). \
            all()
    return results_to_json(results)

@cache.cached(timeout=50, key_prefix='all_comments')
@jsonp
@app.route('/v1/df/'
          'last_12_months',
        #'<string:cuadrante>',
          methods=['GET'])
def df_all_last_year():
    if request.method == 'GET':
        max_date = Cuadrantes.query. \
            with_entities(func.max(Cuadrantes.date).label('date')). \
            scalar()
        start_date = monthsub(max_date, -11)
        results_df = Cuadrantes.query. \
            filter(and_(Cuadrantes.date <= max_date, Cuadrantes.date >= start_date)). \
            with_entities(func.lower(Cuadrantes.crime).label('crime'),
                          func.sum(Cuadrantes.count).label('count'),
                          func.sum(Cuadrantes.population).label('population')). \
            group_by(Cuadrantes.crime). \
            order_by(Cuadrantes.crime). \
            all()
        # results = Cuadrantes.query. \
        #     filter(and_(Cuadrantes.date <= max_date, Cuadrantes.date >= start_date),
        #            func.lower(Cuadrantes.cuadrante) == cuadrante). \
        #     with_entities(func.lower(Cuadrantes.crime).label('crime'),
        #                   func.sum(Cuadrantes.count).label('count'),
        #                   func.sum(Cuadrantes.population).label('population')). \
        #     group_by(Cuadrantes.crime). \
        #     order_by(Cuadrantes.crime). \
        #     all()
    return results_to_json(results_df, 12)


@jsonp
@cache.cached(timeout=None)
@app.route('/v1/df/'
          '<string:crime>',
          methods=['GET'])
def df_all(crime):
    if request.method == 'GET':
        results = Cuadrantes.query. \
            filter(Cuadrantes.crime == crime). \
            with_entities(func.lower(Cuadrantes.crime).label('crime'),
                          Cuadrantes.date,
                          func.sum(Cuadrantes.count).label('count'),
                          func.sum(Cuadrantes.population).label('population')). \
            group_by(Cuadrantes.date, Cuadrantes.crime). \
            order_by(Cuadrantes.date). \
            all()
    return results_to_json(results)

@jsonp
@app.route('/v1/cuadrantes/'
          '<string:crime>/'
          '<string:cuadrante>',
          methods=['GET'])
def cuadrantes(crime, cuadrante):
    if request.method == 'GET':
        results = Cuadrantes.query. \
            filter(Cuadrantes.cuadrante == cuadrante,
                   Cuadrantes.crime == crime). \
            with_entities(func.lower(Cuadrantes.cuadrante).label('cuadrante'),
                          func.lower(Cuadrantes.sector).label('sector'),
                          func.lower(Cuadrantes.crime).label('crime'),
                          Cuadrantes.date,
                          Cuadrantes.count,
                          Cuadrantes.population) \
            .order_by(Cuadrantes.date) \
            .all()
        #results = db.session.execute("select cuadrante, sector, crime, date, count, population from cuadrantes order by crime, date, cuadrante, sector where cuadrante = ?", (cuadrante_id,))
    return results_to_json(results)

@jsonp
@app.route('/v1/cuadrantes/'
          'all/'
          '<string:cuadrante>',
          methods=['GET'])
def cuadrantes_all(cuadrante):
    if request.method == 'GET':
        results = Cuadrantes.query. \
            filter(func.lower(Cuadrantes.cuadrante) == cuadrante). \
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

@jsonp
@cache.cached(timeout=None)
@app.route('/v1/sum/cuadrantes/all',
          methods=['GET'])
def cuadrantes_sum_all():
    if request.method == 'GET':
        max_date = Cuadrantes.query. \
            filter(). \
            with_entities(func.max(Cuadrantes.date).label('date')). \
            scalar()
        start_date = monthsub(max_date, -11)
        results = Cuadrantes.query. \
            filter(and_(Cuadrantes.date >= start_date, Cuadrantes.date <= max_date)). \
            with_entities(func.lower(Cuadrantes.cuadrante).label('cuadrante'),
                          func.lower(Cuadrantes.sector).label('sector'),
                          func.lower(Cuadrantes.crime).label('crime'),
                          func.sum(Cuadrantes.count).label("count"),
                          func.sum(Cuadrantes.population).label("population")) \
            .group_by(Cuadrantes.crime, Cuadrantes.sector, Cuadrantes.cuadrante) \
            .order_by(Cuadrantes.crime, Cuadrantes.cuadrante) \
            .all()
        #results = db.session.execute("select cuadrante, sector, crime, date, count, population from cuadrantes order by crime, date, cuadrante, sector where cuadrante = ?", (cuadrante_id,))
    return results_to_json(results, 12)

@jsonp
@cache.cached(timeout=50)
@app.route('/v1/sum/sectores/all',
          methods=['GET'])
def sectores_sum_all():
    if request.method == 'GET':
        max_date = Cuadrantes.query. \
            filter(). \
            with_entities(func.max(Cuadrantes.date).label('date')). \
            scalar()
        start_date = monthsub(max_date, -11)
        results = Cuadrantes.query. \
            filter(and_(Cuadrantes.date >= start_date, Cuadrantes.date <= max_date)). \
            with_entities(func.lower(Cuadrantes.sector).label('sector'),
                          func.lower(Cuadrantes.crime).label('crime'),
                          func.sum(Cuadrantes.count).label("count"),
                          func.sum(Cuadrantes.population).label("population")) \
            .group_by(Cuadrantes.crime, Cuadrantes.sector) \
            .order_by(Cuadrantes.crime, Cuadrantes.sector) \
            .all()
    return results_to_json(results, 12)

@jsonp
@app.route('/v1/sectores/'
          '<string:crime>/'
          '<string:sector>',
          methods=['GET'])
def sectors(crime, sector):
    if request.method == 'GET':
        results = Cuadrantes.query. \
            filter(Cuadrantes.sector == sector,
                   Cuadrantes.crime == crime). \
            with_entities(func.lower(Cuadrantes.sector).label('sector'),
                          func.lower(Cuadrantes.crime).label('crime'),
                          Cuadrantes.date,
                          func.sum(Cuadrantes.count).label('count'),
                          func.sum(Cuadrantes.population).label('population')). \
            group_by(Cuadrantes.crime, Cuadrantes.date, Cuadrantes.sector). \
            order_by(Cuadrantes.date). \
            all()
    return results_to_json(results)

@jsonp
@app.route('/v1/list/crimes')
def listcrimes():
    results = Cuadrantes.query. \
              with_entities(func.lower(Cuadrantes.crime).label('crime')).\
              distinct().\
              all()
    return results_to_json(results)

@jsonp
@app.route('/v1/list/cuadrantes')
def listcuadrantes():
    results = Cuadrantes.query. \
              with_entities(func.lower(Cuadrantes.sector).label('sector'),
                            func.lower(Cuadrantes.cuadrante).label('cuadrante')).\
              distinct().\
              all()
    return results_to_json(results)

@jsonp
@app.route('/v1/list/sectores')
def listsectores():
    results = Cuadrantes.query. \
              with_entities(func.lower(Cuadrantes.sector).label('sector')).\
              distinct().\
              all()
    return results_to_json(results)


@jsonp
@app.route('/v1/top5/counts/cuadrante')
def top5cuadrantes():
    max_date = Cuadrantes.query. \
            filter(). \
            with_entities(func.max(Cuadrantes.date).label('date')). \
            scalar()
    start_date = monthsub(max_date, -11)
    sql_query = """with crimes as
                      (select sum(count) as count,sector,cuadrante,max(population)as population, crime
                      from cuadrantes
                      where date >= '{0}' and date <= '{1}'
                      group by cuadrante, sector, crime)
                   SELECT *
                   from
                      (SELECT count,lower(crime) as crime,lower(sector) as sector,lower(cuadrante) as cuadrante,
                      rank() over (partition by crime order by count desc) as rank,population
                      from crimes group by count,crime,sector,cuadrante,population) as temp2
                      where rank <= 5
                      order by crime, rank, cuadrante, sector asc""".format(start_date, max_date)
    results = db.engine.execute(sql_query)
    return ResultProxy_to_json(results)

@jsonp
@app.route('/v1/top5/rates/sector')
def top5sectores():
    max_date = Cuadrantes.query. \
            filter(). \
            with_entities(func.max(Cuadrantes.date).label('date')). \
            scalar()
    start_date = monthsub(max_date, -11)
    sql_query = text("""with crimes as
                       (select (sum(count) / (sum(population::float) /12 )* 100000) as rate,sum(count) as count,sector,sum(population)/12 as population, crime
                       from cuadrantes
                       where date >= '{0}' and date <= '{1}'
                       group by sector, crime)
                   SELECT * from
                       (SELECT count,rate,lower(crime) as crime,lower(sector) as sector,rank() over (partition by crime order by rate desc) as rank,population
                       from crimes
                       group by count,crime,sector,population, rate) as temp2
                       where rank <= 5""".format(start_date, max_date))
    results = db.session.execute(sql_query)
    return ResultProxy_to_json(results)

@jsonp
@app.route('/v1/top5/counts/change/cuadrantes')
def top5changecuadrantes():
    # start=request.args.get('start', START_STATE)
    # end=request.args.get('end', LAST_STRING)
    # if end != 'last':
    #     if not check_date_month(end):
    #         abort(abort(make_response('something is wrong with the end date you provided', 400)))
    # if not check_date_month(start):
    #     abort(abort(make_response('something is wrong with the start date you provided', 400)))
    max_date = Cuadrantes.query. \
            filter(). \
            with_entities(func.max(Cuadrantes.date).label('date')). \
            scalar()
    max_date_minus3 = monthsub(max_date, -2)
    max_date_last_year = monthsub(max_date, -12)
    max_date_last_year_minus3 = monthsub(max_date, -14)
    sql_query = """with difference as
                                       (select crime, cuadrante, sector, max(population) as population,
                                               sum(case when date <= '{0}' and date >= '{1}'
                                               THEN count ELSE 0 END) as end_count,
                                               sum(case when date <= '{2}' and date >= '{3}'
                                               THEN count ELSE 0 END) as start_count,
                                               sum(case when date <= '{0}' and date >= '{1}'
                                               THEN count ELSE 0 END) -
                                               sum(case when date <= '{2}' and date >= '{3}'
                                               THEN count ELSE 0 END) as difference
                                        from cuadrantes
                                        group by cuadrante, sector, crime)
                                    SELECT *
                                    from (
                                        SELECT rank() over (partition by crime order by difference desc) as rank,
                                               lower(crime) as crime, lower(cuadrante) as cuadrante,
                                               lower(sector) as sector,population, start_count, end_count,
                                               difference from difference
                                        group by difference,crime,sector,cuadrante, population, start_count, end_count)
                                    as temp
                                    where rank <= 5
                                    order by crime, rank, cuadrante, sector asc""".format(max_date,
                                                                                          max_date_minus3,
                                                                                          max_date_last_year,
                                                                                          max_date_last_year_minus3)
    results = db.session.execute(sql_query)
    return ResultProxy_to_json(results)


 
if __name__ == '__main__':
    app.config['PROFILE'] = True
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
    app.run(debug=True)

