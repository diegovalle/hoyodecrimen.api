from flask import jsonify
from models import db, Cuadrantes, Cuadrantes_Poly
from datetime import datetime
from sqlalchemy import func, and_
import time

class InvalidAPIUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.message
        return rv


def ResultProxy_to_json(results):
    json_results = []
    keys = results.keys()
    for result in results:
        d = {}
        for i, key in enumerate(keys):
            if key == "date":
                d["date"] = result[key][0:7]
                #d["month"] = int(result[key][5:7])
            else:
                d[key] = result[key]
        json_results.append(d)
    if not json_results:
        raise InvalidAPIUsage("not found", 404)
    return jsonify(rows=json_results)


def results_to_array(results, truncate_date=True):
    json_results = []
    if len(results) > 0:
        keys = results[0].keys()
        for result in results:
            d = {}
            for i, key in enumerate(keys):
                if key == "date":
                    if truncate_date == True:
                        d["date"] = result[i][0:7]
                    else:
                        d["date"] = result[i]
                    #d["month"] = int(result[i][5:7])
                else:
                    d[key] = result[i]
            json_results.append(d)
        return json_results
    else:
        raise InvalidAPIUsage('not found', 404)


def results_to_json(results):
    # response = jsonify({'code': 404,'message': 'No found'})
    # response.status_code = 404
    # return response
    return jsonify(rows=results_to_array(results))


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
        if str < '2013-01-01':
            valid = False
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


def check_periods(start_period1, start_period2, end_period1, end_period2):
    start_period1 += '-01'
    start_period2 += '-01'
    end_period1 += '-01'
    end_period2 += '-01'
    if end_period1 != '-01' or end_period2 != '-01' or \
                    start_period1 != '-01' or \
                    start_period2 != '-01':
        if not check_date_month(end_period1):
            raise InvalidAPIUsage('something is wrong with the '
                                  'end_period1 date you '
                                  'provided')
        if not check_date_month(end_period2):
            raise InvalidAPIUsage('something is wrong with the '
                                  'end_period2 date you '
                                  'provided')
        if not check_date_month(start_period1):
            raise InvalidAPIUsage('something is wrong with the '
                                  'start_period1 date you '
                                  'provided')
        if not check_date_month(start_period2):
            raise InvalidAPIUsage('something is wrong with the '
                                  'start_period2 date you '
                                  'provided')
        if end_period2 <= start_period2 or \
                        end_period1 <= start_period1 or \
                        start_period2 <= end_period1:
            raise InvalidAPIUsage('date order not valid')
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
    return max_date, max_date_minus3, \
           max_date_last_year, \
           max_date_last_year_minus3



