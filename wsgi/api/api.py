from flask import Blueprint, Flask, jsonify, \
    request, abort, make_response, url_for, \
    send_from_directory, send_file, current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text, literal_column, literal
from sqlalchemy.dialects.mssql import INTEGER, DATE
from sqlalchemy.orm import join
from sqlalchemy import func, and_, or_
from flask_cache import Cache
from werkzeug.contrib.profiler import ProfilerMiddleware
from functools import wraps
from geoalchemy2.elements import WKTElement
import time
import os
from models import db, Cuadrantes, Cuadrantes_Poly, Municipios, Crime_latlong
import lib
from lib import InvalidAPIUsage
from urlparse import urlparse


_basedir = os.path.abspath(os.path.dirname(__file__))

# Use redis if not running in Openshift
if 'OPENSHIFT_APP_UUID' not in os.environ:
    cache = Cache(config={
        'CACHE_TYPE': 'simple'  # null or simple
    })
else:
    cache = Cache(config={
        'CACHE_TYPE': 'redis',
        # 'CACHE_REDIS_URL': 'redis://:' +os.environ['REDIS_PASSWORD']
        # +'@' + os.environ['OPENSHIFT_REDIS_HOST'] + ':'
        # + os.environ['OPENSHIFT_REDIS_PORT'],
        'CACHE_DEFAULT_TIMEOUT': 2592000,  # One month
        'CACHE_REDIS_PASSWORD': os.environ['REDIS_PASSWORD'],
        'CACHE_REDIS_HOST': os.environ['OPENSHIFT_REDIS_HOST'],
        'CACHE_REDIS_PORT': os.environ['OPENSHIFT_REDIS_PORT'],
        'CACHE_KEY_PREFIX': 'hoyodecrimen'
    })


API = Blueprint('API', __name__, url_prefix='/api/v1')

def process_crime(crime, start_date, max_date, sector="none", cuadrante="none", municipio="none"):
    if crime == "ALL":
        filters = [and_(Cuadrantes.date >= start_date, Cuadrantes.date <= max_date)]
    else:
        filters = [or_(*[func.upper(Cuadrantes.crime) == x for x in crime.split(',')])]
        filters.append(and_(Cuadrantes.date >= start_date, Cuadrantes.date <= max_date))
    if sector != "none":
        if sector != "ALL":
            filters.append(func.upper(Cuadrantes.sector) == sector)
    if cuadrante != "none":
        if cuadrante != "ALL":
            filters.append(func.upper(Cuadrantes.cuadrante) == cuadrante)
    if municipio != "none":
        if municipio != "ALL":
            filters.append(func.upper(Municipios.municipio) == municipio)
    return filters

def make_cache_key(*args, **kwargs):
    # Make sure the cache distinguishes requests with different parameters
    o = urlparse(request.url)
    # remove the scheme and netloc to make caching more portable
    return o.path + o.query


@API.errorhandler(InvalidAPIUsage)
def invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    #h = response.headers
    #h['Access-Control-Allow-Origin'] = "*"
    return response


def jsonp(func):
    """Wraps JSONified output for JSONP requests."""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            data = str(func(*args, **kwargs).data)
            content = str(callback) + '(' + data + ')'
            mimetype = 'application/javascript'
            return current_app.response_class(content, mimetype=mimetype)
        else:
            return func(*args, **kwargs)
    return decorated_function

@cache.memoize()
def check_dates(start_period, end_period, default_start=None):
    start_period += '-01'
    end_period += '-01'
    if end_period != '-01' or start_period != '-01':
        if not lib.check_date_month(start_period):
            raise InvalidAPIUsage('something is wrong with the '
                                  'start_date date you provided')
        if not lib.check_date_month(end_period):
            raise InvalidAPIUsage('something is wrong with the '
                                  'end_date date you provided')
        if start_period > end_period:
            raise InvalidAPIUsage('date order not valid')
        max_date = end_period
        start_date = start_period
    else:
        max_date = Cuadrantes.query. \
            filter(). \
            with_entities(func.max(Cuadrantes.date).label('date')). \
            scalar()
        if not default_start:
            start_date = lib.month_sub(max_date, -11)
        else:
            start_date = default_start
    return start_date, max_date

@API.route('/cuadrantes/geojson')
@jsonp
def cuad_geojson():
    """Returns a map of the cuadrantes delictivos encoded as geojson

    :status 200: return a geojson map

    :resheader Content-Type: application/json

    **Example request**:

    .. sourcecode:: http

      GET /api/v1/cuadrantes/geojson HTTP/1.1
      Host: hoyodecrimen.com
      Accept: application/json
    """
    return send_from_directory(os.path.join(_basedir, '..', 'static', 'geojson'), 'cuadrantes.json')

@API.route('/sectores/geojson')
@jsonp
def sectores_geojson():
    """Returns a map of the sectores delictivos encoded as geojson

    :status 200: return a geojson map

    :resheader Content-Type: application/json

    **Example request**:

    .. sourcecode:: http

      GET /api/v1/sectores/geojson HTTP/1.1
      Host: hoyodecrimen.com
      Accept: application/json
    """
    return send_from_directory(os.path.join(_basedir, '..', 'static', 'geojson'), 'sectores.json')

@API.route('/municipios/geojson')
@jsonp
def muns_geojson():
    """Returns a map of the municipios that make up the Federal District encoded as geojson

    :status 200: return a geojson map

    :resheader Content-Type: application/json

    **Example request**:

    .. sourcecode:: http

      GET /api/v1/municipios/geojson HTTP/1.1
      Host: hoyodecrimen.com
      Accept: application/json
    """
    return send_from_directory(os.path.join(_basedir, '..', 'static', 'geojson'), 'municipios.json')

# @API.route('/estariamosmejorcon', methods=['GET'])
# @jsonp
# @cache.cached(key_prefix=make_cache_key)
# def estariamosmejorcon():
#     """Return the once and future president of Mexico

#     :status 200: when the best man for the job is a good ol' regular citizen
#     :status 666: when the best man for the job is president once more

#     :resheader Content-Type: application/json

#     **Example request**:

#     .. sourcecode:: http

#       GET /api/v1/estariamosmejorcon HTTP/1.1
#       Host: hoyodecrimen.com
#       Accept: application/json

#     """
#     return jsonify(rows=['Calderon'])


@API.route('/cuadrantes/pip/'
           '<string:long>/'
           '<string:lat>',
           methods=['GET'])
@jsonp
#@cache.cached(key_prefix=make_cache_key)
def pip(long, lat):
    """Given a latitude and longitude determine the cuadrante they correspond to.

    :param long: longitude
    :param lat: longitude

    :status 200: when the cuadrante corresponding to the latitude and longitude is found
    :status 400: when the latitude or longitude where incorrectly specified
    :status 404: when the latitude or longitude are outside of the Federal District cuadrante area

    :resheader Content-Type: application/json

    **Example request**:

    .. sourcecode:: http

      GET /api/v1/cuadrantes/pip/-99.13333/19.43 HTTP/1.1
      Host: hoyodecrimen.com
      Accept: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json

      {
        "pip":
          [
            {
              "cuadrante": "C-1.4.4",
              "geomery": "{\"type\":\"MultiPolygon\",\"coordinates\":[[[[-99.129543,19.436234],[-99.12966,19.435347],[-99.129766,19.43449],[-99.12994,19.433287],[-99.130025,19.432576],[-99.130206,19.431322],[-99.130576,19.428702],[-99.132613,19.428972],[-99.136883,19.429561],[-99.136343,19.433343],[-99.136008,19.435295],[-99.135754,19.437014],[-99.13479,19.436886],[-99.133691,19.436745],[-99.131628,19.436484],[-99.129543,19.436234]]]]}",
              "sector": "CORREDOR - CENTRO"
            }
          ]
      }

    """
    # sql_query = """SELECT ST_AsGeoJSON(geom) as geom,id,sector
    #                 FROM cuadrantes_poly
    #                 where ST_Contains(geom,ST_GeometryFromText('POINT(-99.13 19.43)',4326))=True;"""
    if not lib.check_float(long):
        raise InvalidAPIUsage('something is wrong with the longitude you provided')
    if not lib.check_float(lat):
        raise InvalidAPIUsage('something is wrong with the latitude you provided')
    point = WKTElement("POINT(%s %s)" % (long, lat), srid=4326)
    results_pip = Cuadrantes_Poly.query. \
        filter(func.ST_Contains(Cuadrantes_Poly.geom, point).label("geom")). \
        with_entities(func.upper(Cuadrantes_Poly.id.label("cuadrante")),
                      func.upper(Cuadrantes_Poly.sector).label("sector"),
                      func.ST_AsGeoJSON(Cuadrantes_Poly.geom).label("geom")). \
        first()
    if results_pip is not None:
        json_results = [{'geometry': results_pip[2],
             'cuadrante': results_pip[0],
             'sector': results_pip[1]}]
    else:
        raise InvalidAPIUsage("You're not inside the Federal District provinciano", 404)
    return jsonify(pip=json_results)


@cache.memoize()
def get_df_period(start_date, max_date, crime):
    if crime == "ALL":
        filters = [and_(Cuadrantes.date >= start_date, Cuadrantes.date <= max_date)]
    else:
        filters = [or_(*[func.upper(Cuadrantes.crime) == x for x in crime.split(',')])]
        filters.append(and_(Cuadrantes.date >= start_date, Cuadrantes.date <= max_date))
    return Cuadrantes.query. \
        filter(*filters). \
        with_entities(func.upper(Cuadrantes.crime).label('crime'),
                      func.sum(Cuadrantes.count).label('count'),
                      func.sum(Cuadrantes.population).op("/")(lib.month_diff(max_date, start_date)).label('population')). \
        group_by(Cuadrantes.crime). \
        order_by(Cuadrantes.crime). \
        all()


