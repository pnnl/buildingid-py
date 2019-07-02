# -*- coding: utf-8 -*-
#
# pnnl-buildingid: tests/buildingid/test_code_area.py
#
# Copyright (c) 2019, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE.txt and WARRANTY.txt for details.

import unittest

from ..context import buildingid
from buildingid.code import CodeArea
from buildingid.context import openlocationcode

class TestCodeArea(unittest.TestCase):
    def test_buildingid_code_area_resize(self):
        origCodeArea = CodeArea(openlocationcode.CodeArea(-1.0, -1.0, 1.0, 1.0, codeLength=openlocationcode.PAIR_CODE_LENGTH_), -10.0, -10.0, 10.0, 10.0, codeLength=openlocationcode.PAIR_CODE_LENGTH_)

        newCodeArea = origCodeArea.resize()

        self.assertEqual(newCodeArea.centroid, origCodeArea.centroid)
        self.assertEqual(newCodeArea.latitudeLo, -9.0)
        self.assertEqual(newCodeArea.longitudeLo, -9.0)
        self.assertEqual(newCodeArea.latitudeHi, 9.0)
        self.assertEqual(newCodeArea.longitudeHi, 9.0)
        self.assertEqual(newCodeArea.codeLength, origCodeArea.codeLength)

if __name__ == '__main__':
    unittest.main()
