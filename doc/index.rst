.. HoyoDeCrimen API documentation master file, created by
   sphinx-quickstart on Sun Oct 19 16:45:20 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to HoyoDeCrimen API's documentation!
============================================

Contents:

.. toctree::
   :maxdepth: 2



.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`

License
========

Data accessed via this API is provided under the 
`Creative Commons Attribution-ShareAlike (CC-BY-SA) 3.0 Unported license 
<http://creativecommons.org/licenses/by-sa/3.0/legalcode>`_. If you use
this data you must link back to http://hoyodecrimen.com/, as
the origin of the data.


Basic overview
==============

Broadly speaking, you can get a JSON representation of any type of
crime that occurred in the Federal District. For example,
http://hoyodecrimen.com/v1/enumerate/cuadrantes will return a list of
all the cuadrantes the Federal District is made of.
http://hoyodecrimen.com/v1/enumerate/crimes will return a list of all
crimes in the database. Then you can use
http://hoyodecrimen.com/v1/series/cuadrantes/homicidio%20doloso/c-1.1.1
to get a time series of the homicide rate in cuadrante c-1.1.1. Note
that "homicidio doloso" can be changed to `all` to get all the crimes
that occurred in that cuadrante.

Note
====
Population is given in persons/year and corresponds to that of the
2010 census. Rates are always annualized.

What's available
================


+------------------------+-----------------------------------------------------+------------------------------------------------------------------+
| Service                | Description                                         | Endpoint                                                         | 
|                        |                                                     |                                                                  |
+========================+=====================================================+==================================================================+
| Point in Polygon       | Given a lat and longitude return the                | | **/v1/pip/(string: long)/(string: lat)**                       |
|                        | corresponding cuadrante                             | | **/v1/pip/extras/(string: long)/(string: lat)**                |
+------------------------+-----------------------------------------------------+------------------------------------------------------------------+
| Time Series            | Crimes ordered by month of occurrence               | | **/v1/series/sector/(string: sector)/(string: crime)**       |
|                        |                                                     | | **/v1/series/cuadrante/(string: cuadrante/(string: crime))**  |
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


Endpoints
==========

.. autoflask:: hoyodecrimen:app
   :blueprints: API