@cache.memoize()
def get_cuad_period(cuadrante, crime, start_date, max_date):
    if crime == "ALL":
        filters = [and_(Cuadrantes.date >= start_date, Cuadrantes.date <= max_date),
                   func.upper(Cuadrantes.cuadrante) == cuadrante]
    else:
        filters = [or_(*[func.upper(Cuadrantes.crime) == x for x in crime.split(',')])]
        filters.append(func.upper(Cuadrantes.cuadrante) == cuadrante)
        filters.append(and_(Cuadrantes.date >= start_date, Cuadrantes.date <= max_date))
        #filters = [and_(Cuadrantes.date >= start_date, Cuadrantes.date <= max_date),
        #           func.upper(Cuadrantes.crime) == crime,
        #           func.upper(Cuadrantes.cuadrante) == cuadrante]
    return Cuadrantes.query. \
        filter(*filters). \
        with_entities(func.upper(Cuadrantes.crime).label('crime'),
                      func.sum(Cuadrantes.count).label('count'),
                      func.sum(Cuadrantes.population).op("/")(lib.month_diff(max_date, start_date)).label('population')). \
        group_by(Cuadrantes.crime). \
        order_by(Cuadrantes.crime). \
        all()


@cache.memoize()
def get_cuad_series(cuadrante, crime):
    if crime == "ALL":
        pip_filter = [func.upper(Cuadrantes.cuadrante) == cuadrante]
    else:

        pip_filter = [or_(*[func.upper(Cuadrantes.crime) == x for x in crime.split(',')])]
        pip_filter.append(func.upper(Cuadrantes.cuadrante) == cuadrante)

        #pip_filter = [func.upper(Cuadrantes.crime) == crime,
        #              func.upper(Cuadrantes.cuadrante) == cuadrante]
    results_cuad = Cuadrantes.query. \
        filter(*pip_filter). \
        with_entities(func.upper(Cuadrantes.cuadrante).label('cuadrante'),
                      func.upper(Cuadrantes.sector).label('sector'),
                      func.upper(Cuadrantes.crime).label('crime'),
                      Cuadrantes.date,
                      Cuadrantes.count,
                      Cuadrantes.population) \
        .order_by(Cuadrantes.crime, Cuadrantes.date) \
        .all()
    #import pdb; pdb.set_trace()
    return results_cuad
    # compare the cuadrante with the rest of the DF (last 12 months)
    # max_date = Cuadrantes.query. \
    #     with_entities(func.max(Cuadrantes.date).label('date')). \
    #     scalar()
    # start_date = month_sub(max_date, -11)

    # if crime == "ALL":
    #     filters = [and_(Cuadrantes.date >= start_date, Cuadrantes.date <= max_date),
    #                func.upper(Cuadrantes.cuadrante) == cuadrante]
    # else:
    #     filters = [and_(Cuadrantes.date >= start_date, Cuadrantes.date <= max_date),
    #                func.upper(Cuadrantes.crime) == crime,
    #                func.upper(Cuadrantes.cuadrante) == cuadrante]
    #
    # results_df_period = Cuadrantes.query. \
    #     filter(and_(Cuadrantes.date <= max_date, Cuadrantes.date >= start_date)). \
    #     with_entities(func.upper(Cuadrantes.crime).label('crime'),
    #                   func.sum(Cuadrantes.count).label('count'),
    #                   func.sum(Cuadrantes.population).op("/")(lib.month_diff(max_date, start_date)).label('population')). \
    #     group_by(Cuadrantes.crime). \
    #     order_by(Cuadrantes.crime). \
    #     all()
    # results_cuad_period = Cuadrantes.query. \
    #     filter(*filters). \
    #     with_entities(func.upper(Cuadrantes.crime).label('crime'),
    #                   func.sum(Cuadrantes.count).label('count'),
    #                   func.sum(Cuadrantes.population).op("/")(lib.month_diff(max_date, start_date)).label('population')). \
    #     group_by(Cuadrantes.crime). \
    #     order_by(Cuadrantes.crime). \
    #     all()


    #return results_cuad, results_df_period, results_cuad_period


@API.route('/cuadrantes/crimes/<string:crime>/pip/'
           '<string:long>/'
           '<string:lat>',
           methods=['GET'])
@jsonp
@cache.cached(key_prefix=make_cache_key)
def frontpage(crime, long, lat):
    """Given a latitude and longitude determine the cuadrante they correspond to. Include extra crime info

    Returns a list containg the cuadrante polygon as GeoJSON, all the crimes that occurred in the cuadrante
    by date, the sum of crime counts that occurred in the whole DF during the last 12 months, and the sum of crimes in
    the cuadrante containing the longitude and latitude during the last 12 months

    :param long: long
    :param lat: lat
    :param crime: the name of a crime or the keyword ``all``

    :status 200: when the cuadrante corresponding to the latitude and longitude is found
    :status 400: when the latitude or longitude where incorrectly specified
    :status 404: when the latitude or longitude are outside of the Federal District cuadrante area or the crime requested doesn't exist

    :resheader Content-Type: application/json

    **Example request**:

    .. sourcecode:: http

      GET /api/v1/cuadrantes/crimes/all/pip/-99.13333/19.43 HTTP/1.1
      Host: hoyodecrimen.com
      Accept: application/json

    **Example response (truncated)**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
      "cuadrante": [
      {
      "count": 0,
      "crime": "HOMICIDIO DOLOSO",
      "cuadrante": "C-1.4.4",
      "month": 1,
      "population": 1405,
      "sector": "CORREDOR - CENTRO",l
      "year": 2013
      },
      ...
      "cuadrante_period": [
      {
      "count": 0,
      "crime": "HOMICIDIO DOLOSO",
      "population": 16860
      },
      ...
      "df_period": [
      {
      "count": 823,
      "crime": "HOMICIDIO DOLOSO",
      "population": 8785874
      },
      ...
      "pip": [
      {
      "cuadrante": "C-1.4.4",
      "geomery": "{\"type\":\"MultiPolygon\",\"coordinates\":[[[[-99.129543,19.436234],[-99.12966,19.435347],[-99.129766,19.43449],[-99.12994,19.433287],[-99.130025,19.432576],[-99.130206,19.431322],[-99.130576,19.428702],[-99.132613,19.428972],[-99.136883,19.429561],[-99.136343,19.433343],[-99.136008,19.435295],[-99.135754,19.437014],[-99.13479,19.436886],[-99.133691,19.436745],[-99.131628,19.436484],[-99.129543,19.436234]]]]}",
      "sector": "CORREDOR - CENTRO"
      }
    """
    # sql_query = """SELECT ST_AsGeoJSON(geom) as geom,id,sector
    #                 FROM cuadrantes_poly
    #                 where ST_Contains(geom,ST_GeometryFromText('POINT(-99.13 19.43)',4326))=True;"""
    crime = crime.upper()
    start_date = request.args.get('start_date', '', type=str)
    end_date = request.args.get('end_date', '', type=str)
    start_date, max_date = check_dates(start_date, end_date)

    if not lib.check_float(long):
        raise InvalidAPIUsage('something is wrong with the longitude you provided')
        #abort(abort(make_response('something is wrong with the longitude you provided', 400)))
    if not lib.check_float(lat):
        raise InvalidAPIUsage('something is wrong with the latitude you provided')
        #abort(abort(make_response('something is wrong with the latitude you provided', 400)))
    point = WKTElement("POINT(%s %s)" % (long, lat), srid=4326)
    results_pip = Cuadrantes_Poly.query. \
        filter(func.ST_Contains(Cuadrantes_Poly.geom, point).label("geom")). \
        with_entities(func.upper(Cuadrantes_Poly.id.label("cuadrante")),
                      func.upper(Cuadrantes_Poly.sector).label("sector"),
                      func.ST_AsGeoJSON(Cuadrantes_Poly.geom).label("geom")). \
        first()
    if (results_pip is not None):
        results_cuad = get_cuad_series(results_pip[0], crime)
        results_df_period = get_df_period(start_date, max_date, crime)
        results_cuad_period = get_cuad_period(results_pip[0], crime, start_date, max_date)
        json_results = [{'geometry': results_pip[2],
             'cuadrante': results_pip[0],
             'sector': results_pip[1]}]
    else:
        raise InvalidAPIUsage("You're not inside the Federal District provinciano", 404)
    return jsonify(pip=json_results,
                   cuadrante=lib.results_to_array(results_cuad),
                   df_period=lib.results_to_array(results_df_period),
                   cuadrante_period=lib.results_to_array(results_cuad_period))


@API.route('/cuadrantes/crimes/<string:crime>/pip_extra/'
           '<string:long>/'
           '<string:lat>',
           methods=['GET'])
