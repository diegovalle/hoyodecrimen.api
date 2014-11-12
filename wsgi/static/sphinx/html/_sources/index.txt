.. HoyoDeCrimen API documentation master file, created by
   sphinx-quickstart on Sun Oct 19 16:45:20 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. Fuck you sphinx documentation. I'm not including any god damn toctree directive
   straight to the content for me. #FirstWorldAnarchists

Welcome to HoyoDeCrimen API's documentation!
============================================

.. contents::



.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`


Basic overview
==============

The Hoyodecrimen REST API allows you to query crime data about Mexico
City. You can even do fancy things like get the top 9 cuadrantes
where homicide counts changed the most.

Since the API is based on REST principles and returns JSON data, it's
very easy to write applications that use it. You can use your browser
to access any API URL, or pretty much any HTTP client in any
programming language (yes, even something like STATA).

For example, https://hoyodecrimen.com/api/v1/crimes will return a list
of all crimes in the database.
https://hoyodecrimen.com/api/v1/cuadrantes will return a list of all
the cuadrantes in the Federal District. Once you have a list of crimes
and cuadrantes you can use
https://hoyodecrimen.com/api/v1/cuadrantes/c-1.1.1/crimes/homicidio%20doloso/series
to get a time series of the homicide rate in cuadrante C-1.1.1 (the
API is case insensitive). Note that `homicidio%20doloso` can be
changed to `all` to get all the crimes that occurred in that
cuadrante.

Status
======
This is beta software and paths may break (but not much). If you
notice an error, have any comments, or stuff you'd like added to the
API raise an issue on `GitHub
<https://github.com/diegovalle/hoyodecrimen.api/issues>`_ or email me
at diegovalle@gmail.com. All data comes from freedom of information
requests to the Mexico City government, sometimes I get data on crimes
which happened in non-specified cuadrantes (*NO ESPECIFICADO*) and sometimes
not, depending on how lucky I get when the FOIA request is answered.

License
========

Data accessed via this API is provided under the
`Attribution-NonCommercial-ShareAlike 4.0 International
<http://creativecommons.org/licenses/by-nc-sa/4.0/>`_. If you use this
data you must link back to https://hoyodecrimen.com/ as the origin of
the data.

What's available
================


+------------------------+-----------------------------------------------------+-----------------------------------------------------------------------------------+
| Service                | Action                                              | URI                                                                               | 
|                        |                                                     |                                                                                   |
+========================+=====================================================+===================================================================================+
| Point in Polygon       | Given a longitude and latitude return the           | | **/api/v1/cuadrantes/pip/(string: long)/(string: lat)**                         |
|                        | corresponding cuadrante and sector                  | | **/api/v1/cuadrantes/crimes/(string: crime)/pip/(string: long)/(string: lat)**  |
+------------------------+-----------------------------------------------------+-----------------------------------------------------------------------------------+
| Time Series            | Crime counts ordered by month of occurrence for a   | | **/api/v1/sectores/(string: sector)/crimes/(string: crime)/series/**            |
|                        | cuadrante or sector                                 | | **/api/v1/cuadrantes/(string: cuadrante)/crimes/(string: crime)/series**        |
|                        |                                                     |                                                                                   |
+------------------------+-----------------------------------------------------+-----------------------------------------------------------------------------------+
| List Cuadrantes or     | Sum of crimes that occurred in a                    | | **/api/v1/cuadrantes/(string: cuadrante)/crimes/(string: crime)/period**        |
| Sectores               | cuadrante or sector for a specified                 | | **/api/v1/sectores/(string: sector)/crimes/(string: crime)/period**             |
|                        | period of time                                      | | **/api/v1/cuadrantes/(string: cuadrante)/crimes/(string: crime)/period/change** |
+------------------------+-----------------------------------------------------+-----------------------------------------------------------------------------------+
| Top Most Violent       | A list of the cuadrantes and sectors with the       | | **/api/v1/sectores/crimes/(string: crime)/top/rates**                           |
|                        | highest rates (sectores), crime counts              | | **/api/v1/cuadrantes/crimes/(string: crime)/top/counts**                        |
|                        | (cuadrantes) or change in crime counts (cuadrantes) | | **/api/v1/cuadrantes/crimes/(string: crime)/top/counts/change**                 | 
+------------------------+-----------------------------------------------------+-----------------------------------------------------------------------------------+
| DF data                | A time series of the sum of all crimes              | | **/api/v1/df/crimes/(string: crime)/series**                                    |
|                        | that occurred in the Federal District               |                                                                                   |
+------------------------+-----------------------------------------------------+-----------------------------------------------------------------------------------+
| Enumerate              | Get a list of the names of all cuadrantes,          | | **/api/v1/cuadrantes**                                                          |
|                        | sectores or crimes                                  | | **/api/v1/sectores**                                                            |
|                        |                                                     | | **/api/v1/crimes**                                                              |
+------------------------+-----------------------------------------------------+-----------------------------------------------------------------------------------+


Getting Started
=================

All endpoints are GET requests that send back an object filled will
the relevant data. You really want to use JSONP to access the
API. Here is a basic example of how to handle JSONP requests using
jQuery.

.. code-block:: javascript

   $.ajax({
       dataType: 'jsonp',
       url: 'https://hoyodecrimen.com/api/v1/cuadrantes/c-1.1.1/crimes/homicidio%20doloso/series',
       success: function(data) {
           // console.debug(data)
       }
   });

.. or in python:

.. python

..   import requests as r
..   import pandas as pd
..   sectores = r.get("https://hoyodecrimen.com/api/v1/sectores").json['rows']
..   df = pd.DataFrame(sectores)

Handling Errors
=================

If there is a validation error with the request, or the cuadrante or
crime queried does not exist, an error object will be passed back
which contains a short description of what went wrong.

Example Error Response:

.. code-block:: javascript

   $.ajax({
       dataType: 'jsonp',
       // notice the invalid start_date
       url: 'https://hoyodecrimen.com/api/v1/cuadrantes/c-1.1.1/crimes/all/series?start_date=2014-99?end_date=2014-07',
       success: function(data) {
           // console.debug(data)
       },
       error: function(xhr, error) {
           // console.debug(xhr.responseText); // error description
           // console.debug(xhr.status); //should be 400
       }
   });

Note
====
Population is given in persons/year and corresponds to that of the
2010 census.


API Reference
==============

.. autoflask:: hoyodecrimen:app
  :undoc-static:
