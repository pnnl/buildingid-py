# -*- coding: utf-8 -*-
#
# pnnl-buildingid: tests/buildingid/test_code.py
#
# Copyright (c) 2019, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE.txt and WARRANTY.txt for details.

import unittest

from openlocationcode import openlocationcode
import shapely.wkt

from ..context import buildingid
from buildingid.code import RE_PATTERN_, decode, encode, isValid

class TestCode(unittest.TestCase):
    def test_buildingid_code_decode(self):
        with self.assertRaises(ValueError):
            decode(None)

        with self.assertRaises(ValueError):
            decode('')

        # # TODO
        # decode('6FG22222+22-0-0-0-0')

        # # TODO
        # decode('6FQ72222+22-40000-40000-40000-40000')

    def test_buildingid_code_encode_when_geom_is_wkt_POINT(self):
        geom = shapely.wkt.loads('POINT (0 0)')

        (geom_bounds_min_x, geom_bounds_min_y, geom_bounds_max_x, geom_bounds_max_y) = geom.bounds

        geom_centroid = geom.centroid

        code = encode(geom_bounds_min_y, geom_bounds_min_x, geom_bounds_max_y, geom_bounds_max_x, geom_centroid.y, geom_centroid.x, codeLength=openlocationcode.PAIR_CODE_LENGTH_)

        self.assertEqual('6FG22222+22-0-0-0-0', code)

    def test_buildingid_code_encode_when_geom_is_wkt_POLYGON(self):
        geom = shapely.wkt.loads('POLYGON ((0 0, 0 10, 10 10, 10 0, 0 0))')

        (geom_bounds_min_x, geom_bounds_min_y, geom_bounds_max_x, geom_bounds_max_y) = geom.bounds

        geom_centroid = geom.centroid

        code = encode(geom_bounds_min_y, geom_bounds_min_x, geom_bounds_max_y, geom_bounds_max_x, geom_centroid.y, geom_centroid.x, codeLength=openlocationcode.PAIR_CODE_LENGTH_)

        self.assertEqual('6FQ72222+22-40000-40000-40000-40000', code)

    def test_buildingid_code_CodeArea_encode(self):
        geom = shapely.wkt.loads('POINT (0 0)')

        (geom_bounds_min_x, geom_bounds_min_y, geom_bounds_max_x, geom_bounds_max_y) = geom.bounds

        geom_centroid = geom.centroid

        origCode = encode(geom_bounds_min_y, geom_bounds_min_x, geom_bounds_max_y, geom_bounds_max_x, geom_centroid.y, geom_centroid.x, codeLength=openlocationcode.PAIR_CODE_LENGTH_)

        origCodeArea = decode(origCode)

        newCodeArea = origCodeArea.resize()

        newCode = newCodeArea.encode()

        self.assertEqual(origCode, newCode)

    def test_buildingid_code_isValid(self):
        self.assertFalse(isValid(None))
        self.assertFalse(isValid(''))
        self.assertTrue(isValid('6FG22222+22-0-0-0-0'))
        self.assertTrue(isValid('6FQ72222+22-40000-40000-40000-40000'))

    def test_buildingid_code_re(self):
        self.assertEqual(None, RE_PATTERN_.match('00000000+-0-0-0-0'))
        self.assertEqual(None, RE_PATTERN_.match('00220000+-0-0-0-0'))
        self.assertEqual(None, RE_PATTERN_.match('00002200+-0-0-0-0'))
        self.assertEqual(None, RE_PATTERN_.match('00000022+-0-0-0-0'))
        self.assertEqual(None, RE_PATTERN_.match('00000000+22-0-0-0-0'))
        self.assertNotEqual(None, RE_PATTERN_.match('22000000+-0-0-0-0'))
        self.assertEqual(None, RE_PATTERN_.match('22000000+0-0-0-0-0'))
        self.assertNotEqual(None, RE_PATTERN_.match('22000000+00-0-0-0-0'))
        self.assertNotEqual(None, RE_PATTERN_.match('22000000+000-0-0-0-0'))
        self.assertNotEqual(None, RE_PATTERN_.match('22220000+-0-0-0-0'))
        self.assertEqual(None, RE_PATTERN_.match('22220000+0-0-0-0-0'))
        self.assertNotEqual(None, RE_PATTERN_.match('22220000+00-0-0-0-0'))
        self.assertNotEqual(None, RE_PATTERN_.match('22220000+000-0-0-0-0'))
        self.assertNotEqual(None, RE_PATTERN_.match('22222200+-0-0-0-0'))
        self.assertEqual(None, RE_PATTERN_.match('22222200+0-0-0-0-0'))
        self.assertNotEqual(None, RE_PATTERN_.match('22222200+00-0-0-0-0'))
        self.assertNotEqual(None, RE_PATTERN_.match('22222200+000-0-0-0-0'))
        self.assertNotEqual(None, RE_PATTERN_.match('22222222+-0-0-0-0'))
        self.assertEqual(None, RE_PATTERN_.match('22222222+0-0-0-0-0'))
        self.assertNotEqual(None, RE_PATTERN_.match('22222222+00-0-0-0-0'))
        self.assertNotEqual(None, RE_PATTERN_.match('22222222+000-0-0-0-0'))
        self.assertEqual(None, RE_PATTERN_.match('22222222+2-0-0-0-0'))
        self.assertEqual(None, RE_PATTERN_.match('22222222+0-0-0-0-0'))
        self.assertNotEqual(None, RE_PATTERN_.match('22222222+00-0-0-0-0'))
        self.assertEqual(None, RE_PATTERN_.match('22222222+002-0-0-0-0'))
        self.assertNotEqual(None, RE_PATTERN_.match('22222222+22-0-0-0-0'))
        self.assertNotEqual(None, RE_PATTERN_.match('22222222+222-0-0-0-0'))
        self.assertEqual(None, RE_PATTERN_.match('22222222+2202-0-0-0-0'))
        self.assertNotEqual(None, RE_PATTERN_.match('22222222+2220-0-0-0-0'))

if __name__ == '__main__':
    unittest.main()
