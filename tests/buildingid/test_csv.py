# -*- coding: utf-8 -*-
#
# pnnl-buildingid: tests/buildingid/test_csv.py
#
# Copyright (c) 2019, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE.txt and WARRANTY.txt for details.

import io
import re
import unittest

from ..context import buildingid
from buildingid.command_line.dict_decoders import LatLngDictDecoder, WKBDictDecoder, WKTDictDecoder
from buildingid.command_line.dict_encoders import BaseGeometryDictEncoder, ErrorDictEncoder
from buildingid.command_line.dict_pipe import DictPipe
from buildingid.command_line.exceptions import FieldNotFoundError, FieldNotUniqueError
from buildingid.context import openlocationcode

class TestCSV(unittest.TestCase):
    def test_buildingid_csv_DictPipe_LatLngDictDecoder_FieldNotFoundError(self):
        decoder_in = LatLngDictDecoder('Latitude', 'Longitude')

        encoder_out = BaseGeometryDictEncoder('UBID', openlocationcode.PAIR_CODE_LENGTH_)

        encoder_err = ErrorDictEncoder('UBID')

        dict_pipe = DictPipe(decoder_in, encoder_out, encoder_err)

        io_in = io.StringIO('x,Longitude')
        io_out = io.StringIO('')
        io_err = io.StringIO('')

        with self.assertRaisesRegex(FieldNotFoundError, re.escape('field \'Latitude\' is not defined')):
            dict_pipe.run(io_in, io_out, io_err, args_in=[], kwargs_in={}, args_out=[], kwargs_out={})

        io_in = io.StringIO('Latitude,x')
        io_out = io.StringIO('')
        io_err = io.StringIO('')

        with self.assertRaisesRegex(FieldNotFoundError, re.escape('field \'Longitude\' is not defined')):
            dict_pipe.run(io_in, io_out, io_err, args_in=[], kwargs_in={}, args_out=[], kwargs_out={})

    def test_buildingid_csv_DictPipe_WKBDictDecoder_FieldNotFoundError(self):
        decoder_in = WKBDictDecoder('WKB')

        encoder_out = BaseGeometryDictEncoder('UBID', openlocationcode.PAIR_CODE_LENGTH_)

        encoder_err = ErrorDictEncoder('UBID')

        dict_pipe = DictPipe(decoder_in, encoder_out, encoder_err)

        io_in = io.StringIO('x')
        io_out = io.StringIO('')
        io_err = io.StringIO('')

        with self.assertRaisesRegex(FieldNotFoundError, re.escape('field \'WKB\' is not defined')):
            dict_pipe.run(io_in, io_out, io_err, args_in=[], kwargs_in={}, args_out=[], kwargs_out={})

    def test_buildingid_csv_DictPipe_WKTDictDecoder_FieldNotFoundError(self):
        decoder_in = WKTDictDecoder('WKT')

        encoder_out = BaseGeometryDictEncoder('UBID', openlocationcode.PAIR_CODE_LENGTH_)

        encoder_err = ErrorDictEncoder('UBID')

        dict_pipe = DictPipe(decoder_in, encoder_out, encoder_err)

        io_in = io.StringIO('x')
        io_out = io.StringIO('')
        io_err = io.StringIO('')

        with self.assertRaisesRegex(FieldNotFoundError, re.escape('field \'WKT\' is not defined')):
            dict_pipe.run(io_in, io_out, io_err, args_in=[], kwargs_in={}, args_out=[], kwargs_out={})

    def test_buildingid_csv_DictPipe_LatLngDictDecoder_FieldNotUniqueError(self):
        decoder_in = LatLngDictDecoder('Latitude', 'Longitude')

        encoder_out = BaseGeometryDictEncoder('UBID', openlocationcode.PAIR_CODE_LENGTH_)

        encoder_err = ErrorDictEncoder('UBID')

        dict_pipe = DictPipe(decoder_in, encoder_out, encoder_err)

        io_in = io.StringIO('Latitude,Longitude,UBID')
        io_out = io.StringIO('')
        io_err = io.StringIO('')

        with self.assertRaisesRegex(FieldNotUniqueError, re.escape('field \'UBID\' has already been taken')):
            dict_pipe.run(io_in, io_out, io_err, args_in=[], kwargs_in={}, args_out=[], kwargs_out={})

        io_in = io.StringIO('Latitude,Longitude,UBID_Error_Name')
        io_out = io.StringIO('')
        io_err = io.StringIO('')

        with self.assertRaisesRegex(FieldNotUniqueError, re.escape('field \'UBID_Error_Name\' has already been taken')):
            dict_pipe.run(io_in, io_out, io_err, args_in=[], kwargs_in={}, args_out=[], kwargs_out={})

        io_in = io.StringIO('Latitude,Longitude,UBID_Error_Message')
        io_out = io.StringIO('')
        io_err = io.StringIO('')

        with self.assertRaisesRegex(FieldNotUniqueError, re.escape('field \'UBID_Error_Message\' has already been taken')):
            dict_pipe.run(io_in, io_out, io_err, args_in=[], kwargs_in={}, args_out=[], kwargs_out={})

    def test_buildingid_csv_DictPipe_WKBDictDecoder_FieldNotUniqueError(self):
        decoder_in = WKBDictDecoder('WKB')

        encoder_out = BaseGeometryDictEncoder('UBID', openlocationcode.PAIR_CODE_LENGTH_)

        encoder_err = ErrorDictEncoder('UBID')

        dict_pipe = DictPipe(decoder_in, encoder_out, encoder_err)

        io_in = io.StringIO('WKB,UBID')
        io_out = io.StringIO('')
        io_err = io.StringIO('')

        with self.assertRaisesRegex(FieldNotUniqueError, re.escape('field \'UBID\' has already been taken')):
            dict_pipe.run(io_in, io_out, io_err, args_in=[], kwargs_in={}, args_out=[], kwargs_out={})

        io_in = io.StringIO('WKB,UBID_Error_Name')
        io_out = io.StringIO('')
        io_err = io.StringIO('')

        with self.assertRaisesRegex(FieldNotUniqueError, re.escape('field \'UBID_Error_Name\' has already been taken')):
            dict_pipe.run(io_in, io_out, io_err, args_in=[], kwargs_in={}, args_out=[], kwargs_out={})

        io_in = io.StringIO('WKB,UBID_Error_Message')
        io_out = io.StringIO('')
        io_err = io.StringIO('')

        with self.assertRaisesRegex(FieldNotUniqueError, re.escape('field \'UBID_Error_Message\' has already been taken')):
            dict_pipe.run(io_in, io_out, io_err, args_in=[], kwargs_in={}, args_out=[], kwargs_out={})

    def test_buildingid_csv_DictPipe_WKTDictDecoder_FieldNotUniqueError(self):
        decoder_in = WKTDictDecoder('WKT')

        encoder_out = BaseGeometryDictEncoder('UBID', openlocationcode.PAIR_CODE_LENGTH_)

        encoder_err = ErrorDictEncoder('UBID')

        dict_pipe = DictPipe(decoder_in, encoder_out, encoder_err)

        io_in = io.StringIO('WKT,UBID')
        io_out = io.StringIO('')
        io_err = io.StringIO('')

        with self.assertRaisesRegex(FieldNotUniqueError, re.escape('field \'UBID\' has already been taken')):
            dict_pipe.run(io_in, io_out, io_err, args_in=[], kwargs_in={}, args_out=[], kwargs_out={})

        io_in = io.StringIO('WKT,UBID_Error_Name')
        io_out = io.StringIO('')
        io_err = io.StringIO('')

        with self.assertRaisesRegex(FieldNotUniqueError, re.escape('field \'UBID_Error_Name\' has already been taken')):
            dict_pipe.run(io_in, io_out, io_err, args_in=[], kwargs_in={}, args_out=[], kwargs_out={})

        io_in = io.StringIO('WKT,UBID_Error_Message')
        io_out = io.StringIO('')
        io_err = io.StringIO('')

        with self.assertRaisesRegex(FieldNotUniqueError, re.escape('field \'UBID_Error_Message\' has already been taken')):
            dict_pipe.run(io_in, io_out, io_err, args_in=[], kwargs_in={}, args_out=[], kwargs_out={})

    def test_buildingid_csv_DictPipe_LatLngDictDecoder(self):
        decoder_in = LatLngDictDecoder('Latitude', 'Longitude')

        encoder_out = BaseGeometryDictEncoder('UBID', openlocationcode.PAIR_CODE_LENGTH_)

        encoder_err = ErrorDictEncoder('UBID')

        dict_pipe = DictPipe(decoder_in, encoder_out, encoder_err)

        io_in = io.StringIO('Latitude,Longitude\r\n0,0\r\n')
        io_out = io.StringIO('')
        io_err = io.StringIO('')

        dict_pipe.run(io_in, io_out, io_err, args_in=[], kwargs_in={}, args_out=[], kwargs_out={})

        self.assertEqual('Latitude,Longitude\r\n0,0\r\n', io_in.getvalue())
        self.assertEqual('Latitude,Longitude,UBID\r\n0,0,6FG22222+22-0-0-0-0\r\n', io_out.getvalue())
        self.assertEqual('', io_err.getvalue())

        io_in = io.StringIO('Latitude,Longitude\r\nx,x\r\n')
        io_out = io.StringIO('')
        io_err = io.StringIO('')

        dict_pipe.run(io_in, io_out, io_err, args_in=[], kwargs_in={}, args_out=[], kwargs_out={})

        self.assertEqual('Latitude,Longitude\r\nx,x\r\n', io_in.getvalue())
        self.assertEqual('', io_out.getvalue())
        self.assertEqual('Latitude,Longitude,UBID_Error_Name,UBID_Error_Message\r\nx,x,ValueError,could not convert string to float: \'x\'\r\n', io_err.getvalue())

    def test_buildingid_csv_DictPipe_WKBDictDecoder(self):
        decoder_in = WKBDictDecoder('WKB')

        encoder_out = BaseGeometryDictEncoder('UBID', openlocationcode.PAIR_CODE_LENGTH_)

        encoder_err = ErrorDictEncoder('UBID')

        dict_pipe = DictPipe(decoder_in, encoder_out, encoder_err)

        io_in = io.StringIO('WKB\r\n010100000000000000000000000000000000000000\r\n')
        io_out = io.StringIO('')
        io_err = io.StringIO('')

        dict_pipe.run(io_in, io_out, io_err, args_in=[], kwargs_in={}, args_out=[], kwargs_out={})

        self.assertEqual('WKB\r\n010100000000000000000000000000000000000000\r\n', io_in.getvalue())
        self.assertEqual('WKB,UBID\r\n010100000000000000000000000000000000000000,6FG22222+22-0-0-0-0\r\n', io_out.getvalue())
        self.assertEqual('', io_err.getvalue())

        io_in = io.StringIO('WKB\r\nx\r\n')
        io_out = io.StringIO('')
        io_err = io.StringIO('')

        dict_pipe.run(io_in, io_out, io_err, args_in=[], kwargs_in={}, args_out=[], kwargs_out={})

        self.assertEqual('WKB\r\nx\r\n', io_in.getvalue())
        self.assertEqual('', io_out.getvalue())
        self.assertEqual('WKB,UBID_Error_Name,UBID_Error_Message\r\nx,WKBReadingError,Could not create geometry because of errors while reading input.\r\n', io_err.getvalue())

    def test_buildingid_csv_DictPipe_WKTDictDecoder(self):
        decoder_in = WKTDictDecoder('WKT')

        encoder_out = BaseGeometryDictEncoder('UBID', openlocationcode.PAIR_CODE_LENGTH_)

        encoder_err = ErrorDictEncoder('UBID')

        dict_pipe = DictPipe(decoder_in, encoder_out, encoder_err)

        io_in = io.StringIO('WKT\r\nPOINT (0 0)\r\n')
        io_out = io.StringIO('')
        io_err = io.StringIO('')

        dict_pipe.run(io_in, io_out, io_err, args_in=[], kwargs_in={}, args_out=[], kwargs_out={})

        self.assertEqual('WKT\r\nPOINT (0 0)\r\n', io_in.getvalue())
        self.assertEqual('WKT,UBID\r\nPOINT (0 0),6FG22222+22-0-0-0-0\r\n', io_out.getvalue())
        self.assertEqual('', io_err.getvalue())

        io_in = io.StringIO('WKT\r\nx\r\n')
        io_out = io.StringIO('')
        io_err = io.StringIO('')

        dict_pipe.run(io_in, io_out, io_err, args_in=[], kwargs_in={}, args_out=[], kwargs_out={})

        self.assertEqual('WKT\r\nx\r\n', io_in.getvalue())
        self.assertEqual('', io_out.getvalue())
        self.assertEqual('WKT,UBID_Error_Name,UBID_Error_Message\r\nx,WKTReadingError,Could not create geometry because of errors while reading input.\r\n', io_err.getvalue())

if __name__ == '__main__':
    unittest.main()