@jsonp
@cache.cached(key_prefix=make_cache_key)
def frontpage_extra(crime, long, lat):
    """Given a latitude and longitude determine the cuadrante they correspond to. Include extra crime info

    Returns a list containg the cuadrante polygon as GeoJSON, all the crimes that occurred in the cuadrante
    by date, the sum of crime counts that occurred in the whole DF during the last 12 months, and the sum of crimes in
    the cuadrante containing the longitude and latitude during the last 12 months

    :param long: long
    :param lat: lat
    :param crime: the name of a crime or the keyword ``all``

    :status 200: when the cuadrante corresponding to the latitude and longitude is found
    :status 400: when the latitude or longitude where incorrectly specified
    :status 404: when the latitude or longitude are outside of the Federal District cuadrante area or the crime requested doesn't exist

    :resheader Content-Type: application/json

    **Example request**:

    .. sourcecode:: http

      GET /api/v1/cuadrantes/crimes/all/pip_extra/-99.13333/19.43 HTTP/1.1
      Host: hoyodecrimen.com
      Accept: application/json

    **Example response (truncated)**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
      "cuadrante": [
      {
      "count": 0,
      "crime": "HOMICIDIO DOLOSO",
      "cuadrante": "C-1.4.4",
      "month": 1,
      "population": 1405,
      "sector": "CORREDOR - CENTRO",l
      "year": 2013
      },
      ...
      "cuadrante_period": [
      {
      "count": 0,
      "crime": "HOMICIDIO DOLOSO",
      "population": 16860
      },
      ...
      "df_period": [
      {
      "count": 823,
      "crime": "HOMICIDIO DOLOSO",
      "population": 8785874
      },
      ...
      "latlong": [
      {
      "crime": "VIOLACION",
      "date": "2016-08-15",
      "hour": "12:00",
      "lat": 19.428935,
      "long": -99.136566
      },
       ...
      "pip": [
      {
      "cuadrante": "C-1.4.4",
      "geomery": "{\"type\":\"MultiPolygon\",\"coordinates\":[[[[-99.129543,19.436234],[-99.12966,19.435347],[-99.129766,19.43449],[-99.12994,19.433287],[-99.130025,19.432576],[-99.130206,19.431322],[-99.130576,19.428702],[-99.132613,19.428972],[-99.136883,19.429561],[-99.136343,19.433343],[-99.136008,19.435295],[-99.135754,19.437014],[-99.13479,19.436886],[-99.133691,19.436745],[-99.131628,19.436484],[-99.129543,19.436234]]]]}",
      "sector": "CORREDOR - CENTRO"
      }
    """
    # sql_query = """SELECT ST_AsGeoJSON(geom) as geom,id,sector
    #                 FROM cuadrantes_poly
    #                 where ST_Contains(geom,ST_GeometryFromText('POINT(-99.13 19.43)',4326))=True;"""
    crime = crime.upper()
    start_date = request.args.get('start_date', '', type=str)
    end_date = request.args.get('end_date', '', type=str)
    start_date, max_date = check_dates(start_date, end_date)

    if not lib.check_float(long):
        raise InvalidAPIUsage('something is wrong with the longitude you provided')
        #abort(abort(make_response('something is wrong with the longitude you provided', 400)))
    if not lib.check_float(lat):
        raise InvalidAPIUsage('something is wrong with the latitude you provided')
        #abort(abort(make_response('something is wrong with the latitude you provided', 400)))
    point = WKTElement("POINT(%s %s)" % (long, lat), srid=4326)
    results_pip = Cuadrantes_Poly.query. \
        filter(func.ST_Contains(Cuadrantes_Poly.geom, point).label("geom")). \
        with_entities(func.upper(Cuadrantes_Poly.id.label("cuadrante")),
                      func.upper(Cuadrantes_Poly.sector).label("sector"),
                      func.ST_AsGeoJSON(Cuadrantes_Poly.geom).label("geom")). \
        first()
    if (results_pip is not None):
        results_cuad = get_cuad_series(results_pip[0], crime)
        results_df_period = get_df_period(start_date, max_date, crime)
        results_cuad_period = get_cuad_period(results_pip[0], crime, start_date, max_date)

        results_sphere = Crime_latlong.query. \
                         filter(func.ST_Distance_Sphere(point, Crime_latlong.geom) <= 500). \
            with_entities(func.upper(Crime_latlong.crime).label("crime"),
                          func.upper(Crime_latlong.date).label("date"),
                          func.upper(Crime_latlong.hour).label("hour"),
                          Crime_latlong.latitude.label("lat"),
                          Crime_latlong.longitude.label("long")). \
            order_by(Crime_latlong.crime.desc(), Crime_latlong.date.desc()). \
            all()
        json_results = [{'geometry': results_pip[2],
             'cuadrante': results_pip[0],
             'sector': results_pip[1]}]
    else:
        raise InvalidAPIUsage("You're not inside the Federal District provinciano", 404)
    return jsonify(pip=json_results,
                   cuadrante=lib.results_to_array(results_cuad),
                   df_period=lib.results_to_array(results_df_period),
                   cuadrante_period=lib.results_to_array(results_cuad_period),
                   latlong=results_sphere)


@API.route('/latlong/crimes/<string:crime>/coords/'
           '<string:long>/'
           '<string:lat>/distance/<int:distance>',
           methods=['GET'])
@jsonp
@cache.cached(key_prefix=make_cache_key)
def latlong(crime, long, lat, distance):
    """Given a latitude and longitude return all crimes within a certain distance

    Returns a list containg the cuadrante polygon as GeoJSON, all the crimes that occurred in the cuadrante
    by date, the sum of crime counts that occurred in the whole DF during the last 12 months, and the sum of crimes in
    the cuadrante containing the longitude and latitude during the last 12 months

    :param long: long
    :param lat: lat
    :param crime: the name of a crime or the keyword ``all``

    :status 200: when the cuadrante corresponding to the latitude and longitude is found
    :status 400: when the latitude or longitude where incorrectly specified
    :status 404: when the latitude or longitude are outside of the Federal District cuadrante area or the crime requested doesn't exist

    :resheader Content-Type: application/json

    **Example request**:

    .. sourcecode:: http

      GET /api/v1/cuadrantes/crimes/all/coords/-99.13333/19.43/distance/500 HTTP/1.1
      Host: hoyodecrimen.com
      Accept: application/json

    **Example response (truncated)**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
      "cuadrante": [
      {
      "count": 0,
      "crime": "HOMICIDIO DOLOSO",
      "cuadrante": "C-1.4.4",
      "month": 1,
      "population": 1405,
      "sector": "CORREDOR - CENTRO",l
      "year": 2013
      },
      ...
      "cuadrante_period": [
      {
      "count": 0,
      "crime": "HOMICIDIO DOLOSO",
      "population": 16860
      },
      ...
      "df_period": [
      {
      "count": 823,
      "crime": "HOMICIDIO DOLOSO",
      "population": 8785874
      },
      ...
      "latlong": [
      {
      "crime": "VIOLACION",
      "date": "2016-08-15",
      "hour": "12:00",
      "lat": 19.428935,
      "long": -99.136566
      },
       ...
      "pip": [
      {
      "cuadrante": "C-1.4.4",
      "geomery": "{\"type\":\"MultiPolygon\",\"coordinates\":[[[[-99.129543,19.436234],[-99.12966,19.435347],[-99.129766,19.43449],[-99.12994,19.433287],[-99.130025,19.432576],[-99.130206,19.431322],[-99.130576,19.428702],[-99.132613,19.428972],[-99.136883,19.429561],[-99.136343,19.433343],[-99.136008,19.435295],[-99.135754,19.437014],[-99.13479,19.436886],[-99.133691,19.436745],[-99.131628,19.436484],[-99.129543,19.436234]]]]}",
      "sector": "CORREDOR - CENTRO"
      }
    """
    # sql_query = """SELECT ST_AsGeoJSON(geom) as geom,id,sector
    #                 FROM cuadrantes_poly
    #                 where ST_Contains(geom,ST_GeometryFromText('POINT(-99.13 19.43)',4326))=True;"""
    crime = crime.upper()
    start_date = request.args.get('start_date', '', type=str)
    end_date = request.args.get('end_date', '', type=str)
    start_date, max_date = check_dates(start_date, end_date)
    if crime == "ALL":
        filters = [and_(Crime_latlong.date >= start_date, Crime_latlong.date <= max_date)]
    else:
        filters = [or_(*[func.upper(Crime_latlong.crime) == x for x in crime.split(',')])]
        filters.append(and_(Crime_latlong.date >= start_date, Crime_latlong.date <= max_date))

    if distance <= 0:
        raise InvalidAPIUsage('distance has to be greater than zero')

    if not lib.check_float(long):
        raise InvalidAPIUsage('something is wrong with the longitude you provided')
        #abort(abort(make_response('something is wrong with the longitude you provided', 400)))
    if not lib.check_float(lat):
        raise InvalidAPIUsage('something is wrong with the latitude you provided')
        #abort(abort(make_response('something is wrong with the latitude you provided', 400)))

    point = WKTElement("POINT(%s %s)" % (long, lat), srid=4326)

    filters.append(func.ST_Distance_Sphere(point, Crime_latlong.geom) <= distance)

    results_sphere = Crime_latlong.query. \
        filter(*filters). \
        with_entities(func.upper(Crime_latlong.crime).label("crime"),
                      func.upper(Crime_latlong.date).label("date"),
                      func.upper(Crime_latlong.hour).label("hour"),
                      Crime_latlong.latitude.label("lat"),
                      Crime_latlong.longitude.label("long")). \
        order_by(Crime_latlong.crime.desc(), Crime_latlong.date.desc()). \
        all()


    return jsonify(latlong=lib.results_to_array(results_sphere, truncate_date=False))



@API.route('/df/crimes/<string:crime>/hours',
           methods=['GET'])
