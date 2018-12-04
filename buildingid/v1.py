# -*- coding: utf-8 -*-
#
# pnnl-buildingid: buildingid/v1.py
#
# Copyright (c) 2018, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE.txt and WARRANTY.txt for details.

from .context import openlocationcode

from .code_area import CodeArea
from .version import __version__

import deprecation
import re

# Separator for components of a UBID code.
SEPARATOR_ = '-'

# Format string for UBID codes.
FORMAT_STRING_ = '%(centroid_openlocationcode)s%(sep)s%(height_in_openlocationcode_units).0f%(sep)s%(width_in_openlocationcode_units).0f'

# Regular expression for UBID codes.
RE_PATTERN_ = re.compile(r'^([^' + re.escape(SEPARATOR_) + r']+)' + re.escape(SEPARATOR_) + r'([1-9][0-9]*)' + re.escape(SEPARATOR_) + r'([1-9][0-9]*)$')

# The first group of a UBID code is the OLC for the geometric center of mass
# (i.e., centroid) of the building footprint.
RE_GROUP_CENTROID_ = 1

# The second group of the UBID code is the height in OLC grid units of the OLC
# bounding box for the building footprint.
RE_GROUP_HEIGHT_ = 2

# The second group of the UBID code is the width in OLC grid units of the OLC
# bounding box for the building footprint.
RE_GROUP_WIDTH_ = 3

@deprecation.deprecated(deprecated_in='1.1.0', removed_in=None, current_version=__version__, details='Use `buildingid.v3.decode` instead.')
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
    centroid_openlocationcode_CodeArea = openlocationcode.decode(match.group(RE_GROUP_CENTROID_))

    # Extract the size of the OLC bounding box and calculate the half-height and
    # half-width of the OLC code area for the OLC code for the centroid of the
    # building footprint.
    half_height = ((centroid_openlocationcode_CodeArea.latitudeHi - centroid_openlocationcode_CodeArea.latitudeLo) * float(match.group(RE_GROUP_HEIGHT_))) / 2.0
    half_width = ((centroid_openlocationcode_CodeArea.longitudeHi - centroid_openlocationcode_CodeArea.longitudeLo) * float(match.group(RE_GROUP_WIDTH_))) / 2.0

    # Construct and return the UBID code area.
    return CodeArea(centroid_openlocationcode_CodeArea, centroid_openlocationcode_CodeArea.latitudeLo - half_height, centroid_openlocationcode_CodeArea.longitudeLo - half_width, centroid_openlocationcode_CodeArea.latitudeHi + half_height, centroid_openlocationcode_CodeArea.longitudeHi + half_width, centroid_openlocationcode_CodeArea.codeLength)

@deprecation.deprecated(deprecated_in='1.1.0', removed_in=None, current_version=__version__, details='Use `buildingid.v3.encode` instead.')
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

    # Encode the OLC for the centroid of the building footprint.
    centroid_openlocationcode = openlocationcode.encode(latitudeCenter, longitudeCenter, **kwargs)

    # Decode the OLC for the centroid of the building footprint.
    centroid_openlocationcode_CodeArea = openlocationcode.decode(centroid_openlocationcode)

    # Calculate the size of the OLC bounding box for the building footprint,
    # assuming that the centroid of the building footprint is also the centroid
    # of the OLC bounding box.
    #
    # NOTE This introduces two issues. First, the centroid of the building
    # footprint is not necessarily the centroid of the corresponding OLC
    # bounding box (e.g., if the height or width is even). Second, the position
    # of the OLC bounding box (relative to the position of the centroid) is
    # not encoded in the UBID code (i.e., is lost).
    height = (latitudeHi - latitudeLo) / (centroid_openlocationcode_CodeArea.latitudeHi - centroid_openlocationcode_CodeArea.latitudeLo)
    width = (longitudeHi - longitudeLo) / (centroid_openlocationcode_CodeArea.longitudeHi - centroid_openlocationcode_CodeArea.longitudeLo)

    # Construct and return the UBID code.
    return FORMAT_STRING_ % {
        'sep': SEPARATOR_,
        'centroid_openlocationcode': centroid_openlocationcode,
        'height_in_openlocationcode_units': height,
        'width_in_openlocationcode_units': width,
    }

@deprecation.deprecated(deprecated_in='1.1.0', removed_in=None, current_version=__version__, details='Use `buildingid.v3.encodeCodeArea` instead.')
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

@deprecation.deprecated(deprecated_in='1.1.0', removed_in=None, current_version=__version__, details='Use `buildingid.v3.isValid` instead.')
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
    # (i) the OLC for the centroid of the building footprint is valid and (ii)
    # the height and width are greater than zero.
    return openlocationcode.isValid(match.group(RE_GROUP_CENTROID_)) and (int(match.group(RE_GROUP_HEIGHT_)) > 0) and (int(match.group(RE_GROUP_WIDTH_)) > 0)
