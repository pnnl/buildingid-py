# -*- coding: utf-8 -*-
#
# pnnl-buildingid: buildingid/wkt.py
#
# Copyright (c) 2018, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE.txt and WARRANTY.txt for details.

from .code_area import CodeArea

import shapely.wkt
import typing

def parse(wktstr: str) -> typing.Tuple[float, float, float, float, float, float]:
    """Returns the parameters for encoding a UBID for the shape that is given by Well-known Text (WKT) string.

    Arguments:
    wktstr -- the Well-known Text (WKT) string

    Returns:
    latitudeLo -- the latitude of the southwest corner of the bounding box for the shape
    longitudeLo -- the longitude of the southwest corner of the bounding box for the shape
    latitudeHi -- the latitude of the northeast corner of the bounding box for the shape
    longitudeHi -- the longitude of the northeast corner of the bounding box for the shape
    latitudeCenter -- the latitude of the centroid of the shape
    longitudeCenter -- the longitude of the centroid of the shape

    Raises:
    'shapely.errors.WKTReadingError' -- if an error occurs when reading the Well-known Text (WKT) string
    """

    # Parse the Well-known Text (WKT) string.
    g = shapely.wkt.loads(wktstr)

    # Calculate the bounding box.
    #
    # NOTE For a 'shapely.geometry.point.Point', the "x" field is the longitude
    # and the "y" field is the latitude.
    (longitudeLo, latitudeLo, longitudeHi, latitudeHi) = g.bounds

    # Calculate the centroid.
    g_centroid = g.centroid

    return (latitudeLo, longitudeLo, latitudeHi, longitudeHi, g_centroid.y, g_centroid.x)
