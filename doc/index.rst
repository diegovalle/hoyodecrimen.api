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
crime that occurred in the Federal District. For example, http:// will
give you a list of all the cuadrantes the Federal District is made of.
http:// will give you a list of all crimes in the database.  Then you
can use http:// to get a time series of the homicide rate in cuadrante
c-1.1.1. Note that "homicidio doloso" can be changed to `all` to get
all the crimes that occurred in that cuadrante.

What's available
================


+------------------------+----------------------------------------------------------------+--------------+----------+
| Service                | Description                                                    | Example Use  | Header 4 |
|                        |                                                                |              |          |
+========================+================================================================+==============+==========+
| Point in Polygon       | Given a lat and longitude return the
                           corresponding cuadrante                                                       | column 3     | column 4 |
+------------------------+----------------------------------------------------------------+--------------+----------+
| Time Series            |                                                             | ...          |          |
+------------------------+----------------------------------------------------------------+--------------+----------+
| List Cuadrantes and     | sum of crimes that occurred in each 
| Sectores               | cuadrante or sector for a specified period of time
                                                                                      | ...          |          |
+------------------------+----------------------------------------------------------------+--------------+----------+
| Top Most Violent       | A list of the Cuadrantes and sectors with the 
                         | highest rates (sectores) and crime counts 
                         | (cuadrantes)                                                           | ...          |          |
+------------------------+----------------------------------------------------------------+--------------+----------+
| DF data                | A time series of the sum of all crimes 
                         | that occurred in the Federal District                                                         | ...          |          |
+------------------------+----------------------------------------------------------------+--------------+----------+
| Enumerate                  | Get a list of available Cuadrantes, 
                         | Sectores and Crimes                                     | ...          |          |
+------------------------+----------------------------------------------------------------+--------------+----------+

Endpoints
==========

.. autoflask:: api:app
   :endpoints:
