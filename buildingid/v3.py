# -*- coding: utf-8 -*-
#
# pnnl-buildingid: buildingid/v3.py
#
# Copyright (c) 2018, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE.txt and WARRANTY.txt for details.

from .context import openlocationcode

from .code_area import CodeArea

import re

# Format string for UBID codes.
FORMAT_STRING_ = '%s-%.0f-%.0f-%.0f-%.0f'

# Regular expression for UBID codes.
RE_PATTERN_ = re.compile(r'^([' + re.escape(openlocationcode.CODE_ALPHABET_) + r']{4,8}' + re.escape(openlocationcode.SEPARATOR_) + r'[' + re.escape(openlocationcode.CODE_ALPHABET_) + r']*)-(0|[1-9][0-9]*)-(0|[1-9][0-9]*)-(0|[1-9][0-9]*)-(0|[1-9][0-9]*)$')

# The first group of a UBID code is the OLC for the geometric center of mass
# (i.e., centroid) of the building footprint.
RE_GROUP_OPENLOCATIONCODE_ = 1

# The second group of the UBID code is the Chebyshev distance in OLC grid units
# from the OLC for the centroid of the building footprint to the northern extent
# of the OLC bounding box for the building footprint.
RE_GROUP_NORTH_ = 2

# The third group of the UBID code is the Chebyshev distance in OLC grid units
# from the OLC for the centroid of the building footprint to the eastern extent
# of the OLC bounding box for the building footprint.
RE_GROUP_EAST_ = 3

# The fourth group of the UBID code is the Chebyshev distance in OLC grid units
# from the OLC for the centroid of the building footprint to the southern extent
# of the OLC bounding box for the building footprint.
RE_GROUP_SOUTH_ = 4

# The fifth group of the UBID code is the Chebyshev distance in OLC grid units
# from the OLC for the centroid of the building footprint to the western extent
# of the OLC bounding box for the building footprint.
RE_GROUP_WEST_ = 5

def decode(code: str) -> CodeArea:
    """Returns the UBID code area for the given UBID code.

    Arguments:
    code - the UBID code

    Returns:
    The UBID code area.

    Raises:
    'ValueError' - if the UBID code is invalid or if the OLC for the centroid of the building footprint is invalid
    """

    # Attempt to match the regular expression.
    match = RE_PATTERN_.match(code)

    # If the UBID code does not match the regular expression, raise an error.
    if match is None:
        raise ValueError('Invalid UBID')

    # Extract the OLC for the centroid of the building footprint.
    centroid_openlocationcode = match.group(RE_GROUP_OPENLOCATIONCODE_)

    # Decode the OLC for the centroid of the building footprint.
    centroid_openlocationcode_CodeArea = openlocationcode.decode(centroid_openlocationcode)

    # Calculate the size of the OLC for the centroid of the building footprint
    # in decimal degree units.
    height = centroid_openlocationcode_CodeArea.latitudeHi - centroid_openlocationcode_CodeArea.latitudeLo
    width = centroid_openlocationcode_CodeArea.longitudeHi - centroid_openlocationcode_CodeArea.longitudeLo

    # Calculate the size of the OLC bounding box for the building footprint,
    # assuming that the datum are Chebyshev distances.
    latitudeHi = centroid_openlocationcode_CodeArea.latitudeHi + (int(match.group(RE_GROUP_NORTH_)) * height)
    longitudeHi = centroid_openlocationcode_CodeArea.longitudeHi + (int(match.group(RE_GROUP_EAST_)) * width)
    latitudeLo = centroid_openlocationcode_CodeArea.latitudeLo - (int(match.group(RE_GROUP_SOUTH_)) * height)
    longitudeLo = centroid_openlocationcode_CodeArea.longitudeLo - (int(match.group(RE_GROUP_WEST_)) * width)

    # Construct and return the UBID code area.
    return CodeArea(centroid_openlocationcode_CodeArea, latitudeLo, longitudeLo, latitudeHi, longitudeHi, centroid_openlocationcode_CodeArea.codeLength)

