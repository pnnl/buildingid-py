=================================
Unique Building Identifier (UBID)
=================================

**Website:** https://buildingid.pnnl.gov/

-------------
Documentation
-------------

Install
=======

To complete this guide, `Git <https://git-scm.com/>`_ and `Python 3 <https://www.python.org/>`_ are required.
Dependencies are automatically installed using `pip <https://pypi.python.org/pypi/pip>`_.

Clone the repository and submodules, and then install the ``pnnl-buildingid`` package:

::

  git clone https://github.com/pnnl/buildingid-py
  cd buildingid-py
  git submodule update --init
  pip3 install -e .

Verify the location of the ``buildingid`` command:

::

  which buildingid
  #=> /usr/local/bin/buildingid

Uninstall
=========

Use `pip <https://pypi.python.org/pypi/pip>`_ to remove the ``pnnl-buildingid`` package:

::

  pip3 uninstall pnnl-buildingid

Test
====

Test the ``pnnl-buildingid`` package using the `nose <https://pypi.org/project/nose/>`_ package:

::

  nosetests tests/

Coverage testing is enabled using the `coverage <https://pypi.org/project/coverage/>`_ package:

::

  nosetests --with-coverage --cover-html --cover-package=buildingid tests/

Usage
=====

The ``pnnl-buildingid`` package supports two usages:

* Application programming interface (API)
* Command-line interface (CLI; the ``buildingid`` command)

The API
```````

* ``buildingid.code``

  - ``Code``

  - ``CodeArea``

    + ``encode() -> Code``

    + ``resize() -> CodeArea``

  - ``decode(Code) -> CodeArea``

  - ``encode(float, float, float, float, float, float, **kwargs) -> Code``

  - ``isValid(Code) -> bool``

In the following example, a UBID code is decoded and then re-encoded:

::

  #!/usr/bin/env python3
  # -*- coding: utf-8 -*-

  import buildingid.code

  if __name__ == '__main__':
    # Initialize UBID code.
    orig_code = '849VQJH6+95J-51-58-42-50'
    print(orig_code)

    # Decode UBID code.
    orig_code_area = buildingid.code.decode(orig_code)
    print(orig_code_area)

    # Resize resulting UBID code area.
    #
    # The effect of this operation is that the length and width of the UBID code
    # area are reduced by half an OLC code area.
    new_code_area = orig_code_area.resize()
    print(new_code_area)

    # Encode new UBID code area.
    new_code = new_code_area.encode()
    print(new_code)

    # Test that new UBID code and UBID code area match the originals.
    assert (orig_code == new_code)
    assert (orig_code_area == new_code_area)

The CLI
```````

View the documentation for the ``buildingid`` command using the ``--help`` command-line option:

::

  buildingid --help
  #=> Usage: buildingid [OPTIONS] COMMAND [ARGS]...
  #=> <<more lines of output>>

View the documentation for a sub-command of the ``buildingid`` command using the ``--help`` command-line option.
For example, to view the documentation for the "append2csv" sub-command:

::

  buildingid append2csv --help
  #=> Usage: buildingid append2csv [OPTIONS] [latlng|wkb|wkt]
  #=> <<more lines of output>>

Commands
^^^^^^^^

+---------------------+--------------------------------------------------------+
| Command name        | Description                                            |
+=====================+========================================================+
| append2csv          | Read CSV file from stdin, append UBID field, and write |
|                     | CSV file to stdout.                                    |
+---------------------+--------------------------------------------------------+

---------
Tutorials
---------

Instructions in this section use `Bash <https://www.gnu.org/software/bash/>`_ syntax.

Append UBID field to CSV file
=============================

Prerequisites
`````````````

1. ``buildingid`` command is installed.

   * Verify installation:

     - ``buildingid --version``

       + Expected output: "buildingid, version 2.0.0" (or higher version)

Step-by-step instructions
`````````````````````````

1. Locate input CSV file, e.g., ``path/to/in.csv``.

2. Locate output CSV file (generated), e.g., ``path/to/out.csv``.

3. Locate errors CSV file (generated), e.g., ``path/to/err.csv``.

4. Identify number of digits in `Open Location Code (OLC) <https://plus.codes/>`_ part of UBID code string, e.g., 11.

5. Identify column of output CSV file that contains UBID code strings, e.g., "UBID".

6. If input CSV file contains latitude and longitude coordinates for a centroid only:

   1. Identify columns of input CSV file that contain latitude and longitude coordinates, e.g., "Latitude" and "Longitude".

   2. Assign UBIDs:

      * ``buildingid append2csv latlng --code-length=11 --fieldname-code="UBID" --fieldname-center-latitude="Latitude" --fieldname-center-longitude="Longitude" < path/to/in.csv > path/to/out.csv 2> path/to/err.csv``

7. If input CSV file contains latitude and longitude coordinates for (i) a centroid and (ii) the northeast and southwest corners of a bounding box:

   1. Identify columns of input CSV file that contain latitude and longitude coordinates, e.g., "Latitude_C", "Longitude_C", "Latitude_N", "Longitude_E", "Latitude_S", and "Longitude_W".

   2. Assign UBIDs:

      * ``buildingid append2csv latlng --code-length=11 --fieldname-code="UBID" --fieldname-center-latitude="Latitude_C" --fieldname-center-longitude="Longitude_C" --fieldname-north-latitude="Latitude_N" --fieldname-east-longitude="Longitude_E" --fieldname-south-latitude="Latitude_S" --fieldname-west-longitude="Longitude_W" < path/to/in.csv > path/to/out.csv 2> path/to/err.csv``

8. If input CSV file contains hex-encoded `well-known binary (WKB) <https://www.iso.org/standard/60343.html>`_ strings:

   1. Identify column of input CSV file that contains hex-encoded WKB strings, e.g., "WKB".

   2. Assign UBIDs:

      * ``buildingid append2csv wkb --code-length=11 --fieldname-code="UBID" --fieldname-wkbstr="WKB" < path/to/in.csv > path/to/out.csv 2> path/to/err.csv``

9. If input CSV file contains `well-known text (WKT) <https://www.iso.org/standard/60343.html>`_ strings:

   1. Identify column of input CSV file that contains WKT strings, e.g., "WKT".

   2. Assign UBIDs:

      * ``buildingid append2csv wkt --code-length=11 --fieldname-code="UBID" --fieldname-wktstr="WKT" < path/to/in.csv > path/to/out.csv 2> path/to/err.csv``

Notes
`````

See ``buildingid append2csv --help`` for full help.

Convert from Esri shapefile to CSV file
=======================================

Prerequisites
`````````````

1. `Geospatial Data Abstraction Library (GDAL) <https://www.gdal.org/>`_ is installed.

   * Verify installation:

     - ``ogr2ogr --version``

       + Expected output: "GDAL 2.3.1, released 2018/06/22" (version and release date may vary)

Step-by-step instructions
`````````````````````````

1. Locate input Esri shapefile, e.g., ``path/to/in.shp``.

2. Locate output CSV file (generated), e.g., ``path/to/out.csv``.

3. Convert input Esri shapefile into output CSV file:

   * ``ogr2ogr -t_srs "EPSG:4326" -f CSV path/to/out.csv path/to/in.shp -lco GEOMETRY=AS_WKT``

Notes
`````

See ``ogr2ogr --long-usage`` for full help.

Output CSV file has added "WKT" column whose elements are `well-known text (WKT) <https://www.iso.org/standard/60343.html>`_ strings; enabled by ``-lco GEOMETRY=AS_WKT`` option.

Projection system for geographic coordinates is `WGS84 <https://epsg.io/4326>`_; enabled by ``-t_srs "EPSG:4326"`` option.

Records in input Esri shapefile are converted into rows in output CSV file, where fields in input Esri shapefile are converted into columns in output CSV file.

Shapes in input Esri shapefile are converted into elements of "WKT" column of output CSV file.

------------
Case Studies
------------

Chicago, IL
===========

`The City of Chicago's open data portal <https://data.cityofchicago.org>`_ hosts the `"Building Footprints (current)" <https://data.cityofchicago.org/Buildings/Building-Footprints-current-/hz9b-7nh8>`_ dataset in CSV format; available at: https://data.cityofchicago.org/api/views/syp8-uezg/rows.csv?accessType=DOWNLOAD.

The "the_geom" column of the input CSV file contains WKT strings.

To assign UBIDs to the records in the input CSV file:

1. ``buildingid append2csv wkt --code-length=11 --fieldname-code="UBID" --fieldname-wktstr="the_geom" < rows.csv > rows.out.csv 2> rows.err.csv``

San Jose, CA
============

The `City of San Jose <http://www.sanjoseca.gov>`_ hosts `datasets <http://www.sanjoseca.gov/index.aspx?NID=3308>`_ that include building footprints and land parcels.

The contents of the `"Basemap_2" <http://www.sanjoseca.gov/DocumentCenter/View/44895>`_ zip archive includes a building footprints dataset in Esri shapefile format.
The coordinate system is `NAD 1983 StatePlane California III FIPS 0403 Feet <http://www.spatialreference.org/ref/esri/102643/>`_.

To convert the Esri shapefile into CSV format and then assign UBIDs to the resulting CSV file:

1. ``ogr2ogr -t_srs "ESRI:102643" -f CSV BuildingFootprint.csv Basemap2_201905021152225992/BuildingFootprint.shp -lco GEOMETRY=AS_WKT``

2. ``buildingid append2csv wkt --code-length=11 --fieldname-code="UBID" --fieldname-wktstr="WKT" < BuildingFootprint.csv > BuildingFootprint.out.csv 2> BuildingFootprint.err.csv``

-------
License
-------

`The 2-Clause BSD License <https://opensource.org/licenses/BSD-2-Clause>`_

-------------
Contributions
-------------

Contributions are accepted on `GitHub <https://github.com/>`_ via the fork and pull request workflow.
See `here <https://help.github.com/articles/using-pull-requests/>`_ for more information.
