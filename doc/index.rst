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

Status
======
This is beta software and paths may break (but not much). If you
notice an error, have any comments, or stuff you'd like added to the
API raise an issue on `GitHub
<https://github.com/diegovalle/hoyodecrimen.api/issues>`_ or email me
at diegovalle@gmail.com. All data comes from freedom of information
requests to the Mexico City government, sometimes I get data on crimes
which happened in non-specified cuadrantes *(en blanco)* and sometimes
not depending on how lucky I get when the FOI request is answered.

License
========

Data accessed via this API is provided under the 
`Creative Commons Attribution-ShareAlike (CC-BY-SA) 3.0 Unported license 
<https://creativecommons.org/licenses/by-sa/3.0/legalcode>`_. If you use
this data you must link back to https://hoyodecrimen.com/ as
the origin of the data.

What's available
================


+------------------------+-----------------------------------------------------+------------------------------------------------------------------+
| Service                | Action                                              | URI                                                              | 
|                        |                                                     |                                                                  |
+========================+=====================================================+==================================================================+
| Point in Polygon       | Given a longitude and latitude return the           | | **/v1/pip/(string: long)/(string: lat)**                       |
|                        | corresponding cuadrante and sector                  | | **/v1/pip/extras/(string: long)/(string: lat)**                |
+------------------------+-----------------------------------------------------+------------------------------------------------------------------+
| Time Series            | Crimes counts ordered by month of occurrence for a  | | **/v1/series/sector/(string: sector)/(string: crime)**         |
|                        | single cuadrante or sector                          | | **/v1/series/cuadrante/(string: cuadrante/(string: crime))**   |
|                        |                                                     |                                                                  |
+------------------------+-----------------------------------------------------+------------------------------------------------------------------+
| List Cuadrantes or     | Sum of crimes that occurred in each                 | | **/v1/list/cuadrantes/(string: crime)**                        |
| Sectores               | and every cuadrante or sector for a specified       | | **/v1/list/sectores/(string: crime)**                          |
|                        | period of time                                      | | **/v1/list/change/cuadrantes/(string: crime)**                 |
+------------------------+-----------------------------------------------------+------------------------------------------------------------------+
| Top Most Violent       | A list of the cuadrantes and sectors with the       | | **/v1/top/rates/sectores/(string: crime)**                     |
|                        | highest rates (sectores), crime counts              | | **/v1/top/counts/cuadrantes/(string: crime)**                  |
|                        | (cuadrantes) or change in crime counts              | | **/v1/top/counts/change/cuadrantes/(string: crime)**           | 
+------------------------+-----------------------------------------------------+------------------------------------------------------------------+
| DF data                | A time series of the sum of all crimes              | | **/v1/series/df/(string: crime)**                              |
|                        | that occurred in the Federal District               |                                                                  |
+------------------------+-----------------------------------------------------+------------------------------------------------------------------+
| Enumerate              | Get a list of the names of all cuadrantes,          | | **/v1/enumerate/crimes**                                       |
|                        | sectores or crimes                                  | | **/v1/enumerate/sectores**                                     |
|                        |                                                     | | **/v1/enumerate/cuadrantes**                                   |
+------------------------+-----------------------------------------------------+------------------------------------------------------------------+


Basic overview
==============

Broadly speaking, you can get a JSON representation of any type of
crime that occurred in the Federal District. For example,
https://hoyodecrimen.com/api/v1/enumerate/crimes will return a list of
all crimes in the database.
https://hoyodecrimen.com/api/v1/enumerate/cuadrantes will return a list
of all the cuadrantes in the Federal District. Once you have a list of
crimes and cuadrantes you can use
https://hoyodecrimen.com/api/v1/series/cuadrante/c-1.1.1/homicidio%20doloso
to get a time series of the homicide rate in cuadrante c-1.1.1. Note
that `homicidio%20doloso` can be changed to `all` to get all the
crimes that occurred in that cuadrante.

Getting Started
=================

All endpoints are GET requests that send back an object filled will
the relevant data. You really want to use JSONP to access the
API. Here is a basic example of how to handle JSONP requests using
jQuery.

.. code-block:: javascript

   $.ajax({
       dataType: 'jsonp',
       url: 'http://localhost:5000/api/v1/series/cuadrante/c-1.1.1/homicidio%20doloso',
       success: function(data) {
           // console.debug(data)
       }
   });

Handling Errors
=================

If there is a validation error with the request, or the cuadrante or
crime queried does not exist, an error object will be passed back
which contains a short description of what went wrong.

Example Error Response

.. code-block:: javascript

   $.ajax({
       dataType: 'jsonp',
       // notice the invalid start_date
       url: 'http://localhost:5000/api/v1/series/cuadrante/c-1.1.1/all?start_date=2014-99?end_date=2014-07',
       success: function(data) {
           // console.debug(data)
       },
       error: function(xhr, error) {
           // console.debug(xhr.responseText); // error description
           // console.debug(xhr.status); //should be 400
       }
   });

If you query for a crime or cuadrante that doesn't exist a 404 error is returned


Note
====
Population is given in persons/year and corresponds to that of the
2010 census.


API Reference
==============

.. autoflask:: hoyodecrimen:app
   :blueprints: API