def encode(latitudeLo: float, longitudeLo: float, latitudeHi: float, longitudeHi: float, latitudeCenter: float, longitudeCenter: float, **kwargs) -> str:
    """Returns the UBID code for the given coordinates.

    Arguments:
    latitudeLo - the latitude in decimal degrees of the southwest corner of the minimal bounding box for the building footprint
    longitudeLo - the longitude in decimal degrees of the southwest corner of the minimal bounding box for the building footprint
    latitudeHi - the latitude in decimal degrees of the northeast corner of the minimal bounding box for the building footprint
    longitudeHi - the longitude in decimal degrees of the northeast corner of the minimal bounding box for the building footprint
    latitudeCenter - the latitude in decimal degrees of the centroid of the building footprint
    longitudeCenter - the longitude in decimal degrees of the centroid of the building footprint

    Keyword arguments:
    codeLength - the OLC code length (not including the separator)

    Returns:
    The UBID code area.

    Raises:
    'ValueError' - if the OLC for the centroid of the building footprint cannot be encoded (e.g., invalid code length)
    """

    # Encode the OLCs for the northeast and southwest corners of the minimal
    # bounding box for the building footprint.
    northeast_openlocationcode = openlocationcode.encode(latitudeHi, longitudeHi, **kwargs)
    southwest_openlocationcode = openlocationcode.encode(latitudeLo, longitudeLo, **kwargs)

    # Encode the OLC for the centroid of the building footprint.
    centroid_openlocationcode = openlocationcode.encode(latitudeCenter, longitudeCenter, **kwargs)

    # Decode the OLCs for the northeast and southwest corners of the minimal
    # bounding box for the building footprint.
    northeast_openlocationcode_CodeArea = openlocationcode.decode(northeast_openlocationcode)
    southwest_openlocationcode_CodeArea = openlocationcode.decode(southwest_openlocationcode)

    # Decode the OLC for the centroid of the building footprint.
    centroid_openlocationcode_CodeArea = openlocationcode.decode(centroid_openlocationcode)

    # Calculate the size of the OLC for the centroid of the building footprint
    # in decimal degree units.
    height = centroid_openlocationcode_CodeArea.latitudeHi - centroid_openlocationcode_CodeArea.latitudeLo
    width = centroid_openlocationcode_CodeArea.longitudeHi - centroid_openlocationcode_CodeArea.longitudeLo

    # Calculate the Chebyshev distances to the northern, eastern, southern and
    # western of the OLC bounding box for the building footprint.
    delta_north = (northeast_openlocationcode_CodeArea.latitudeHi - centroid_openlocationcode_CodeArea.latitudeHi) / height
    delta_east = (northeast_openlocationcode_CodeArea.longitudeHi - centroid_openlocationcode_CodeArea.longitudeHi) / width
    delta_south = (centroid_openlocationcode_CodeArea.latitudeLo - southwest_openlocationcode_CodeArea.latitudeLo) / height
    delta_west = (centroid_openlocationcode_CodeArea.longitudeLo - southwest_openlocationcode_CodeArea.longitudeLo) / width

    # Construct and return the UBID code.
    return FORMAT_STRING_ % (centroid_openlocationcode, delta_north, delta_east, delta_south, delta_west)

def encodeCodeArea(parent: CodeArea) -> str:
    """Returns the UBID code for the given UBID code area.

    Arguments:
    parent - the UBID code area

    Returns:
    The UBID code area.

    Raises:
    'ValueError' - if the OLC for the centroid of the building footprint cannot be encoded (e.g., invalid code length)
    """

    # Ensure that the UBID code area is valid (e.g., that the OLC code lengths
    # for the UBID code area and the OLC code area are equal).
    if parent is None:
        raise ValueError('Invalid CodeArea')
    elif not (parent.codeLength == parent.child.codeLength):
        raise ValueError('Invalid CodeArea: \'codeLength\' mismatch')

    # Delegate.
    return encode(parent.latitudeLo, parent.longitudeLo, parent.latitudeHi, parent.longitudeHi, parent.child.latitudeCenter, parent.child.longitudeCenter, codeLength=parent.codeLength)

def isValid(code: str) -> bool:
    """Is the given UBID code valid?

    Arguments:
    code - the UBID code

    Returns:
    'True' if the UBID code is valid. Otherwise, 'False'.
    """

    # Undefined UBID codes are invalid.
    if code is None:
        return False

    # Attempt to match the regular expression.
    match = RE_PATTERN_.match(code)

    # UBID codes that fail to match the regular expression are invalid.
    if match is None:
        return False

    # A UBID code that successfully matches the regular expression is valid if
    # the OLC for the centroid of the building footprint is valid.
    return openlocationcode.isValid(match.group(RE_GROUP_OPENLOCATIONCODE_))