@jsonp
@cache.cached(key_prefix=make_cache_key)
def hours_df(crime):
    """Return the number of crimes by hour

    :param crime: the name of crime or the keyword ``all`` to return all crimes

    :status 200: when the sum of all crimes is found
    :status 404: when the crime is not found in the database

    :query start_date: Start of the period from which to start aggregating in ``%Y-%m`` format (e.g. 2013-01)
    :query end_date: End of the period to analyze in ``%Y-%m`` format (e.g. 2013-06). Must be greater or equal to start_date

    :resheader Content-Type: application/json

    **Example request**:

    .. sourcecode:: http

      GET /api/v1/df/crimes/ALL/hours HTTP/1.1
      Host: hoyodecrimen.com
      Accept: application/json

    **Example response (truncated)**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
      "rows": [
      {
      "count": 206,
      "crime": "HOMICIDIO DOLOSO",
      "end_date": "2016-09",
      "hour": "00",
      "start_date": "2015-10"
      },
      {
      "count": 231,
      "crime": "HOMICIDIO DOLOSO",
      "end_date": "2016-09",
      "hour": "01",
      "start_date": "2015-10"
      },
    ...

    """
    """SELECT substr(hour, 1, 2) as hour, count(c.crime) as count, c.crime
    FROM crime_latlong as c
    LEFT JOIN
    (SELECT max_hour, crime
    FROM
    (
       SELECT
         max_hour, crime,
         ROW_NUMBER() OVER (PARTITION BY crime ORDER BY count desc) as rn
       FROM
         (SELECT substr(hour, 1, 2) as max_hour, count(crime) as count, crime
         from crime_latlong
          GROUP BY substr(hour, 1, 2), crime
         ORDER BY crime ASC, substr(hour, 1, 2)) as counts
       ) t
    WHERE
       t.rn = 1) as p
    ON c.crime::text = p.crime::text
    GROUP BY substr(hour, 1, 2), c.crime, p.max_hour
    ORDER BY ((max_hour::integer + 5) % 24) ASC, c.crime, substr(hour, 1, 2);
    """
    crime = crime.upper()
    start_date = request.args.get('start_date', '', type=str)
    end_date = request.args.get('end_date', '', type=str)
    start_date, max_date = check_dates(start_date, end_date)
    if crime == "ALL":
        filters = [and_(Crime_latlong.date >= start_date, Crime_latlong.date <= max_date)]
    else:
        filters = [or_(*[func.upper(Crime_latlong.crime) == x for x in crime.split(',')])]
        filters.append(and_(Crime_latlong.date >= start_date, Crime_latlong.date <= max_date))
    subq = Crime_latlong.query \
        .filter(*filters) \
        .with_entities(func.substr(literal(start_date, type_=db.String), 0, 8).label('start_date'),
                      func.substr(literal(max_date, type_=db.String), 0, 8).label('end_date'),
                      func.substr(Crime_latlong.hour, 0, 3).label('max_hour'),
                      func.upper(Crime_latlong.crime).label('crime'),
                      func.count(Crime_latlong.crime).label('count')) \
        .group_by(func.substr(Crime_latlong.hour, 0, 3), Crime_latlong.crime) \
        .order_by(Crime_latlong.crime, func.substr(Crime_latlong.hour, 0, 3)) \
        .subquery()
    partition = Crime_latlong.query \
        .with_entities(subq.c.max_hour,
                       subq.c.crime,
                       subq.c.count,
                       func.row_number().over(partition_by=subq.c.crime, order_by=subq.c.count.desc()).label('rn')
                       ) \
        .subquery()
    max = Crime_latlong.query \
        .with_entities(partition.c.max_hour,
                       partition.c.crime
                       ) \
        .filter(partition.c.rn == 1) \
        .subquery()
    # all_crimes = Crime_latlong.query \
    #     .with_entities(func.upper(Crime_latlong.crime).label('crime')) \
    #     .distinct() \
    #     .subquery()
    #
    # cross_join = Crime_latlong.query \
    #     .join(all_crimes, literal(True)) \
    #     .with_entities(func.substr(literal(start_date, type_=db.String), 0, 8).label('start_date'),
    #                    func.substr(literal(max_date, type_=db.String), 0, 8).label('end_date'),
    #                    func.substr(Crime_latlong.hour, 0, 3).label('hour'),
    #                    literal("0", type_=db.String).label('count'),
    #                    all_crimes.c.crime) \
    #     .distinct() \
    #     .subquery()

    results = Crime_latlong.query \
        .join(max, Crime_latlong.crime == max.c.crime) \
        .filter(*filters) \
        .with_entities(func.substr(literal(start_date, type_=db.String), 0, 8).label('start_date'),
                      func.substr(literal(max_date, type_=db.String), 0, 8).label('end_date'),
                      func.substr(Crime_latlong.hour, 0, 3).label('hour'),
                      func.upper(Crime_latlong.crime).label('crime'),
                      func.count(Crime_latlong.crime).label('count')) \
        .group_by(func.substr(Crime_latlong.hour, 0, 3), Crime_latlong.crime, max.c.max_hour) \
        .order_by(func.mod(func.cast(max.c.max_hour, INTEGER) + 5, 24), Crime_latlong.crime, func.substr(Crime_latlong.hour, 0, 3)) \
        .all()

    # r = Crime_latlong.query \
    #     .join(cross_join, and_(results.c.crime == cross_join.c.crime, results.c.hour == cross_join.c.hour, results.c.count == None)) \
    #     .with_entities(func.substr(literal(start_date, type_=db.String), 0, 8).label('start_date'),
    #                   func.substr(literal(max_date, type_=db.String), 0, 8).label('end_date'),
    #                   func.substr(Crime_latlong.hour, 0, 3).label('hour'),
    #                   func.upper(Crime_latlong.crime).label('crime'),
    #                   func.count(Crime_latlong.crime).label('count')) \
    #     .filter() \
    #     .all()
    return lib.results_to_json(results)


@API.route('/df/crimes/<string:crime>/days',
           methods=['GET'])
@jsonp
@cache.cached(key_prefix=make_cache_key)
def days_df(crime):
    """Return the number of crimes by day

    :param crime: the name of crime or the keyword ``all`` to return all crimes

    :status 200: when the sum of all crimes is found
    :status 404: when the crime is not found in the database

    :query start_date: Start of the period from which to start aggregating in ``%Y-%m`` format (e.g. 2013-01)
    :query end_date: End of the period to analyze in ``%Y-%m`` format (e.g. 2013-06). Must be greater or equal to start_date

    :resheader Content-Type: application/json

    **Example request**:

    .. sourcecode:: http

      GET /api/v1/df/crimes/ALL/hours HTTP/1.1
      Host: hoyodecrimen.com
      Accept: application/json

    **Example response (truncated)**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
      "rows": [
      {
      "count": 201,
      "crime": "HOMICIDIO DOLOSO",
      "dow": 0,
      "end_date": "2016-09",
      "start_date": "2015-10"
      },
      {
      "count": 148,
      "crime": "HOMICIDIO DOLOSO",
      "dow": 1,
      "end_date": "2016-09",
      "start_date": "2015-10"
      },
    ...

    """
    """SELECT EXTRACT(DOW FROM to_date(date, 'YYYY-MM-DD')) as dow, count(c.crime) as count, c.crime
    FROM crime_latlong as c
    LEFT JOIN
    (SELECT dow, crime
    FROM
    (
       SELECT
         dow, crime,
         ROW_NUMBER() OVER (PARTITION BY crime ORDER BY count desc) as rn
       FROM
         (SELECT EXTRACT(DOW FROM to_date(date, 'YYYY-MM-DD')) as dow, count(crime) as count, crime
         from crime_latlong
          GROUP BY EXTRACT(DOW FROM to_date(date, 'YYYY-MM-DD')), crime
         ORDER BY crime ASC, EXTRACT(DOW FROM to_date(date, 'YYYY-MM-DD'))) as counts
       ) t
    WHERE
       t.rn = 1) as p
    ON c.crime::text = p.crime::text
    GROUP BY EXTRACT(DOW FROM to_date(date, 'YYYY-MM-DD')), c.crime, p.dow
    ORDER BY ((dow::integer + 1) % 7) ASC, c.crime, dow;
    """
    crime = crime.upper()
    start_date = request.args.get('start_date', '', type=str)
    end_date = request.args.get('end_date', '', type=str)
    start_date, max_date = check_dates(start_date, end_date)
    if crime == "ALL":
        filters = [and_(Crime_latlong.date >= start_date, Crime_latlong.date <= max_date)]
    else:
        filters = [or_(*[func.upper(Crime_latlong.crime) == x for x in crime.split(',')])]
        filters.append(and_(Crime_latlong.date >= start_date, Crime_latlong.date <= max_date))
    subq = Crime_latlong.query \
        .filter(*filters) \
        .with_entities(func.substr(literal(start_date, type_=db.String), 0, 8).label('start_date'),
                      func.substr(literal(max_date, type_=db.String), 0, 8).label('end_date'),
                      func.extract('dow', func.cast(Crime_latlong.date, DATE)).label('dow'),
                      func.upper(Crime_latlong.crime).label('crime'),
                      func.count(Crime_latlong.crime).label('count')) \
        .group_by(func.extract('dow', func.cast(Crime_latlong.date, DATE)), Crime_latlong.crime) \
        .order_by(Crime_latlong.crime, func.extract('dow', func.cast(Crime_latlong.date, DATE))) \
        .subquery()
    partition = Crime_latlong.query \
        .with_entities(subq.c.dow,
                       subq.c.crime,
                       subq.c.count,
                       func.row_number().over(partition_by=subq.c.crime, order_by=subq.c.count.desc()).label('rn')
                       ) \
        .subquery()
    max = Crime_latlong.query \
        .with_entities(partition.c.dow,
                       partition.c.crime
                       ) \
        .filter(partition.c.rn == 1) \
        .subquery()

    results = Crime_latlong.query \
        .join(max, Crime_latlong.crime == max.c.crime) \
        .filter(*filters) \
        .with_entities(func.substr(literal(start_date, type_=db.String), 0, 8).label('start_date'),
                      func.substr(literal(max_date, type_=db.String), 0, 8).label('end_date'),
                      func.cast(func.extract('dow', func.cast(Crime_latlong.date, DATE)), INTEGER).label('dow'),
                      func.upper(Crime_latlong.crime).label('crime'),
                      func.count(Crime_latlong.crime).label('count')) \
        .group_by(func.extract('dow', func.cast(Crime_latlong.date, DATE)), Crime_latlong.crime, max.c.dow) \
        .order_by(func.mod(func.cast(max.c.dow, INTEGER) + 1, 7), Crime_latlong.crime,
                  func.extract('dow', func.cast(Crime_latlong.date, DATE))) \
        .all()

    return lib.results_to_json(results)


@API.route('/df/crimes/<string:crime>/series',
           methods=['GET'])
@jsonp
@cache.cached(key_prefix=make_cache_key)
def df_all(crime):
    """Return the sum of crimes that occurred in the Federal District

    :param crime: the name of crime or the keyword ``all`` to return all crimes

    :status 200: when the sum of all crimes is found
    :status 404: when the crime is not found in the database

    :query start_date: Start of the period from which to start the series. ``%Y-%m`` format (e.g. 2013-01)
    :query end_date: End of the period to analyze in ``%Y-%m`` format (e.g. 2013-06). Must be greater or equal to start_date

    :resheader Content-Type: application/json


    **Example request**:

    .. sourcecode:: http

      GET /api/v1/df/crimes/violacion/series HTTP/1.1
      Host: hoyodecrimen.com
      Accept: application/json

    **Example response (truncated)**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
      "rows": [
      {
      "count": 64,
      "crime": "VIOLACION",
      "month": 1,
      "population": 8785874,
      "year": 2013
      },
      ...

    """
    crime = crime.upper()

    start_date = request.args.get('start_date', '', type=str)
    end_date = request.args.get('end_date', '', type=str)
    # Needs to default to 2013-01 when the series starts instead of a year ago
    start_date, max_date = check_dates(start_date, end_date, '2013-01-01')
    filters = process_crime(crime, start_date, max_date)
    # if crime == "ALL":
    #     filters = [and_(Cuadrantes.date >= start_date, Cuadrantes.date <= max_date),
    #                ]
    # else:
    #     filters = [and_(Cuadrantes.date >= start_date, Cuadrantes.date <= max_date),
    #                func.upper(Cuadrantes.crime) == crime]
    results = Cuadrantes.query. \
        filter(*filters). \
        with_entities(func.upper(Cuadrantes.crime).label('crime'),
                      Cuadrantes.date,
                      func.sum(Cuadrantes.count).label('count'),
                      func.sum(Cuadrantes.population).label('population')). \
        group_by(Cuadrantes.date, Cuadrantes.crime). \
        order_by(Cuadrantes.crime, Cuadrantes.date). \
        all()
    return lib.results_to_json(results)




