#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from hoyodecrimen import app
import json
import unittest

#import tempfile

class FlaskTestCase(unittest.TestCase):
    # Check that the API is generating json and responding, even if it's crap
    # def test_calderas(self):
#         tester = app.test_client(self)
#         response = tester.get('/api/v1/estariamosmejorcon',
# content_type='application/json')
#         self.assertEqual(response.status_code, 200)
#         # Check that the result sent is the hero of all Mexico
#         self.assertEqual(json.loads(response.data.decode('utf-8')), {"rows": ["Calderon"]})

    # Check the API endpoint
    def test_api_v1_top_counts_change_cuadrantes(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/cuadrantes/crimes/homicidio%20doloso/top/counts/change',
                              content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data.decode('utf-8')), {"rows": []})

    # Check that the API correctly deals with date parameters
    def test_error_api_v1_top_counts_change_cuadrantes_dates(self):
        base_url = '/api/v1/cuadrantes/crimes/homicidio%20doloso/top/counts/change'
        tester = app.test_client(self)
        response = tester.get(base_url + '?start_period1=2013-01&end_period1=2013-12&start_period2=2014-01&end_period2=2014-06', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # Invalid dates or dates before 2013-01
        response = tester.get(base_url + '?start_period1=2005-19', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response = tester.get(base_url + '?start_period2=2005-19', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response = tester.get(base_url + '?end_period1=2005-19', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response = tester.get(base_url + '?end_period2=2005-19', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response = tester.get(base_url + '?start_period1=2005-19', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response = tester.get(base_url + '?start_period1=2015-12', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        # test with all dates specified
        response = tester.get(base_url + '?start_period1=2005-19&end_period1=2005-19&start_period2=2005-19&end_period2=2005-19', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        # Overlapping periods
        response = tester.get(base_url + '?start_period1=2016-01&end_period1=2016-06&start_period2=2013-03&end_period2=2014-02', content_type='application/json')
        # 1sr period invalid
        response = tester.get(base_url + '?start_period1=2016-06&end_period1=2016-01&start_period2=2013-03&end_period2=2014-02', content_type='application/json')
        self.assertEqual(response.status_code, 400)

    # Check that the API correctly deals with date parameters
    def test_top_rates_sectores(self):
        base_url = '/api/v1/sectores/crimes/homicidio%20doloso/top/rates'
        tester = app.test_client(self)
        response = tester.get(base_url + '?start_date=2016-08&end_date=2017-07', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # End date is smaller than start date
        response = tester.get(base_url + '?start_date=2014-08&end_date=2013-07', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        # Start date is smaller than 2013 (when the data started being collected)
        response = tester.get(base_url + '?start_date=2012-08&end_date=2013-07', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        # Equal dates are allowed since it would only span that month
        response = tester.get(base_url + '?start_date=2016-07&end_date=2016-07', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data.decode('utf-8')), {"rows": []})

    # Check that the API correctly deals with date parameters
    def test_top_counts_cuadrantes(self):
        base_url = '/api/v1/cuadrantes/crimes/homicidio%20doloso/top/counts'
        tester = app.test_client(self)
        response = tester.get(base_url + '?start_date=2016-08&end_date=2017-07', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # End date is smaller than start date
        response = tester.get(base_url + '?start_date=2014-08&end_date=2013-07', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        # Start date is smaller than 2013 (when the data started being collected)
        response = tester.get(base_url + '?start_date=2012-08&end_date=2013-07', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        # Equal dates are allowed since it would only span that month
        response = tester.get(base_url + '?start_date=2016-07&end_date=2016-07', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data.decode('utf-8')), {"rows": []})

    # Check the API endpoint
    def test_api_v1_enumerate_sectores(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/sectores', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data.decode('utf-8')), {"rows": []})

    # Check the API endpoint
    def test_api_v1_enumerate_cuadrantes(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/cuadrantes', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data.decode('utf-8')), {"rows": []})

    # Check the API endpoint
    def test_api_v1_enumerate_crimes(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/crimes', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data.decode('utf-8')), {"rows": []})

    # Check the API endpoint
    def test_api_v1_list_change_cuadrantes_all(self):
        base_url = '/api/v1/cuadrantes/all/crimes/all/period/change'
        tester = app.test_client(self)
        response = tester.get(base_url + '?start_period1=2013-01&end_period1=2013-12&start_period2=2014-01&end_period2=2014-06', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data.decode('utf-8')), {"rows": []})
        # Invalid dates or dates before 2013-01
        response = tester.get(base_url + '?start_period1=2005-19', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response = tester.get(base_url + '?start_period2=2005-19', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response = tester.get(base_url + '?end_period1=2005-19', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response = tester.get(base_url + '?end_period2=2005-19', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response = tester.get(base_url + '?start_period1=2005-19', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response = tester.get(base_url + '?start_period1=2012-12', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        # test with all dates specified
        response = tester.get(base_url + '?start_period1=2005-19&end_period1=2005-19&start_period2=2005-19&end_period2=2005-19', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        # Overlapping periods
        response = tester.get(base_url + '?start_period1=2013-01&end_period1=2013-06&start_period2=2013-03&end_period2=2014-02', content_type='application/json')
        # 1sr period invalid
        response = tester.get(base_url + '?start_period1=2013-06&end_period1=2013-01&start_period2=2013-03&end_period2=2014-02', content_type='application/json')
        self.assertEqual(response.status_code, 400)

    # Check the API endpoint
    def test_api_v1_list_sectores_all(self):
        base_url = '/api/v1/sectores/all/crimes/all/period'
        tester = app.test_client(self)
        response = tester.get(base_url, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # End date is smaller than start date
        response = tester.get(base_url + '?start_date=2014-08&end_date=2013-07', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        # Start date is smaller than 2013 (when the data started being collected)
        response = tester.get(base_url + '?start_date=2012-08&end_date=2013-07', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        # Equal dates are allowed since it would only span that month
        response = tester.get(base_url + '?start_date=2016-07&end_date=2016-07', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data.decode('utf-8')), {"rows": []})
        # Success
        response = tester.get(base_url + '?start_date=2016-01&end_date=2016-07', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data.decode('utf-8')), {"rows": []})

    # Check the API endpoint
    def test_api_v1_list_cuadrantes_all(self):
        base_url = '/api/v1/cuadrantes/all/crimes/all/period'
        tester = app.test_client(self)
        response = tester.get(base_url, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # End date is smaller than start date
        response = tester.get(base_url + '?start_date=2014-08&end_date=2013-07', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        # Start date is smaller than 2016 (when the data started being collected)
        response = tester.get(base_url + '?start_date=2012-08&end_date=2013-07', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        # Equal dates are allowed since it would only span that month
        response = tester.get(base_url + '?start_date=2016-07&end_date=2016-07', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data.decode('utf-8')), {"rows": []})
        # Success
        response = tester.get(base_url + '?start_date=2016-01&end_date=2016-07', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data.decode('utf-8')), {"rows": []})

    # Check the API endpoint
    def test_api_v1_series_sectores_a(self):
        base_url = '/api/v1/sectores/lindavista/crimes/violacion/series'
        tester = app.test_client(self)
        response = tester.get(base_url, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # End date is smaller than start date
        response = tester.get(base_url + '?start_date=2014-08&end_date=2013-07', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        # Start date is smaller than 2013 (when the data started being collected)
        response = tester.get(base_url + '?start_date=2012-08&end_date=2013-07', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        # Equal dates are allowed since it would only span that month
        response = tester.get(base_url + '?start_date=2016-07&end_date=2016-07', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data.decode('utf-8')), {"rows": []})
        # Success
        response = tester.get(base_url + '?start_date=2016-01&end_date=2016-07', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data.decode('utf-8')), {"rows": []})
        #response = tester.get('/api/v1/sector/angel%20-%20zona%20rosa/crimes/robo%20a%20negocio%20c.v./series', content_type='application/json')
        #self.assertEqual(response.status_code, 200)

    # Check the API endpoint
    def test_api_v1_series_cuadrantes_crimes(self):
        base_url = '/api/v1/cuadrantes/c-1.1.1/crimes/violacion/series'
        tester = app.test_client(self)
        response = tester.get(base_url, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # Equal dates are allowed since it would only span that month
        response = tester.get(base_url + '?start_date=2016-07&end_date=2016-07', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # Success
        response = tester.get(base_url + '?start_date=2016-01&end_date=2016-07', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data.decode('utf-8')), {"rows": []})

    # Check the API endpoint
    def test_df_crimes_series(self):
        base_url = '/api/v1/df/crimes/violacion/series'
        tester = app.test_client(self)
        response = tester.get(base_url, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # Equal dates are allowed since it would only span that month
        response = tester.get(base_url + '?start_date=2014-07&end_date=2014-07', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # Success
        response = tester.get(base_url + '?start_date=2014-01&end_date=2014-07', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data.decode('utf-8')), {"rows": []})


    # Check the API endpoint
    def test_api_v1_pip_extras_(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/cuadrantes/crimes/all/pip/-99.13333/19.43', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data.decode('utf-8')), {"rows": []})

    # Check the API endpoint
    def test_api_v1_pip(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/cuadrantes/pip/-99.13333/19.43', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data.decode('utf-8')), {"rows": []})

    # Check the API endpoint
    def test_api_v1_pip(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/latlong/crimes/ROBO%20A%20TRANSEUNTE%20C.V.,ROBO%20A%20TRANSEUNTE%20S.V.,ROBO%20A%20BORDO%20DE%20TAXI%20C.V.,ROBO%20A%20BORDO%20DE%20MICROBUS%20S.V.,ROBO%20A%20BORDO%20DE%20MICROBUS%20C.V.,ROBO%20A%20BORDO%20DE%20METRO%20S.V.,ROBO%20A%20BORDO%20DE%20METRO%20C.V./coords/-99.122815/19.506460/distance/50000000000?start_date=2016-01&end_date=2016-04', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data.decode('utf-8')), {"rows": []})

    # Check the API endpoint
    def test_api_v1_pip(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/cuadrantes/crimes/HOMICIDIO%20DOLOSO,LESIONES%20POR%20ARMA%20DE%20FUEGO,ROBO%20DE%20VEHICULO%20AUTOMOTOR%20S.V.,ROBO%20DE%20VEHICULO%20AUTOMOTOR%20C.V.,ROBO%20A%20TRANSEUNTE%20C.V./pip_extra/-99.133208/19.432605540309215', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data.decode('utf-8')), {"rows": []})

    def test_api_404(self):
        tester = app.test_client(self)
        response = tester.get('/adsflsdklfjaskljfkldsjfkjasklfjklsafsadfs', content_type='html/text')
        self.assertEqual(response.status_code, 404)

    def test_df_en_home(self):
        base_url = '/en/'
        tester = app.test_client(self)
        response = tester.get(base_url, content_type="text/html")
        self.assertEqual(response.status_code, 200)

    def test_df_crimes_series(self):
        base_url = '/en/rates'
        tester = app.test_client(self)
        response = tester.get(base_url, content_type="text/html")
        self.assertEqual(response.status_code, 200)

    def test_df_crimes_series(self):
        base_url = '/en/counts'
        tester = app.test_client(self)
        response = tester.get(base_url, content_type="text/html")
        self.assertEqual(response.status_code, 200)

    def test_df_crimes_series(self):
        base_url = '/en/trends'
        tester = app.test_client(self)
        response = tester.get(base_url, content_type="text/html")
        self.assertEqual(response.status_code, 200)

    def test_df_crimes_series(self):
        base_url = '/en/sectors-map'
        tester = app.test_client(self)
        response = tester.get(base_url, content_type="text/html")
        self.assertEqual(response.status_code, 200)

    def test_df_crimes_series(self):
        base_url = '/en/cuadrantes-map'
        tester = app.test_client(self)
        response = tester.get(base_url, content_type="text/html")
        self.assertEqual(response.status_code, 200)

    def test_df_en_home2(self):
        base_url = '/'
        tester = app.test_client(self)
        response = tester.get(base_url, content_type="text/html")
        self.assertEqual(response.status_code, 200)

    def test_df_crimes_series2(self):
        base_url = '/tasas'
        tester = app.test_client(self)
        response = tester.get(base_url, content_type="text/html")
        self.assertEqual(response.status_code, 200)

    def test_df_crimes_series2(self):
        base_url = '/numero'
        tester = app.test_client(self)
        response = tester.get(base_url, content_type="text/html")
        self.assertEqual(response.status_code, 200)

    def test_df_crimes_series2(self):
        base_url = '/tendencias'
        tester = app.test_client(self)
        response = tester.get(base_url, content_type="text/html")
        self.assertEqual(response.status_code, 200)

    def test_df_crimes_series2(self):
        base_url = '/sectors-mapa'
        tester = app.test_client(self)
        response = tester.get(base_url, content_type="text/html")
        self.assertEqual(response.status_code, 200)

    def test_df_crimes_series2(self):
        base_url = '/cuadrantes-mapa'
        tester = app.test_client(self)
        response = tester.get(base_url, content_type="text/html")
        self.assertEqual(response.status_code, 200)

    def test_df_api(self):
        base_url = '/api/'
        tester = app.test_client(self)
        response = tester.get(base_url, content_type="text/html")
        self.assertEqual(response.status_code, 200)

    def test_api_v1_geojson_cuadrantes(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/cuadrantes/geojson', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data.decode('utf-8')), {"rows": []})

    def test_api_v1_geojson_sectores(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/sectores/geojson', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data.decode('utf-8')), {"rows": []})

    def test_api_v1_geojson_municipios(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/municipios/geojson', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data.decode('utf-8')), {"rows": []})

    # def test_api_v1_mun_counts(self):
    #     tester = app.test_client(self)
    #     response = tester.get('/api/v1/municipios/crimes/homicidio%20doloso/top/counts', content_type='application/json')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertNotEqual(json.loads(response.data.decode('utf-8')), {"rows": []})

    def test_api_v1_mun_series(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/municipios/tlalpan/crimes/homicidio%20doloso/series', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data.decode('utf-8')), {"rows": []})

    def test_api_v1_mun_series(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/municipios', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data.decode('utf-8')), {"rows": []})

    def test_api_v1_crimes_extra(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/crimes_extra', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data.decode('utf-8')), {"rows": []})

    def test_api_v1_series_extra2(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/df/crimes/all/series_extra', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data.decode('utf-8')), {"rows": []})

    # Check that the cuadrantes polygons match the crime data
    def test_cuadrantes(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/cuadrantes', content_type='application/json')
        cuadrantes = tester.get('/api/v1/cuadrantes/geojson', content_type='application/json')
        for i in range(0, len(json.loads(cuadrantes.data.decode('utf-8'))['features'])):
            print(json.loads(cuadrantes.data.decode('utf-8'))['features'][i]['properties']['cuadrante'].encode('utf-8'))
            cuadrante = tester.get('/api/v1/cuadrantes/' +  json.loads(cuadrantes.data.decode('utf-8'))['features'][i]['properties']['cuadrante'] + '/crimes/homicidio%20doloso/series', content_type='application/json')
            self.assertEqual(cuadrante.status_code, 200)
            self.assertNotEqual(json.loads(cuadrante.data.decode('utf-8')), {"rows": []})

    # Check that the sectores polygons match the crime data
    def test_sectores(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/sectores/', content_type='application/json')
        cuadrantes = tester.get('/api/v1/sectores/geojson', content_type='application/json')
        for i in range(0, len(json.loads(cuadrantes.data.decode('utf-8'))['features'])):
            #print(json.loads(cuadrantes.data.decode('utf-8'))['features'][i]['properties']['sector'].encode('utf-8'))
            cuadrante = tester.get('/api/v1/sectores/' +  json.loads(cuadrantes.data.decode('utf-8'))['features'][i]['properties']['sector'] + '/crimes/homicidio%20doloso/series', content_type='application/json')
            self.assertEqual(cuadrante.status_code, 200)
            self.assertNotEqual(json.loads(cuadrante.data.decode('utf-8')), {"rows": []})


if __name__ == '__main__':
    unittest.main()
