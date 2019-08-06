# -*- coding: utf-8 -*-
#
# pnnl-buildingid: buildingid/code.py
#
# Copyright (c) 2019, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE.txt and WARRANTY.txt for details.

import re
import typing

from .context import openlocationcode
from .validators import isValidCodeArea, isValidCodeLength, isValidLatitude, isValidLatitudeCenter, isValidLongitude, isValidLongitudeCenter

SEPARATOR_ = '-'

FORMAT_STRING_ = '%s-%.0f-%.0f-%.0f-%.0f'

RE_PATTERN_ = re.compile(r''.join([
    r'^',
    r'(',
        r'[', re.escape(openlocationcode.CODE_ALPHABET_[0:9]), r'][', re.escape(openlocationcode.CODE_ALPHABET_[0:18]), r']',
        r'(?:',
            re.escape(openlocationcode.PADDING_CHARACTER_), r'{6}',
            re.escape(openlocationcode.SEPARATOR_),
            r'(?:',
                re.escape(openlocationcode.PADDING_CHARACTER_), r'{2,}',
            r')?',
            r'|',
            r'[', re.escape(openlocationcode.CODE_ALPHABET_), r']{2}',
            r'(?:',
                re.escape(openlocationcode.PADDING_CHARACTER_), r'{4}',
                re.escape(openlocationcode.SEPARATOR_),
                r'(?:',
                    re.escape(openlocationcode.PADDING_CHARACTER_), r'{2,}',
                r')?',
                r'|',
                r'[', re.escape(openlocationcode.CODE_ALPHABET_), r']{2}',
                r'(?:',
                    re.escape(openlocationcode.PADDING_CHARACTER_), r'{2}',
                    re.escape(openlocationcode.SEPARATOR_),
                    r'(?:',
                        re.escape(openlocationcode.PADDING_CHARACTER_), r'{2,}',
                    r')?',
                    r'|',
                    r'[', re.escape(openlocationcode.CODE_ALPHABET_), r']{2}',
                    re.escape(openlocationcode.SEPARATOR_),
                    r'(?:',
                        re.escape(openlocationcode.PADDING_CHARACTER_), r'{2,}',
                        r'|',
                        r'[', re.escape(openlocationcode.CODE_ALPHABET_), r']{2,}',
                        re.escape(openlocationcode.PADDING_CHARACTER_), r'*',
                    r')?',
                r')',
            r')',
        r')',
    r')',
    re.escape(SEPARATOR_),
    r'(0|[1-9][0-9]*)',
    re.escape(SEPARATOR_),
    r'(0|[1-9][0-9]*)',
    re.escape(SEPARATOR_),
    r'(0|[1-9][0-9]*)',
    re.escape(SEPARATOR_),
    r'(0|[1-9][0-9]*)',
    r'$',
]), flags=re.IGNORECASE)

RE_GROUP_OPENLOCATIONCODE_ = 1

RE_GROUP_NORTH_ = 2

RE_GROUP_EAST_ = 3

RE_GROUP_SOUTH_ = 4

RE_GROUP_WEST_ = 5

Code = typing.NewType('Code', str)

