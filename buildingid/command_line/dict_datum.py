# -*- coding: utf-8 -*-
#
# pnnl-buildingid: buildingid/command_line/dict_datum.py
#
# Copyright (c) 2019, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE.txt and WARRANTY.txt for details.

import typing

import shapely.geometry.base
import shapely.geometry.point

from ..code import Code, encode

class DictDatum(object):
    def __init__(self, geom: shapely.geometry.base.BaseGeometry, bounds: typing.Tuple[float, float, float, float] = None, centroid: shapely.geometry.point.Point = None) -> None:
        super(DictDatum, self).__init__()

        self.geom = geom

        self._bounds = bounds
        self._centroid = centroid

    @property
    def bounds(self) -> typing.Tuple[float, float, float, float]:
        if self._bounds is None:
            return self.geom.bounds
        else:
            return self._bounds

    @property
    def centroid(self) -> shapely.geometry.point.Point:
        if self._centroid is None:
            return self.geom.centroid
        else:
            return self._centroid

    def encode(self, **kwargs) -> Code:
        bounds = self.bounds
        centroid = self.centroid

        return encode(bounds[1], bounds[0], bounds[3], bounds[2], centroid.y, centroid.x, **kwargs)
