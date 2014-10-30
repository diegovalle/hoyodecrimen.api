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
        response = tester.get('/api/v1/cuadrantes/crimes/homicidio%20doloso/top/counts/change', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data), {"rows": []})

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
        base_url = '/api/v1/sectores/crimes/homicidio%20doloso/top/rates'
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
        base_url = '/api/v1/cuadrantes/crimes/homicidio%20doloso/top/counts'
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
        response = tester.get('/api/v1/sectores/enumerate', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data), {"rows": []})

    # Check the API endpoint
    def test_api_v1_enumerate_cuadrantes(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/cuadrantes/enumerate', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data), {"rows": []})

    # Check the API endpoint
    def test_api_v1_enumerate_crimes(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/crimes/enumerate', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data), {"rows": []})

    # Check the API endpoint
    def test_api_v1_list_change_cuadrantes_all(self):
        base_url = '/api/v1/cuadrantes/crimes/all/period/change'
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
        base_url = '/api/v1/sectores/crimes/all/period'
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
        base_url = '/api/v1/cuadrantes/crimes/all/period'
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
        base_url = '/api/v1/sector/angel%20-%20zona%20rosa/crimes/violacion/series'
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
        #response = tester.get('/api/v1/sector/angel%20-%20zona%20rosa/crimes/robo%20a%20negocio%20c.v./series', content_type='application/json')
        #self.assertEqual(response.status_code, 200)

    # Check the API endpoint
    def test_api_v1_series_cuadrantes_crimes(self):
        base_url = '/api/v1/cuadrante/c-1.1.1/crimes/violacion/series'
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
        self.assertNotEqual(json.loads(response.data), {"rows": []})


    # Check the API endpoint
    def test_api_v1_pip_extras_(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/pip/-99.13333/19.43/extras', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data), {"rows": []})

    # Check the API endpoint
    def test_api_v1_pip(self):
        tester = app.test_client(self)
        response = tester.get('/api/v1/pip/-99.13333/19.43', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.data), {"rows": []})

    def test_api_404(self):
        tester = app.test_client(self)
        response = tester.get('/adsflsdklfjaskljfkldsjfkjasklfjklsafsadfs', content_type='html/text')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
