# -*- coding: utf-8 -*-
#
# pnnl-buildingid: tests/buildingid/test_code_area.py
#
# Copyright (c) 2019, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE.txt and WARRANTY.txt for details.

import unittest

from openlocationcode import openlocationcode

from ..context import buildingid
from buildingid.code import CodeArea

class TestCodeArea(unittest.TestCase):
    def test_buildingid_code_area_area(self):
        codeArea = CodeArea(openlocationcode.CodeArea(-1.0, -1.0, 1.0, 1.0, codeLength=openlocationcode.PAIR_CODE_LENGTH_), -10.0, -10.0, 10.0, 10.0, codeLength=openlocationcode.PAIR_CODE_LENGTH_)

        self.assertEqual(codeArea.area, 400.0)

    def test_buildingid_code_area_intersection(self):
        codeArea = CodeArea(openlocationcode.CodeArea(-1.0, -1.0, 1.0, 1.0, codeLength=openlocationcode.PAIR_CODE_LENGTH_), -10.0, -10.0, 10.0, 10.0, codeLength=openlocationcode.PAIR_CODE_LENGTH_)
        otherCodeArea = CodeArea(openlocationcode.CodeArea(-1.0, -1.0, 1.0, 1.0, codeLength=openlocationcode.PAIR_CODE_LENGTH_), -5.0, -5.0, 15.0, 15.0, codeLength=openlocationcode.PAIR_CODE_LENGTH_)

        bbox = codeArea.intersection(otherCodeArea)

        self.assertEqual(bbox[0], -5.0)
        self.assertEqual(bbox[1], -5.0)
        self.assertEqual(bbox[2], 10.0)
        self.assertEqual(bbox[3], 10.0)

    def test_buildingid_code_area_jaccard(self):
        codeArea = CodeArea(openlocationcode.CodeArea(-1.0, -1.0, 1.0, 1.0, codeLength=openlocationcode.PAIR_CODE_LENGTH_), -10.0, -10.0, 10.0, 10.0, codeLength=openlocationcode.PAIR_CODE_LENGTH_)
        otherCodeArea = CodeArea(openlocationcode.CodeArea(-1.0, -1.0, 1.0, 1.0, codeLength=openlocationcode.PAIR_CODE_LENGTH_), -5.0, -5.0, 15.0, 15.0, codeLength=openlocationcode.PAIR_CODE_LENGTH_)

        self.assertEqual(codeArea.jaccard(otherCodeArea), 225.0 / (400.0 + 400.0 - 225.0)) # OK: intersects

        otherCodeArea = CodeArea(openlocationcode.CodeArea(-1.0, -1.0, 1.0, 1.0, codeLength=openlocationcode.PAIR_CODE_LENGTH_), -20.0, -20.0, -10.0, -10.0, codeLength=openlocationcode.PAIR_CODE_LENGTH_)

        self.assertEqual(codeArea.jaccard(otherCodeArea), 0.0) # OK: adjacent

        otherCodeArea = CodeArea(openlocationcode.CodeArea(-1.0, -1.0, 1.0, 1.0, codeLength=openlocationcode.PAIR_CODE_LENGTH_), -30.0, -30.0, -20.0, -20.0, codeLength=openlocationcode.PAIR_CODE_LENGTH_)

        self.assertEqual(codeArea.jaccard(otherCodeArea), None) # Fail: no intersection

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
