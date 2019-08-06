# -*- coding: utf-8 -*-
#
# pnnl-buildingid: buildingid/command_line/dict_decoders.py
#
# Copyright (c) 2019, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE.txt and WARRANTY.txt for details.

import typing

import shapely.geometry
import shapely.geometry.point
import shapely.wkb
import shapely.wkt

from .dict_datum import DictDatum
from .dict_pipe import DictDecoder

class LatLngDictDecoder(DictDecoder[DictDatum]):
    def __init__(self, fieldname_center_latitude: str, fieldname_center_longitude: str, fieldname_north_latitude: str = None, fieldname_south_latitude: str = None, fieldname_west_longitude: str = None, fieldname_east_longitude: str = None) -> None:
        super(LatLngDictDecoder, self).__init__()

        self.fieldname_center_latitude = fieldname_center_latitude
        self.fieldname_center_longitude = fieldname_center_longitude

        self.fieldname_north_latitude = self.fieldname_center_latitude if (fieldname_north_latitude is None) else fieldname_north_latitude
        self.fieldname_south_latitude = self.fieldname_center_latitude if (fieldname_south_latitude is None) else fieldname_south_latitude
        self.fieldname_east_longitude = self.fieldname_center_longitude if (fieldname_east_longitude is None) else fieldname_east_longitude
        self.fieldname_west_longitude = self.fieldname_center_longitude if (fieldname_west_longitude is None) else fieldname_west_longitude

    def decode(self, row: typing.Dict[str, str]) -> DictDatum:
        center_latitude = float(row[self.fieldname_center_latitude])
        center_longitude = float(row[self.fieldname_center_longitude])

        centroid = shapely.geometry.point.Point(center_longitude, center_latitude)

        if (self.fieldname_center_latitude == self.fieldname_north_latitude == self.fieldname_south_latitude) and (self.fieldname_center_longitude == self.fieldname_east_longitude == self.fieldname_west_longitude):
            return DictDatum(centroid)
        else:
            north_latitude = float(row[self.fieldname_north_latitude])
            south_latitude = float(row[self.fieldname_south_latitude])
            east_longitude = float(row[self.fieldname_east_longitude])
            west_longitude = float(row[self.fieldname_west_longitude])

            bounds = (west_longitude, south_latitude, east_longitude, north_latitude)

            bbox = shapely.geometry.box(*bounds, ccw=True)

            return DictDatum(bbox, bounds=bounds, centroid=centroid)

    @property
    def fieldnames(self) -> typing.List[str]:
        return list(set([
            self.fieldname_center_latitude,
            self.fieldname_center_longitude,
            self.fieldname_north_latitude,
            self.fieldname_south_latitude,
            self.fieldname_east_longitude,
            self.fieldname_west_longitude,
        ]))

class WKBDictDecoder(DictDecoder[DictDatum]):
    def __init__(self, fieldname_wkbstr: str) -> None:
        super(WKBDictDecoder, self).__init__()

        self.fieldname_wkbstr = fieldname_wkbstr

    def decode(self, row: typing.Dict[str, str]) -> DictDatum:
        wkbstr = str(row[self.fieldname_wkbstr])

        geom = shapely.wkb.loads(wkbstr, hex=True)

        return DictDatum(geom)

    @property
    def fieldnames(self) -> typing.List[str]:
        return [
            self.fieldname_wkbstr,
        ]

class WKTDictDecoder(DictDecoder[DictDatum]):
    def __init__(self, fieldname_wktstr: str) -> None:
        super(WKTDictDecoder, self).__init__()

        self.fieldname_wktstr = fieldname_wktstr

    def decode(self, row: typing.Dict[str, str]) -> DictDatum:
        wktstr = str(row[self.fieldname_wktstr])

        geom = shapely.wkt.loads(wktstr)

        return DictDatum(geom)

    @property
    def fieldnames(self) -> typing.List[str]:
        return [
            self.fieldname_wktstr,
        ]
