#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pnnl-buildingid: tests/test_v2.py
#
# Copyright (c) 2018, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE.txt and WARRANTY.txt for details.

import csv
import unittest

from buildingid.context import openlocationcode

import buildingid
import buildingid.v2
import buildingid.wkt

class MyTestCase(unittest.TestCase):
    def assertIsWithinTolerance(self, x, y, tolerance=0, precision=None):
        self.assertTrue(round(abs(abs(x) - abs(y)), precision) <= tolerance)

    def assertEqualCodeArea(self, x, y, **kwargs):
        self.assertIsNotNone(x)
        self.assertIsNotNone(y)
        self.assertIsWithinTolerance(x.latitudeLo, y.latitudeLo, **kwargs)
        self.assertIsWithinTolerance(x.longitudeLo, y.longitudeLo, **kwargs)
        self.assertIsWithinTolerance(x.latitudeHi, y.latitudeHi, **kwargs)
        self.assertIsWithinTolerance(x.longitudeHi, y.longitudeHi, **kwargs)
        self.assertIsWithinTolerance(x.latitudeCenter, y.latitudeCenter, **kwargs)
        self.assertIsWithinTolerance(x.longitudeCenter, y.longitudeCenter, **kwargs)
        self.assertEqual(x.codeLength, y.codeLength)
        self.assertIsWithinTolerance(x.child.latitudeLo, y.child.latitudeLo, **kwargs)
        self.assertIsWithinTolerance(x.child.longitudeLo, y.child.longitudeLo, **kwargs)
        self.assertIsWithinTolerance(x.child.latitudeHi, y.child.latitudeHi, **kwargs)
        self.assertIsWithinTolerance(x.child.longitudeHi, y.child.longitudeHi, **kwargs)
        self.assertIsWithinTolerance(x.child.latitudeCenter, y.child.latitudeCenter, **kwargs)
        self.assertIsWithinTolerance(x.child.longitudeCenter, y.child.longitudeCenter, **kwargs)
        self.assertEqual(x.child.codeLength, y.child.codeLength)

    def test_decode(self):
        with open('test_data/encode_and_decode.csv', mode='r') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                code = str(row['code.v2'])

                child = openlocationcode.CodeArea(float(row['child.latitudeLo']), float(row['child.longitudeLo']), float(row['child.latitudeHi']), float(row['child.longitudeHi']), int(row['child.codeLength']))

                code_area = buildingid.CodeArea(child, float(row['latitudeLo']), float(row['longitudeLo']), float(row['latitudeHi']), float(row['longitudeHi']), int(row['codeLength']))

                self.assertEqualCodeArea(buildingid.v2.decode(code), code_area, tolerance=float(row['tolerance']), precision=int(row['precision']))

    def test_encode(self):
        with open('test_data/encode_and_decode.csv', mode='r') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                code = str(row['code.v2'])

                child = openlocationcode.CodeArea(float(row['child.latitudeLo']), float(row['child.longitudeLo']), float(row['child.latitudeHi']), float(row['child.longitudeHi']), int(row['child.codeLength']))

                code_area = buildingid.CodeArea(child, float(row['latitudeLo']), float(row['longitudeLo']), float(row['latitudeHi']), float(row['longitudeHi']), int(row['codeLength']))
                code_area = code_area.resize()

                self.assertEqual(buildingid.v2.encode(code_area.latitudeLo, code_area.longitudeLo, code_area.latitudeHi, code_area.longitudeHi, child.latitudeCenter, child.longitudeCenter, codeLength=code_area.codeLength), code)

    def test_encodeCodeArea(self):
        with open('test_data/encode_and_decode.csv', mode='r') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                code = str(row['code.v2'])

                child = openlocationcode.CodeArea(float(row['child.latitudeLo']), float(row['child.longitudeLo']), float(row['child.latitudeHi']), float(row['child.longitudeHi']), int(row['child.codeLength']))

                code_area = buildingid.CodeArea(child, float(row['latitudeLo']), float(row['longitudeLo']), float(row['latitudeHi']), float(row['longitudeHi']), int(row['codeLength']))
                code_area = code_area.resize()

                self.assertEqual(buildingid.v2.encodeCodeArea(code_area), code)

    def test_isValid(self):
        with open('test_data/isValid.v2.csv', mode='r') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                code = str(row['code.v2'])

                boolval = True if str(row['isValid']) == "true" else False

                self.assertEqual(buildingid.v2.isValid(code), boolval)

    def test_wkt(self):
        with open('test_data/encode_and_decode.csv', mode='r') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                code = str(row['code.v2'])

                the_geom = str(row['the_geom'])

                self.assertEqual(buildingid.v2.encode(*buildingid.wkt.parse(the_geom), codeLength=int(row['codeLength'])), code)

if __name__ == '__main__':
    unittest.main()