@API.route('/cuadrantes/<string:cuadrante>'
           '/crimes/<string:crime>/'
           'series',
           methods=['GET'])
@jsonp
@cache.cached(key_prefix=make_cache_key)
def cuadrantes(cuadrante, crime):
    """Return the count of crimes that occurred in a cuadrante, by date

    :param crime: the name of crime or the keyword ``all`` to return all crimes
    :param cuadrante: the name of the cuadrante from which to return the time series or the keyword ``all to return all cuadrantes

    :status 200: when the sum of all crimes is found
    :status 404: when the crime or cuadrante is not found in the database

    :query start_date: Start of the period from which to start the series. ``%Y-%m`` format (e.g. 2013-01)
    :query end_date: End of the period to analyze in ``%Y-%m`` format (e.g. 2013-06). Must be greater or equal to start_date

    :resheader Content-Type: application/json

    **Example request**:

    .. sourcecode:: http

      GET /api/v1/cuadrantes/c-1.1.1/crimes/violacion/series HTTP/1.1
      Host: hoyodecrimen.com
      Accept: application/json

    **Example response (truncated)**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
      "rows": [
      {
      "count": 0,
      "crime": "HOMICIDIO DOLOSO",
      "cuadrante": "C-1.1.1",
      "month": 1,
      "population": 1594,
      "sector": "ANGEL - ZONA ROSA",
      "year": 2013
      },
      ...

    """
    cuadrante = cuadrante.upper()
    crime = crime.upper()

    start_date = request.args.get('start_date', '', type=str)
    end_date = request.args.get('end_date', '', type=str)
    # Needs to default to 2013-01 when the series starts instead of a year ago
    start_date, max_date = check_dates(start_date, end_date, '2013-01-01')
    filters = process_crime(crime, start_date, max_date, cuadrante = cuadrante)
    # if crime == "ALL":
    #     filters = [and_(Cuadrantes.date >= start_date, Cuadrantes.date <= max_date)]
    # else:
    #     filters = [and_(Cuadrantes.date >= start_date, Cuadrantes.date <= max_date),
    #                func.upper(Cuadrantes.crime) == crime]
    # if cuadrante != "ALL":
    #     filters.append(func.upper(Cuadrantes.cuadrante) == cuadrante)

    results = Cuadrantes.query. \
        filter(*filters). \
        with_entities(func.upper(Cuadrantes.cuadrante).label('cuadrante'),
                      func.upper(Cuadrantes.sector).label('sector'),
                      func.upper(Cuadrantes.crime).label('crime'),
                      Cuadrantes.date,
                      Cuadrantes.count,
                      Cuadrantes.population). \
        order_by(Cuadrantes.cuadrante, Cuadrantes.crime, Cuadrantes.date). \
        all()
    return lib.results_to_json(results)


@API.route('/sectores/<string:sector>'
           '/crimes/<string:crime>/'
           'series',
           methods=['GET'])
@jsonp
@cache.cached(key_prefix=make_cache_key)
def sectors(crime, sector):
    """Return the count of crimes that occurred in a sector, by date

    :param crime: the name of crime or the keyword ``all`` to return all crimes
    :param cuadrante: the name of the cuadrante from which to return the time series or the keyword ``all to return all sectores

    :status 200: when the sum of all crimes is found
    :status 404: when the crime or cuadrante is not found in the database

    :query start_date: Start of the period from which to start the series. ``%Y-%m`` format (e.g. 2013-01)
    :query end_date: End of the period to analyze in ``%Y-%m`` format (e.g. 2013-06). Must be greater or equal to start_date

    :resheader Content-Type: application/json

    **Example request**:

    .. sourcecode:: http

      GET /api/v1/sectores/angel%20-%20zona%20rosa/crimes/violacion/series HTTP/1.1
      Host: hoyodecrimen.com
      Accept: application/json

    **Example response (truncated)**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
      "rows": [
      {
      "count": 0,
      "crime": "HOMICIDIO DOLOSO",
      "month": 1,
      "population": 25606,
      "sector": "ANGEL - ZONA ROSA",
      "year": 2013
      },
      ...

    """
    sector = sector.upper()
    crime = crime.upper()
    start_date = request.args.get('start_date', '', type=str)
    end_date = request.args.get('end_date', '', type=str)
    start_date, max_date = check_dates(start_date, end_date, '2013-01-01')
    filters = process_crime(crime, start_date, max_date, sector = sector)
    # if crime == "ALL":
    #     filters = [and_(Cuadrantes.date >= start_date, Cuadrantes.date <= max_date)]
    # else:
    #     filters = [and_(Cuadrantes.date >= start_date, Cuadrantes.date <= max_date),
    #                func.upper(Cuadrantes.crime) == crime]
    # if sector != "ALL":
    #     filters.append(func.upper(Cuadrantes.sector) == sector)

    results = Cuadrantes.query. \
        filter(*filters). \
        with_entities(func.upper(Cuadrantes.sector).label('sector'),
                      func.upper(Cuadrantes.crime).label('crime'),
                      Cuadrantes.date,
                      func.sum(Cuadrantes.count).label('count'),
                      func.sum(Cuadrantes.population).label('population')). \
        group_by(Cuadrantes.crime, Cuadrantes.date, Cuadrantes.sector). \
        order_by(Cuadrantes.sector, Cuadrantes.crime, Cuadrantes.date). \
        all()
    return lib.results_to_json(results)


@API.route('/municipios/<string:municipio>'
           '/crimes/<string:crime>/'
           'series',
           methods=['GET'])
@jsonp
@cache.cached(key_prefix=make_cache_key)
def municipios_series(crime, municipio):
    """Return the count of crimes that occurred in a municipio, by date

    :param crime: the name of crime or the keyword ``all`` to return all crimes
    :param cuadrante: the name of the municipio from which to return the time series or the keyword ``all to return all municipios

    :status 200: when the sum of all crimes is found
    :status 404: when the crime or municipio is not found in the database

    :query start_date: Start of the period from which to start the series. ``%Y-%m`` format (e.g. 2013-01)
    :query end_date: End of the period to analyze in ``%Y-%m`` format (e.g. 2013-06). Must be greater or equal to start_date

    :resheader Content-Type: application/json

    **Example request**:

    .. sourcecode:: http

      GET /api/v1/municipios/tlalpan/crimes/homicidio%20doloso/series
      Host: hoyodecrimen.com
      Accept: application/json

    **Example response (truncated)**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
      "rows": [
      {
      "count": 1,
      "crime": "HOMICIDIO DOLOSO",
      "cve_mun": "09012",
      "date": "2013-01",
      "municipio": "TLALPAN",
      "population": 633181
      },
      ...

    """
    municipio = municipio.upper()
    crime = crime.upper()
    start_date = request.args.get('start_date', '', type=str)
    end_date = request.args.get('end_date', '', type=str)
    start_date, max_date = check_dates(start_date, end_date, '2013-01-01')
    filters = process_crime(crime, start_date, max_date, municipio = municipio)

    results = Cuadrantes.query.join(Municipios, Cuadrantes.cuadrante == Municipios.cuadrante). \
        filter(*filters). \
        with_entities(func.upper(Municipios.municipio).label('municipio'),
                      func.upper(Municipios.cvegeo).label('cve_mun'),
                      func.upper(Cuadrantes.crime).label('crime'),
                      Cuadrantes.date,
                      func.sum(Cuadrantes.count).label('count'),
                      func.sum(Cuadrantes.population).label('population')). \
        group_by(Cuadrantes.crime, Cuadrantes.date, Municipios.municipio, Municipios.cvegeo). \
        order_by(Municipios.municipio, Cuadrantes.crime, Cuadrantes.date). \
        all()
    return lib.results_to_json(results)


@API.route('/cuadrantes/<string:cuadrante>/crimes/<string:crime>/period',
           methods=['GET'])
