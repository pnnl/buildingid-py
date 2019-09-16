# -*- coding: utf-8 -*-
#
# pnnl-buildingid: buildingid/validators.py
#
# Copyright (c) 2019, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE.txt and WARRANTY.txt for details.

from openlocationcode import openlocationcode

def isValidCodeArea(codeArea: openlocationcode.CodeArea) -> bool:
    return isValidCodeLength(codeArea.codeLength) and isValidLatitudeCenter(codeArea.latitudeLo, codeArea.latitudeHi, codeArea.latitudeCenter) and isValidLongitudeCenter(codeArea.longitudeLo, codeArea.longitudeHi, codeArea.longitudeCenter)

def isValidCodeLength(codeLength: int) -> bool:
    return (codeLength >= 2) and ((codeLength >= openlocationcode.PAIR_CODE_LENGTH_) or (codeLength % 2 == 0))

def isValidLatitude(latitudeLo: float, latitudeHi: float) -> bool:
    return -openlocationcode.LATITUDE_MAX_ <= latitudeLo <= latitudeHi <= openlocationcode.LATITUDE_MAX_

def isValidLatitudeCenter(latitudeLo: float, latitudeHi: float, latitudeCenter: float) -> bool:
    return -openlocationcode.LATITUDE_MAX_ <= latitudeLo <= latitudeCenter <= latitudeHi <= openlocationcode.LATITUDE_MAX_

def isValidLongitude(longitudeLo: float, longitudeHi: float) -> bool:
    return -openlocationcode.LONGITUDE_MAX_ <= longitudeLo <= longitudeHi <= openlocationcode.LONGITUDE_MAX_

def isValidLongitudeCenter(longitudeLo: float, longitudeHi: float, longitudeCenter: float) -> bool:
    return -openlocationcode.LONGITUDE_MAX_ <= longitudeLo <= longitudeCenter <= longitudeHi <= openlocationcode.LONGITUDE_MAX_
