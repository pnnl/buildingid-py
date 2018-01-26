# -*- coding: utf-8 -*-
#
# pnnl-buildingid: buildingid/code_area.py
#
# Copyright (c) 2018, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE.txt and WARRANTY.txt for details.

from .context import openlocationcode

class CodeArea(openlocationcode.CodeArea):
    """The coordinates of a decoded Unique Building Identifier (UBID).

    The coordinates include the latitude and longitude of the lower left and
    upper right corners of the Open Location Code (OLC) bounding box for the
    building footprint that the code represents, along with the latitude and
    longitude of the lower left and upper right corners of the OLC grid
    reference cell for the geometric center of mass (i.e., centroid) of the
    building footprint that the code represents.

    Attributes:
    child - the coordinates of a decoded OLC for the center of mass (i.e., centroid)
    """

    def __init__(self, child: openlocationcode.CodeArea, *args, **kwargs) -> None:
        """Default constructor.
        """

        super().__init__(*args, **kwargs)

        self.child = child

    def resize(self) -> 'CodeArea':
        """Returns a resized version of this UBID code area, where the latitude
        and longitude of the lower left and upper right corners of the OLC
        bounding box are moved inwards by dimensions that correspond to half of
        the height and width of the OLC grid reference cell for the centroid.

        The purpose of the resizing operation is to ensure that re-encoding a
        given UBID code area results in the same coordinates.
        """

        # Ensure that the parent and child OLC codes are the same length (i.e.,
        # ensure that the OLC grid reference cells are the same size).
        if not (self.codeLength == self.child.codeLength):
            raise ValueError('Invalid CodeArea: \'codeLength\' mismatch')

        # Calculate the (half-)dimensions of OLC grid reference cell for the
        # centroid.
        half_height = (self.child.latitudeHi - self.child.latitudeLo) / 2.0
        half_width = (self.child.longitudeHi - self.child.longitudeLo) / 2.0

        # Construct and return the new UBID code area.
        return CodeArea(self.child, self.latitudeLo + half_height, self.longitudeLo + half_width, self.latitudeHi - half_height, self.longitudeHi - half_width, codeLength=self.codeLength)