@jsonp
@cache.cached(key_prefix=make_cache_key)
def cuadrantes_sum_all(cuadrante, crime):
    """Return the sum of crimes that occurred in each cuadrante for a specified period of time

    By default it returns the sum of crimes during the last 12 months for all the cuadrantes in the database

    :param crime: the name of crime or the keyword ``all`` to return all crimes
    :param cuadrante: the name of the cuadrante or the keyword ``all`` to return all cuadrantes

    :status 200: when the sum of all crimes is found
    :status 404: when the crime is not found in the database

    :query start_date: Start of the period from which to start aggregating in ``%Y-%m`` format (e.g. 2013-01)
    :query end_date: End of the period to analyze in ``%Y-%m`` format (e.g. 2013-06). Must be greater or equal to start_date

    :resheader Content-Type: application/json


    **Example request**:

    .. sourcecode:: http

      GET /api/v1/cuadrantes/all/crimes/all/period HTTP/1.1
      Host: hoyodecrimen.com
      Accept: application/json

    **Example response (truncated)**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
      "rows": [
      {
      "count": 0,
      "crime": "HOMICIDIO DOLOSO",
      "cuadrante": "C-1.1.1",
      "end_date": "2014-07",
      "population": 1594,
      "sector": "ANGEL - ZONA ROSA",
      "start_date": "2013-08"
      },
      ...

    """
    crime = crime.upper()
    cuadrante = cuadrante.upper()
    start_date = request.args.get('start_date', '', type=str)
    end_date = request.args.get('end_date', '', type=str)
    start_date, max_date = check_dates(start_date, end_date)
    filters = process_crime(crime, start_date, max_date, cuadrante = cuadrante)
    # if crime == "ALL":
    #     filters = [and_(Cuadrantes.date >= start_date, Cuadrantes.date <= max_date)]
    # else:
    #     filters = [and_(Cuadrantes.date >= start_date, Cuadrantes.date <= max_date),
    #                func.upper(Cuadrantes.crime) == crime]
    # if cuadrante != "ALL":
    #     filters.append(func.upper(Cuadrantes.cuadrante) == cuadrante)
    results = Cuadrantes.query. \
        filter(*filters). \
        with_entities(func.substr(literal(start_date, type_=db.String), 0, 8).label('start_date'),
                      func.substr(literal(max_date, type_=db.String), 0, 8).label('end_date'),
                      func.upper(Cuadrantes.cuadrante).label('cuadrante'),
                      func.upper(Cuadrantes.sector).label('sector'),
                      func.upper(Cuadrantes.crime).label('crime'),
                      func.sum(Cuadrantes.count).label("count"),
                      func.sum(Cuadrantes.population).op("/")(lib.month_diff(max_date, start_date)).label("population")) \
        .group_by(Cuadrantes.crime, Cuadrantes.sector, Cuadrantes.cuadrante) \
        .order_by(Cuadrantes.crime, Cuadrantes.cuadrante) \
        .all()
    return lib.results_to_json(results)


@API.route('/sectores/<string:sector>/crimes/<string:crime>/period',
           methods=['GET'])
@jsonp
@cache.cached(key_prefix=make_cache_key)
def sectores_sum_all(sector, crime):
    """Return the sum of crimes that occurred in a particular or in all sectores for a specified period of time

    By default it returns the sum of crimes during the last 12 months for all the sectores in the database

    :param crime: the name of crime or the keyword ``all`` to return all crimes
    :param sector: the name of the sector or the keyword ``all`` to return all sectores

    :status 200: when the sum of all crimes is found
    :status 404: when the crime is not found in the database

    :query start_date: Start of the period from which to start aggregating in ``%Y-%m`` format (e.g. 2013-01)
    :query end_date: End of the period to analyze in ``%Y-%m`` format (e.g. 2013-06). Must be greater or equal to start_date

    :resheader Content-Type: application/json

    **Example request**:

    .. sourcecode:: http

      GET /api/v1/sectores/all/crimes/all/period HTTP/1.1
      Host: hoyodecrimen.com
      Accept: application/json

    **Example response (truncated)**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
      "rows": [
      {
      "count": 26,
      "crime": "HOMICIDIO DOLOSO",
      "end_date": "2014-07",
      "population": 171047,
      "sector": "ABASTO-REFORMA",
      "start_date": "2013-08"
      },
      ...

    """
    crime = crime.upper()
    sector = sector.upper()
    start_date = request.args.get('start_date', '', type=str)
    end_date = request.args.get('end_date', '', type=str)
    start_date, max_date = check_dates(start_date, end_date)
    filters = process_crime(crime, start_date, max_date, sector = sector)
    # if crime == "ALL":
    #     filters = [and_(Cuadrantes.date >= start_date, Cuadrantes.date <= max_date)]
    # else:
    #     filters = [and_(Cuadrantes.date >= start_date, Cuadrantes.date <= max_date),
    #                func.upper(Cuadrantes.crime) == crime]
    # if sector != "ALL":
    #     filters.append(func.upper(Cuadrantes.sector) == sector)
    results = Cuadrantes.query. \
        filter(*filters). \
        with_entities(func.substr(literal(start_date, type_=db.String), 0, 8).label('start_date'),
                      func.substr(literal(max_date, type_=db.String), 0, 8).label('end_date'),
                      func.upper(Cuadrantes.sector).label('sector'),
                      func.upper(Cuadrantes.crime).label('crime'),
                      func.sum(Cuadrantes.count).label("count"),
                      func.sum(Cuadrantes.population).op("/")(lib.month_diff(max_date, start_date)).label("population")) \
        .group_by(Cuadrantes.crime, Cuadrantes.sector) \
        .order_by(Cuadrantes.crime, Cuadrantes.sector) \
        .all()
    return lib.results_to_json(results)


@API.route('/municipios/<string:municipio>/crimes/<string:crime>/period',
           methods=['GET'])
@jsonp
@cache.cached(key_prefix=make_cache_key)
def municipios_sum_all(municipio, crime):
    """Return the sum of crimes that occurred in each municipio for a specified period of time

    By default it returns the sum of crimes during the last 12 months for all the cuadrantes in the database

    :param crime: the name of crime or the keyword ``all`` to return all crimes
    :param municipio: the name of the municipio or the keyword ``all`` to return all municipios

    :status 200: when the sum of all crimes is found
    :status 404: when the crime or municipio is not found in the database

    :query start_date: Start of the period from which to start aggregating in ``%Y-%m`` format (e.g. 2013-01)
    :query end_date: End of the period to analyze in ``%Y-%m`` format (e.g. 2013-06). Must be greater or equal to start_date

    :resheader Content-Type: application/json


    **Example request**:

    .. sourcecode:: http

      GET /api/v1/municipios/tlalpan/crimes/all/period HTTP/1.1
      Host: hoyodecrimen.com
      Accept: application/json

    **Example response (truncated)**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
      "rows": [
      {
      "count": 0,
      "crime": "HOMICIDIO DOLOSO",
      "cuadrante": "C-1.1.1",
      "end_date": "2014-07",
      "population": 1594,
      "sector": "ANGEL - ZONA ROSA",
      "start_date": "2013-08"
      },
      ...

    """
    crime = crime.upper()
    municipio = municipio.upper()
    start_date = request.args.get('start_date', '', type=str)
    end_date = request.args.get('end_date', '', type=str)
    start_date, max_date = check_dates(start_date, end_date)
    filters = process_crime(crime, start_date, max_date, municipio = municipio)
    # if crime == "ALL":
    #     filters = [and_(Cuadrantes.date >= start_date, Cuadrantes.date <= max_date)]
    # else:
    #     filters = [and_(Cuadrantes.date >= start_date, Cuadrantes.date <= max_date),
    #                func.upper(Cuadrantes.crime) == crime]
    # if municipio != "ALL":
    #     filters.append(func.upper(Municipios.municipio) == municipio)
    results = Cuadrantes.query.join(Municipios, Cuadrantes.cuadrante == Municipios.cuadrante). \
        filter(*filters). \
        with_entities(func.substr(literal(start_date, type_=db.String), 0, 8).label('start_date'),
                      func.substr(literal(max_date, type_=db.String), 0, 8).label('end_date'),
                      func.upper(Cuadrantes.crime).label('crime'),
                      func.upper(Municipios.municipio).label('municipio'),
                      func.upper(Municipios.cvegeo).label('cve_mun'),
                      func.sum(Cuadrantes.count).label("count"),
                      func.sum(Cuadrantes.population).op("/")(lib.month_diff(max_date, start_date)).label("population")) \
        .group_by(Cuadrantes.crime, Municipios.municipio, Municipios.cvegeo) \
        .order_by(Cuadrantes.crime, Municipios.municipio) \
        .all()
    return lib.results_to_json(results)


@API.route('/cuadrantes/<string:cuadrante>/crimes/<string:crime>/period/change',
           methods=['GET'])
