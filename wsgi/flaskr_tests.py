from hoyodecrimen import app

import os
import json
import unittest
#import tempfile

class FlaskTestCase(unittest.TestCase):
    # Check that the API is generating json and responding, even if it's crap
    def test_calderas(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/estariamosmejorcon', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # Check that the result sent is the hero of all Mexico
        self.assertEqual(json.loads(response.data), {"rows": ["Calderon"]})

	# Check the API endpoint
    def test_api_v1_top_counts_change_cuadrantes(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/top/counts/change/cuadrantes/homicidio%20doloso', content_type='application/json')
        self.assertEqual(response.status_code, 200)

    # Check that the API correctly deals with date parameters
    def test_error_api_v1_top_counts_change_cuadrantes_dates(self):
        base_url = '/api/v1/top/counts/change/cuadrantes/homicidio%20doloso'
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

    # Check that the API correctly deals with date parameters
    def test_top_rates_sectores(self):
        base_url = '/api/v1/top/rates/sectores/homicidio%20doloso'
        tester = app.test_client(self)
        response = tester.get(base_url + '?start_date=2013-08&end_date=2014-07', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # End date is smaller than start date
        response = tester.get(base_url + '?start_date=2014-08&end_date=2013-07', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        # Start date is smaller than 2013 (when the data started being collected)
        response = tester.get(base_url + '?start_date=2012-08&end_date=2013-07', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        # Equal dates are allowed since it would only span that month
        response = tester.get(base_url + '?start_date=2014-07&end_date=2014-07', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data), {"rows": []})

    # Check that the API correctly deals with date parameters
    def test_top_counts_cuadrantes(self):
        base_url = '/api/v1/top/counts/cuadrantes/homicidio%20doloso'
        tester = app.test_client(self)
        response = tester.get(base_url + '?start_date=2013-08&end_date=2014-07', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # End date is smaller than start date
        response = tester.get(base_url + '?start_date=2014-08&end_date=2013-07', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        # Start date is smaller than 2013 (when the data started being collected)
        response = tester.get(base_url + '?start_date=2012-08&end_date=2013-07', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        # Equal dates are allowed since it would only span that month
        response = tester.get(base_url + '?start_date=2014-07&end_date=2014-07', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data), {"rows": []})

    # Check the API endpoint
    def test_api_v1_enumerate_sectores(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/enumerate/sectores', content_type='application/json')
        self.assertEqual(response.status_code, 200)

    # Check the API endpoint
    def test_api_v1_enumerate_cuadrantes(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/enumerate/cuadrantes', content_type='application/json')
        self.assertEqual(response.status_code, 200)

    # Check the API endpoint
    def test_api_v1_enumerate_crimes(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/enumerate/crimes', content_type='application/json')
        self.assertEqual(response.status_code, 200)

    # Check the API endpoint
    def test_api_v1_list_change_cuadrantes_all(self):
        base_url = '/api/v1/list/change/cuadrantes/all'
        tester = app.test_client(self)
        response = tester.get(base_url + '?start_period1=2013-01&end_period1=2013-12&start_period2=2014-01&end_period2=2014-06', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data), {"rows": []})
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
        base_url = '/api/v1/list/sectores/all'
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
        response = tester.get(base_url + '?start_date=2014-07&end_date=2014-07', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data), {"rows": []})
        # Success
        response = tester.get(base_url + '?start_date=2014-01&end_date=2014-07', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data), {"rows": []})

    # Check the API endpoint
    def test_api_v1_list_cuadrantes_all(self):
        base_url = '/api/v1/list/cuadrantes/all'
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
        response = tester.get(base_url + '?start_date=2014-07&end_date=2014-07', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data), {"rows": []})
        # Success
        response = tester.get(base_url + '?start_date=2014-01&end_date=2014-07', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data), {"rows": []})

    # Check the API endpoint
    def test_api_v1_series_sectores_a(self):
        base_url = '/api/v1/series/sector/angel%20-%20zona%20rosa/violacion'
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
        response = tester.get(base_url + '?start_date=2014-07&end_date=2014-07', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data), {"rows": []})
        # Success
        response = tester.get(base_url + '?start_date=2014-01&end_date=2014-07', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data), {"rows": []})

    # Check the API endpoint
    def test_api_v1_series_cuadrantes(self):
        base_url = '/api/v1/series/cuadrante/c-1.1.1/violacion'
        tester = app.test_client(self)
        response = tester.get(base_url, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # Equal dates are allowed since it would only span that month
        response = tester.get(base_url + '?start_date=2014-07&end_date=2014-07', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # Success
        response = tester.get(base_url + '?start_date=2014-01&end_date=2014-07', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data), {"rows": []})

    # Check the API endpoint
    def test_api_v1_top_counts_change_cuadrantes(self):
        base_url = '/api/v1/series/df/violacion'
        tester = app.test_client(self)
        response = tester.get(base_url, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # Equal dates are allowed since it would only span that month
        response = tester.get(base_url + '?start_date=2014-07&end_date=2014-07', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # Success
        response = tester.get(base_url + '?start_date=2014-01&end_date=2014-07', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data), {"rows": []})

    # Check the API endpoint
    def test_api_v1_pip_extras_(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/pip/extras/-99.13333/19.43', content_type='application/json')
        self.assertEqual(response.status_code, 200)

    # Check the API endpoint
    def test_api_v1_pip(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/pip/-99.13333/19.43', content_type='application/json')
        self.assertEqual(response.status_code, 200)



if __name__ == '__main__':
    unittest.main()