class CodeArea(openlocationcode.CodeArea):
    def __init__(self, centroid: openlocationcode.CodeArea, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.centroid = centroid

    def encode(self) -> Code:
        return encode(self.latitudeLo, self.longitudeLo, self.latitudeHi, self.longitudeHi, self.centroid.latitudeCenter, self.centroid.longitudeCenter, codeLength=self.codeLength)

    def resize(self) -> 'CodeArea':
        halfHeight = float(self.centroid.latitudeHi - self.centroid.latitudeLo) / 2
        halfWidth = float(self.centroid.longitudeHi - self.centroid.longitudeLo) / 2

        return CodeArea(self.centroid, self.latitudeLo + halfHeight, self.longitudeLo + halfWidth, self.latitudeHi - halfHeight, self.longitudeHi - halfWidth, codeLength=self.codeLength)

def decode(code: Code) -> CodeArea:
    match = isValid_(code)

    if match is None:
        raise ValueError('buildingid.code.decode - Invalid code')

    codeAreaCenter = openlocationcode.decode(match.group(RE_GROUP_OPENLOCATIONCODE_))
    assert isValidCodeArea(codeAreaCenter), 'buildingid.code.decode - Invalid code area'

    codeAreaCenterHeight = codeAreaCenter.latitudeHi - codeAreaCenter.latitudeLo
    assert codeAreaCenterHeight >= 0, 'buildingid.code.decode - Invalid code - Negative height'

    codeAreaCenterWidth = codeAreaCenter.longitudeHi - codeAreaCenter.longitudeLo
    assert codeAreaCenterWidth >= 0, 'buildingid.code.decode - Invalid code - Negative width'

    latitudeLo = codeAreaCenter.latitudeLo - (int(match.group(RE_GROUP_SOUTH_)) * codeAreaCenterHeight)
    latitudeHi = codeAreaCenter.latitudeHi + (int(match.group(RE_GROUP_NORTH_)) * codeAreaCenterHeight)
    assert isValidLatitude(latitudeLo, latitudeHi), 'buildingid.code.decode - Invalid code - Invalid latitude coordinates'

    longitudeLo = codeAreaCenter.longitudeLo - (int(match.group(RE_GROUP_WEST_)) * codeAreaCenterWidth)
    longitudeHi = codeAreaCenter.longitudeHi + (int(match.group(RE_GROUP_EAST_)) * codeAreaCenterWidth)
    assert isValidLongitude(longitudeLo, longitudeHi), 'buildingid.code.decode - Invalid code - Invalid longitude coordinates'

    return CodeArea(codeAreaCenter, latitudeLo, longitudeLo, latitudeHi, longitudeHi, codeAreaCenter.codeLength)

def encode(latitudeLo: float, longitudeLo: float, latitudeHi: float, longitudeHi: float, latitudeCenter: float, longitudeCenter: float, codeLength: int = openlocationcode.PAIR_CODE_LENGTH_) -> Code:
    assert isValidCodeLength(codeLength), 'buildingid.code.encode - Invalid code length'
    assert isValidLatitudeCenter(latitudeLo, latitudeHi, latitudeCenter), 'buildingid.code.encode - Invalid latitude coordinates'
    assert isValidLongitudeCenter(longitudeLo, longitudeHi, longitudeCenter), 'buildingid.code.encode - Invalid longitude coordinates'

    olcNortheast = openlocationcode.encode(latitudeHi, longitudeHi, codeLength=codeLength)
    codeAreaNortheast = openlocationcode.decode(olcNortheast)
    assert isValidCodeArea(codeAreaNortheast), 'buildingid.code.encode - Invalid code area (northeast)'

    olcSouthwest = openlocationcode.encode(latitudeLo, longitudeLo, codeLength=codeLength)
    codeAreaSouthwest = openlocationcode.decode(olcSouthwest)
    assert isValidCodeArea(codeAreaSouthwest), 'buildingid.code.encode - Invalid code area (southwest)'

    olcCenter = openlocationcode.encode(latitudeCenter, longitudeCenter, codeLength=codeLength)
    codeAreaCenter = openlocationcode.decode(olcCenter)
    assert isValidCodeArea(codeAreaCenter), 'buildingid.code.encode - Invalid code area (center)'

    codeAreaCenterHeight = codeAreaCenter.latitudeHi - codeAreaCenter.latitudeLo
    assert codeAreaCenterHeight >= 0, 'buildingid.code.encode - Invalid code - Negative height'

    codeAreaCenterWidth = codeAreaCenter.longitudeHi - codeAreaCenter.longitudeLo
    assert codeAreaCenterWidth >= 0, 'buildingid.code.encode - Invalid code - Negative width'

    olcCountNorth = (codeAreaNortheast.latitudeHi - codeAreaCenter.latitudeHi) / codeAreaCenterHeight
    assert olcCountNorth >= 0, 'buildingid.code.encode - Negative extent (north)'

    olcCountSouth = (codeAreaCenter.latitudeLo - codeAreaSouthwest.latitudeLo) / codeAreaCenterHeight
    assert olcCountSouth >= 0, 'buildingid.code.encode - Negative extent (south)'

    olcCountEast = (codeAreaNortheast.longitudeHi - codeAreaCenter.longitudeHi) / codeAreaCenterWidth
    assert olcCountEast >= 0, 'buildingid.code.encode - Negative extent (east)'

    olcCountWest = (codeAreaCenter.longitudeLo - codeAreaSouthwest.longitudeLo) / codeAreaCenterWidth
    assert olcCountWest >= 0, 'buildingid.code.encode - Negative extent (west)'

    return Code(FORMAT_STRING_ % (olcCenter, olcCountNorth, olcCountEast, olcCountSouth, olcCountWest))

def isValid(code: Code) -> bool:
    return isValid_(code) is not None

def isValid_(code: Code) -> typing.Optional[typing.Match]:
    if code is None:
        return None

    match = RE_PATTERN_.match(str(code))

    if (match is None) or not openlocationcode.isValid(match.group(RE_GROUP_OPENLOCATIONCODE_)):
        return None

    return match