@jsonp
@cache.cached(key_prefix=make_cache_key)
def cuadrantes_change_sum_all(cuadrante, crime):
    """Return the change in crime counts for a specified period of time at the cuadrante level

    By default it returns the sum of crimes during the last 12 months

    :param crime: the name of crime or the keyword ``all`` to return all crimes
    :param cuadrante: the name of the cuadrante or the keyword ``all`` to return all cuadrantes

    :status 200: when the  change in crime counts is found
    :status 404: when the crime is not found in the database

    :query start_period1: Start of the period from which to start counting. Together with end_period1 this will specify the first period. Formatted as ``%Y-%m`` (e.g. 2013-01)
    :query end_period1: End of the first period. Formatted as ``%Y-%m`` (e.g. 2013-01)
    :query start_period2: Start of the period from which to start counting. Together with end_period2 this will specify the second period. Formatted as ``%Y-%m`` (e.g. 2013-01)
    :query end_period2: End of the second period. Formatted as ``%Y-%m`` (e.g. 2013-01)

    :resheader Content-Type: application/json

    **Example request**:

    .. sourcecode:: http

      GET /api/v1/cuadrantes/all/crimes/all/period/change HTTP/1.1
      Host: hoyodecrimen.com
      Accept: application/json

    **Example response (truncated)**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
      "rows": [
      {
      "crime": "HOMICIDIO DOLOSO",
      "cuadrante": "O-2.2.9",
      "difference": 5,
      "end_period1": "2013-07",
      "end_period2": "2014-07",
      "period1_count": 0,
      "period2_count": 5,
      "population": 43116,
      "sector": "QUETZAL",
      "start_period1": "2013-05",
      "start_period2": "2014-05"
      },
      ...

    """
    crime = crime.upper()
    cuadrante = cuadrante.upper()
    start_period1 = request.args.get('start_period1', '', type=str)
    start_period2 = request.args.get('start_period2', '', type=str)
    end_period1 = request.args.get('end_period1', '', type=str)
    end_period2 = request.args.get('end_period2', '', type=str)
    max_date, max_date_minus3, max_date_last_year, max_date_last_year_minus3 = lib.check_periods(start_period1,
                                                                                             start_period2,
                                                                                             end_period1,
                                                                                             end_period2)
    sql_query1 = """select upper(crime) as crime, upper(cuadrante) as cuadrante,
                               upper(sector) as sector, max(population) as population,
                               substring(CAST(:max_date_minus3 AS text) for 7) as start_period2,
                               substring(CAST(:max_date AS text) for 7) as end_period2,
                               substring(CAST(:max_date_last_year AS text) for 7) as end_period1,
                               substring(CAST(:max_date_last_year_minus3 AS text) for 7) as start_period1,
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
    sql_query2 = "" if crime == "ALL" else 'WHERE ' + ' OR '.join([ 'upper(crime) = :crime' + str(x) for x in range(len(crime.split(',')))])
    sql_query3 = "" if cuadrante == "ALL" else " where upper(cuadrante) = :cuadrante "
    sql_query4 = """ group by cuadrante, sector, crime
                        order by crime asc, cuadrante asc """
    crime_data = { 'crime'+str(x) : crime.split(',')[x-1] for x in range(len(crime.split(',')))}
    crime_data.update(
                                  {'max_date': max_date,
                                 'max_date_minus3': max_date_minus3,
                                 'max_date_last_year': max_date_last_year,
                                 'max_date_last_year_minus3': max_date_last_year_minus3,
                                 'cuadrante': cuadrante})
    #import pdb; pdb.set_trace()
    results = db.session.execute(sql_query1 + sql_query2 + sql_query3 + sql_query4,
                                  crime_data)
    return lib.ResultProxy_to_json(results)


@API.route('/crimes',
           methods=['GET'])
@jsonp
@cache.cached(key_prefix=make_cache_key)
def listcrimes():
    """Enumerate all the crimes in the database

   :status 200: when all the crimes were found

   :resheader Content-Type: application/json

   **Example request**:

   .. sourcecode:: http

      GET /api/v1/crimes HTTP/1.1
      Host: hoyodecrimen.com
      Accept: application/json

   **Example response (truncated)**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
      "rows": [
      {
      "crime": "HOMICIDIO DOLOSO"
      },
      {
      "crime": "ROBO A NEGOCIO C.V."
      },
      {
      "crime": "ROBO DE VEHICULO AUTOMOTOR C.V."
      }
      ...
   """
    results = Cuadrantes.query. \
        with_entities(func.upper(Cuadrantes.crime).label('crime')). \
        order_by(Cuadrantes.crime). \
        distinct(). \
        all()
    return lib.results_to_json(results)


@API.route('/cuadrantes',
           methods=['GET'])
@jsonp
@cache.cached(key_prefix=make_cache_key)
def listcuadrantes():
    """Enumerate all the cuadrantes and the sectors and municipios they belong to

    :status 200: when all the cuadrantes were found

    :resheader Content-Type: application/json

    **Example request**:

    .. sourcecode:: http

       GET /api/v1/cuadrantes HTTP/1.1
       Host: hoyodecrimen.com
       Accept: application/json

    **Example response (truncated)**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
      "rows": [
      {
      "cuadrante": "P-1.1.1",
      "cve_mun": "09010",
      "municipio": "ALVARO OBREGON",
      "sector": "ALPES"
      },
      ...
    """
    results = Municipios.query. \
        with_entities(func.upper(Municipios.sector).label('sector'),
                      func.upper(Municipios.cuadrante).label('cuadrante'),
                      func.upper(Municipios.municipio).label('municipio'),
                      func.upper(Municipios.cvegeo).label('cve_mun')). \
        order_by(Municipios.municipio, Municipios.sector, Municipios.cuadrante). \
        distinct(). \
        all()
    return lib.results_to_json(results)


@API.route('/sectores',
           methods=['GET'])
@jsonp
@cache.cached(key_prefix=make_cache_key)
def listsectores():
    """Enumerate all the sectores in the database

    :status 200: when all the sectores were found

    :resheader Content-Type: application/json

    **Example request**:

    .. sourcecode:: http

      GET /api/v1/sectores HTTP/1.1
      Host: hoyodecrimen.com
      Accept: application/json

    **Example response (truncated)**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
      "rows": [
      {
      "cve_mun": "09010",
      "municipio": "ALVARO OBREGON",
      "sector": "ALPES"
      },
      ...
    """

    results = Municipios.query. \
        with_entities(func.upper(Municipios.sector).label('sector'),
                      func.upper(Municipios.municipio).label('municipio'),
                      func.upper(Municipios.cvegeo).label('cve_mun')). \
        order_by(Municipios.municipio, Municipios.sector). \
        distinct(). \
        all()
    return lib.results_to_json(results)


@API.route('/municipios',
           methods=['GET'])
@jsonp
@cache.cached(key_prefix=make_cache_key)
def list_municipios():
    """Enumerate all municipios in the Federal District

    :status 200: when all the municipios were found

    :resheader Content-Type: application/json

    **Example request**:

    .. sourcecode:: http

       GET /api/v1/municipios HTTP/1.1
       Host: hoyodecrimen.com
       Accept: application/json

    **Example response (truncated)**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json
      {
      "rows": [
      {
      "cuadrante": "P-1.1.1",
      "cve_mun": "09010",
      "municipio": "ALVARO OBREGON",
      "sector": "ALPES"
      },
      ...
    """
    results = Municipios.query. \
        with_entities(func.upper(Municipios.sector).label('sector'),
                      func.upper(Municipios.cuadrante).label('cuadrante'),
                      func.upper(Municipios.municipio).label('municipio'),
                      func.upper(Municipios.cvegeo).label('cve_mun')). \
        order_by(Municipios.municipio, Municipios.sector, Municipios.cuadrante). \
        distinct(). \
        all()
    return lib.results_to_json(results)

@API.route('/cuadrantes/crimes/<string:crime>/top/counts',
           methods=['GET'])
@jsonp
@cache.cached(key_prefix=make_cache_key)
def top5cuadrantes(crime):
    """Return the top ranked cuadrantes with the highest crime **counts** for a given period of time.

    When no dates parameters are specified the top 5 cuadrantes for the last 12 months are returned
    (e.g. If July is the last date in the database, then the period July 2014 to Aug 2013 will be analyzed).
    All population data returned by this call is in persons/year and comes from the 2010 census

    :param crime: the name of a crime or the keyword ``all``

    :status 200: when the top 5 cuadrantes are found
    :status 400: when the one of the dates was incorrectly specified or the periods overlap
    :status 404: when the crime is not found in the database

    :query start_date: Start of the period from which to start counting. Formatted as ``%Y-%m`` (e.g. 2013-01)
    :query end_date: End of the period to analyze. Must be greater or equal to start_date. Formatted as ``%Y-%m`` (e.g. 2013-01)
    :query rank: Return all cuadrantes ranked higher. Defaults to `5`

    :resheader Content-Type: application/json

    **Example request**:

    .. sourcecode:: http

      GET /api/v1/cuadrantes/crimes/homicidio%20doloso/top/counts HTTP/1.1
      Host: hoyodecrimen.com
      Accept: application/json

    **Example response (truncated)**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json
      {
      "rows": [
      {
      "count": 12,
      "crime": "HOMICIDIO DOLOSO",
      "cuadrante": "N-2.2.1",
      "end_date": "2014-07",
      "population": 1833,
      "rank": 1,
      "sector": "CUCHILLA",
      "start_date": "2013-08"
      },
      ...

    """
    crime = crime.upper()
    start_date = request.args.get('start_date', '', type=str)
    end_date = request.args.get('end_date', '', type=str)
    start_date, max_date = check_dates(start_date, end_date)
    rank = request.args.get('rank', 5, type=int)
    if rank <= 0:
        raise InvalidAPIUsage('Rank must be greater than zero')
        #abort(abort(make_response('No negative numbers', 400)))
    sql_query = """with crimes as
                          (select sum(count) as count,sector,cuadrante,max(population)as population, crime
                          from cuadrantes
                          where date >= :start_date and date <= :max_date"""
    sql_query2 = "" if crime == "ALL" else  ' AND ' + ' OR '.join([ 'upper(crime) = :crime' + str(x) for x in range(len(crime.split(',')))])
    sql_query3 = """
                          group by cuadrante, sector, crime)
                       SELECT *
                       from
                          (SELECT substring(CAST(:start_date AS text) for 7) as start_period,
                                  substring(CAST(:max_date AS text) for 7) as end_period, count,upper(crime) as crime,
                                  upper(sector) as sector,upper(cuadrante) as cuadrante,
                                  rank() over (partition by crime order by count desc) as rank,population
                          from crimes group by count,crime,sector,cuadrante,population) as temp2
                          where rank <= :rank
                          order by crime, rank, cuadrante, sector asc"""
    crime_data = { 'crime'+str(x) : crime.split(',')[x-1] for x in range(len(crime.split(',')))}
    crime_data.update({'start_date': start_date,
                                                                       'max_date': max_date,
                                                                       'crime': crime,
                                                                       'rank': rank})
    results = db.session.execute(sql_query + sql_query2 + sql_query3, crime_data)
    return lib.ResultProxy_to_json(results)


# @API.route('/municipios/crimes/<string:crime>/top/counts',
#            methods=['GET'])
# @jsonp
# @cache.cached(key_prefix=make_cache_key)
# def top5municipios(crime):
#     """Return the top ranked cuadrantes with the highest crime **counts** for a given period of time.

#     When no dates parameters are specified the top 5 cuadrantes for the last 12 months are returned
#     (e.g. If July is the last date in the database, then the period July 2014 to Aug 2013 will be analyzed).
#     All population data returned by this call is in persons/year and comes from the 2010 census

#     :param crime: the name of a crime or the keyword ``all``

#     :status 200: when the top 5 cuadrantes are found
#     :status 400: when the one of the dates was incorrectly specified or the periods overlap
#     :status 404: when the crime is not found in the database

#     :query start_date: Start of the period from which to start counting. Formatted as ``%Y-%m`` (e.g. 2013-01)
#     :query end_date: End of the period to analyze. Must be greater or equal to start_date. Formatted as ``%Y-%m`` (e.g. 2013-01)
#     :query rank: Return all cuadrantes ranked higher. Defaults to `5`

#     :resheader Content-Type: application/json

#     **Example request**:

#     .. sourcecode:: http

#       GET /api/v1/municipios/crimes/homicidio%20doloso/top/counts HTTP/1.1
#       Host: hoyodecrimen.com
#       Accept: application/json

#     **Example response (truncated)**:

#     .. sourcecode:: http

#       HTTP/1.1 200 OK
#       Content-Type: application/json
#       {
#       "rows": [
#       {
#       "count": 12,
#       "crime": "HOMICIDIO DOLOSO",
#       "cuadrante": "N-2.2.1",
#       "end_date": "2014-07",
#       "population": 1833,
#       "rank": 1,
#       "sector": "CUCHILLA",
#       "start_date": "2013-08"
#       },
#       ...

#     """
#     crime = crime.upper()
#     start_date = request.args.get('start_date', '', type=str)
#     end_date = request.args.get('end_date', '', type=str)
#     start_date, max_date = check_dates(start_date, end_date)
#     rank = request.args.get('rank', 5, type=int)
#     if rank <= 0:
#         raise InvalidAPIUsage('Rank must be greater than zero')
#         #abort(abort(make_response('No negative numbers', 400)))
#     sql_query = """with crimes as
#                            (select (sum(c.count) / (sum(c.population::float) / :num_months )* 100000) as rate,sum(c.count) as count,
#                            c.sector,sum(c.population) / :num_months as population, c.crime
#                            from cuadrantes as c
#                            INNER JOIN municipios as m
#                            ON c.cuadrante=m.cuadrante
#                            where date >= :start_date and date <= :max_date and population is not null"""
#     sql_query2 = "" if crime == "ALL" else " and upper(crime) = :crime "
#     sql_query3 = """   group by m.municipio, crime)
#                        SELECT substring(CAST(start_period as text) for 7) as start_date, substring(end_period::text for 7) as end_date,
#                                round(rate::numeric , 1)::float as rate, crime, sector, count, rank, population from
#                            (SELECT :start_date as start_period, :max_date as end_period, count, rate,
#                                    upper(crime) as crime,
#                                    upper(sector) as sector,
#                                    rank() over (partition by crime order by rate desc) as rank,population
#                             from crimes
#                             group by count,crime,sector,population, rate) as temp2
#                            where rank <= :rank """
#     results = db.session.execute(sql_query + sql_query2 + sql_query3, {'start_date': start_date,
#                                                                        'max_date': max_date,
#                                                                        'crime': crime,
#                                                                        'num_months': lib.month_diff(max_date, start_date),
#                                                                        'rank': rank})
#     return lib.ResultProxy_to_json(results)


@API.route('/sectores/crimes/<string:crime>/top/rates',
           methods=['GET'])
@jsonp
@cache.cached(key_prefix=make_cache_key)
def top5sectores(crime):
    """Return the top ranked sectors with the highest crime **rates** for a given period of time.

    When no date parameters are specified the top 5 cuadrantes are returned for the last 12 months
    (e.g. If July is the last date in the database then the period July 2014 to Aug 2013 will be analyzed).
    Crimes where no sector was specified (NO ESPECIFICADO) are ignored.
    All population data returned by this call is in persons/year and comes from the 2010 census

    :param crime: the name of a crime or the keyword ``all``

    :status 200: when the top 5 cuadrantes are found
    :status 400: when the one of the dates was incorrectly specified or the periods overlap
    :status 404: when the crime is not found in the database

    :query start_date: Start of the period from which to start counting. Formatted as ``%Y-%m`` (e.g. 2013-01)
    :query end_date: End of the period to analyze. Must be greater or equal to start_date. Formatted as ``%Y-%m`` (e.g. 2013-01)
    :query rank: Return all sectores with a rate ranked higher. Defaults to `5`

    :resheader Content-Type: application/json

    **Example request**:

    .. sourcecode:: http

      GET /api/v1/sectores/crimes/homicidio%20doloso/top/rates HTTP/1.1
      Host: hoyodecrimen.com
      Accept: application/json

    **Example response (truncated)**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
      "rows": [
      {
      "count": 22,
      "crime": "HOMICIDIO DOLOSO",
      "end_date": "2014-07",
      "population": 33787,
      "rank": 1,
      "rate": 65.1,
      "sector": "CONGRESO",
      "start_date": "2013-08"
      },
      ...

    """
    crime = crime.upper()
    start_date = request.args.get('start_date', '', type=str)
    end_date = request.args.get('end_date', '', type=str)
    start_date, max_date = check_dates(start_date, end_date)
    rank = request.args.get('rank', 5, type=int)
    if rank <= 0:
        raise InvalidAPIUsage('Rank must be greater than zero')
        # abort(abort(make_response('No negative numbers', 400)))
    sql_query = """with crimes as
                           (select (sum(count) / (nullif(sum(population::float), 0) / :num_months )* 100000) as rate,sum(count) as count,
                           sector,sum(population) / :num_months as population, crime
                           from cuadrantes
                           where date >= :start_date and date <= :max_date and population is not null"""
    sql_query2 = "" if crime == "ALL" else ' AND ' + ' OR '.join(
        ['upper(crime) = :crime' + str(x) for x in range(len(crime.split(',')))])
    sql_query3 = """   group by sector, crime)
                       SELECT substring(CAST(start_period as text) for 7) as start_date, substring(end_period::text for 7) as end_date,
                               round(rate::numeric , 1)::float as rate, crime, sector, count, rank, population from
                           (SELECT :start_date as start_period, :max_date as end_period, count, rate,
                                   upper(crime) as crime,
                                   upper(sector) as sector,
                                   rank() over (partition by crime order by rate desc) as rank,population
                           from crimes
                           group by count,crime,sector,population, rate) as temp2
                           where rank <= :rank """
    crime_data = {'crime' + str(x): crime.split(',')[x - 1] for x in range(len(crime.split(',')))}
    crime_data.update({'start_date': start_date,
                       'max_date': max_date,
                       'crime': crime,
                       'num_months': lib.month_diff(max_date, start_date),
                       'rank': rank})
    results = db.session.execute(sql_query + sql_query2 + sql_query3, crime_data)
    return lib.ResultProxy_to_json(results)


@API.route('/cuadrantes/crimes/<string:crime>/top/counts/change',
           methods=['GET'])
@jsonp
@cache.cached(key_prefix=make_cache_key)
def top5changecuadrantes(crime):
    """Return the top ranked cuadrantes where crime **counts** increased the most.

    When no date parameters are specified the top 5 cuadrantes are returned for the last 3 months compared
    with the same period during the previous year (e.g. July-May 2014 compared with July-May 2013).
    All population data returned by this call is in persons/year and comes from the 2010 census

    :param crime: the name of a crime or the keyword ``all``

    :status 200: when the top 5 cuadrantes are found
    :status 400: when the one of the dates was incorrectly specified or the periods overlap
    :status 404: when the crime is not found in the database

    :query start_period1: Start of the period from which to start counting. Together with end_period1 this will specify the first period. Formatted as ``%Y-%m`` (e.g. 2013-01)
    :query end_period1: End of the first period. Formatted as ``%Y-%m`` (e.g. 2013-01)
    :query start_period2: Start of the period from which to start counting. Together with end_period2 this will specify the second period. Formatted as ``%Y-%m`` (e.g. 2013-01)
    :query end_period2: End of the second period. Formatted as ``%Y-%m`` (e.g. 2013-01)
    :query rank: Return the top X ranked cuadrantes.

    :resheader Content-Type: application/json

    **Example request**:

    .. sourcecode:: http

       GET /api/v1/cuadrantes/crimes/homicidio%20doloso/top/counts/change HTTP/1.1
       Host: hoyodecrimen.com
       Accept: application/json

    **Example response (truncated)**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
      "rows": [
      {
      "crime": "HOMICIDIO DOLOSO",
      "cuadrante": "O-2.2.9",
      "difference": 5,
      "end_period1": "2013-07",
      "end_period2": "2014-07",
      "period1_count": 0,
      "period2_count": 5,
      "population": 43116,
      "rank": 1,
      "sector": "QUETZAL",
      "start_period1": "2013-05",
      "start_period2": "2014-05"
      },
      ...

    """
    crime = crime.upper()
    start_period1 = request.args.get('start_period1', '', type=str)
    start_period2 = request.args.get('start_period2', '', type=str)
    end_period1 = request.args.get('end_period1', '', type=str)
    end_period2 = request.args.get('end_period2', '', type=str)
    rank = request.args.get('rank', 5, type=int)
    if rank <= 0:
        raise InvalidAPIUsage('Rank must be greater than zero')
    max_date, max_date_minus3, max_date_last_year, max_date_last_year_minus3 = lib.check_periods(start_period1,
                                                                                             start_period2,
                                                                                             end_period1,
                                                                                             end_period2)
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
    sql_query2 = "" if crime == "ALL" else  'WHERE ' + ' OR '.join([ 'upper(crime) = :crime' + str(x) for x in range(len(crime.split(',')))])
    sql_query3 = """
                                            group by cuadrante, sector, crime)
                                        SELECT *
                                        from (
                                            SELECT substring(CAST(:max_date as text) for 7) as end_period2,
                                                   substring(CAST(:max_date_minus3 as text) for 7) as start_period2,
                                                   substring(CAST(:max_date_last_year as text) for 7) as end_period1,
                                                   substring(CAST(:max_date_last_year_minus3 as text) for 7) as start_period1,
                                                   rank() over (partition by crime order by difference desc) as rank,
                                                   upper(crime) as crime, upper(cuadrante) as cuadrante,
                                                   upper(sector) as sector,population, period1_count, period2_count,
                                                   difference from difference
                                            group by difference,crime,sector,cuadrante, population,  period1_count, period2_count)
                                        as temp
                                        where rank <= :rank
                                        order by crime, rank, cuadrante, sector asc"""
    crime_data = {'crime' + str(x): crime.split(',')[x - 1] for x in range(len(crime.split(',')))}
    crime_data.update( {'max_date': max_date,
                                                                        'max_date_minus3': max_date_minus3,
                                                                        'max_date_last_year': max_date_last_year,
                                                                        'max_date_last_year_minus3': max_date_last_year_minus3,
                                                                        'crime': crime,
                                                                        'rank': rank})
    results = db.session.execute(sql_query1 + sql_query2 + sql_query3, crime_data)
    return lib.ResultProxy_to_json(results)
