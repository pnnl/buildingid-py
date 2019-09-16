# -*- coding: utf-8 -*-
#
# pnnl-buildingid: tests/buildingid/test_validators.py
#
# Copyright (c) 2019, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE.txt and WARRANTY.txt for details.

import unittest

from openlocationcode import openlocationcode

from ..context import buildingid
from buildingid.validators import isValidCodeArea, isValidCodeLength, isValidLatitude, isValidLatitudeCenter, isValidLongitude, isValidLongitudeCenter

class TestValidators(unittest.TestCase):
    def test_buildingid_validators_isValidCodeArea(self):
        self.assertTrue(isValidCodeArea(openlocationcode.CodeArea(0, 0, 1, 1, codeLength=openlocationcode.PAIR_CODE_LENGTH_)))

    def test_buildingid_validators_isValidCodeLength(self):
        self.assertFalse(isValidCodeLength(0))
        self.assertFalse(isValidCodeLength(1))
        self.assertTrue(isValidCodeLength(2))
        self.assertFalse(isValidCodeLength(3))
        self.assertTrue(isValidCodeLength(4))
        self.assertFalse(isValidCodeLength(5))
        self.assertTrue(isValidCodeLength(6))
        self.assertFalse(isValidCodeLength(7))
        self.assertTrue(isValidCodeLength(8))
        self.assertFalse(isValidCodeLength(9))
        self.assertTrue(isValidCodeLength(10))
        self.assertTrue(isValidCodeLength(11))

    def test_buildingid_validators_isValidLatitude(self):
        self.assertTrue(isValidLatitude(0, 1))
        self.assertFalse(isValidLatitude(1, 0))

    def test_buildingid_validators_isValidLatitudeCenter(self):
        self.assertTrue(isValidLatitudeCenter(0, 2, 1))
        self.assertFalse(isValidLatitudeCenter(0, 1, 2))

    def test_buildingid_validators_isValidLongitude(self):
        self.assertTrue(isValidLongitude(0, 1))
        self.assertFalse(isValidLongitude(1, 0))

    def test_buildingid_validators_isValidLongitudeCenter(self):
        self.assertTrue(isValidLongitudeCenter(0, 2, 1))
        self.assertFalse(isValidLongitudeCenter(0, 1, 2))

if __name__ == '__main__':
    unittest.main()
