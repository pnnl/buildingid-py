# -*- coding: utf-8 -*-
#
# pnnl-buildingid: buildingid/v2.py
#
# Copyright (c) 2018, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE.txt and WARRANTY.txt for details.

from .context import openlocationcode

from .code_area import CodeArea
from .version import __version__

import deprecation

# The number of OLC codes in a UBID code.
COUNT_ = 3

# The index for the OLC code for the centroid of the building footprint.
INDEX_CENTROID_ = 0

# The index for the OLC code for the northwest corner of the OLC bounding box
# for the building footprint.
INDEX_NORTHWEST_ = 1

# The index for the OLC code for the southeast corner of the OLC bounding box
# for the building footprint.
INDEX_SOUTHEAST_ = 2

# The separator for OLC codes in a UBID code.
SEPARATOR_ = '-'

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

    # If the UBID code is undefined, raise an error.
    if code is None:
        return ValueError('Invalid UBID')

    # Split the UBID code string using the separator.
    openlocationcodes = code.split(SEPARATOR_)

    # Ensure that the UBID code contains the correct number of OLC codes.
    if len(openlocationcodes) != COUNT_:
        raise ValueError('Invalid UBID: Incorrect Open Location Code count (expected: {0}; received: {1})'.format(COUNT_, len(openlocationcodes)))

    # Decode the OLC codes for the centroid of the building footprint and the
    # northwest and southeast corners of the OLC bounding box for the building
    # footprint.
    centroid_openlocationcode_CodeArea = openlocationcode.decode(openlocationcodes[INDEX_CENTROID_])
    northwest_openlocationcode_CodeArea = openlocationcode.decode(openlocationcodes[INDEX_NORTHWEST_])
    southeast_openlocationcode_CodeArea = openlocationcode.decode(openlocationcodes[INDEX_SOUTHEAST_])

    # Ensure that the OLC code lengths are equal.
    if not (centroid_openlocationcode_CodeArea.codeLength == northwest_openlocationcode_CodeArea.codeLength == southeast_openlocationcode_CodeArea.codeLength):
        raise ValueError('Invalid UBID: Code lengths must be equal (received: ({0},{1},{2}))'.format(centroid_openlocationcode_CodeArea.codeLength, northwest_openlocationcode_CodeArea.codeLength, southeast_openlocationcode_CodeArea.codeLength))

    # Construct and return the UBID code area.
    return CodeArea(centroid_openlocationcode_CodeArea, southeast_openlocationcode_CodeArea.latitudeLo, northwest_openlocationcode_CodeArea.longitudeLo, northwest_openlocationcode_CodeArea.latitudeHi, southeast_openlocationcode_CodeArea.longitudeHi, centroid_openlocationcode_CodeArea.codeLength)

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

    # Encode the OLC codes for the centroid of the building footprint and the
    # northwest and southeast corners of the OLC bounding box for the building
    # footprint.
    centroid_openlocationcode = openlocationcode.encode(latitudeCenter, longitudeCenter, **kwargs)
    northwest_openlocationcode = openlocationcode.encode(latitudeHi, longitudeLo, **kwargs)
    southeast_openlocationcode = openlocationcode.encode(latitudeLo, longitudeHi, **kwargs)

    # Construct and return the result.
    openlocationcodes = [None] * COUNT_
    openlocationcodes[INDEX_CENTROID_] = centroid_openlocationcode
    openlocationcodes[INDEX_NORTHWEST_] = northwest_openlocationcode
    openlocationcodes[INDEX_SOUTHEAST_] = southeast_openlocationcode
    return SEPARATOR_.join(openlocationcodes)

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

    # Split the UBID code string using the separator.
    openlocationcodes = code.split(SEPARATOR_)

    # UBID codes with the incorrect number of OLC codes are invalid.
    if len(openlocationcodes) != COUNT_:
        return False

    try:
        # Decode the OLC codes for the centroid of the building footprint and the
        # northwest and southeast corners of the OLC bounding box for the building
        # footprint.
        centroid_openlocationcode = openlocationcode.decode(openlocationcodes[INDEX_CENTROID_])
        northwest_openlocationcode = openlocationcode.decode(openlocationcodes[INDEX_NORTHWEST_])
        southeast_openlocationcode = openlocationcode.decode(openlocationcodes[INDEX_SOUTHEAST_])
    except:
        # If any OLC cannot be decoded, then the UBID code is invalid.
        return False
    else:
        # A UBID code is valid if the latitudes of the centroid of the building
        # footprint is within the bounds of the latitudes of the northwest and
        # southeast corners of the OLC bounding box for the building footprint.
        isValidLatitude = southeast_openlocationcode.latitudeLo <= centroid_openlocationcode.latitudeCenter <= northwest_openlocationcode.latitudeHi

        # A UBID code is valid if the longitudes of the centroid of the building
        # footprint is within the bounds of the longitudes of the northwest and
        # southeast corners of the OLC bounding box for the building footprint.
        isValidLongitude = northwest_openlocationcode.longitudeLo <= centroid_openlocationcode.longitudeCenter <= southeast_openlocationcode.longitudeHi

        # A UBID code is valid if the OLC code lengths are equal.
        isValidCodeLength = centroid_openlocationcode.codeLength == northwest_openlocationcode.codeLength == southeast_openlocationcode.codeLength

        # Logical conjunction of predicates.
        return isValidLatitude and isValidLongitude and isValidCodeLength
