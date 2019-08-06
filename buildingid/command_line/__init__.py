# -*- coding: utf-8 -*-
#
# pnnl-buildingid: buildingid/command_line/__init__.py
#
# Copyright (c) 2019, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE.txt and WARRANTY.txt for details.

# import csv
import logging

import click
import click_log

from .dict_decoders import LatLngDictDecoder, WKBDictDecoder, WKTDictDecoder
from .dict_encoders import BaseGeometryDictEncoder, ErrorDictEncoder
from .dict_pipe import DictPipe
from .exceptions import CustomException
from .set_csv_field_size_limit import set_csv_field_size_limit

from ..validators import isValidCodeLength
from ..version import __version__

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

click_log.basic_config(logger)

set_csv_field_size_limit()

def click_callback_code_length_(ctx: None, opt: click.core.Option, codeLength: int) -> int:
    """Callback for "--code-length" option (the number of digits in the OLC segment of the UBID string).

    See `buildingid.validators.isValidCodeLength` for details.
    """

    if isValidCodeLength(codeLength):
        return codeLength
    else:
        raise click.BadParameter('Invalid Open Location Code length: {0}'.format(str(codeLength)))

@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.pass_context
@click.version_option(__version__)
def cli(ctx: None) -> None:
    """Unique Building Identifier (UBID) Software – Beta Source Code (Battelle IPID 31307-E)

    This Beta version of the Software is provided to you for evaluation and
    suggested improvements.  Battelle plans to release the Software to the
    public as open source software under an Open Source Initiative-approved open
    source license.  The public version will be available on the PNNL GitHub
    page https://github.com/pnnl and through the US DOE Office of Scientific and
    Technical Information DOE Code site at https://www.osti.gov/doecode/.
    """

@cli.command('append2csv', short_help='append "UBID" field to rows of CSV file')
@click.argument('dict-decoder-id', nargs=1, type=click.Choice(['latlng', 'wkb', 'wkt'], case_sensitive=True))
@click.option('--code-length', type=click.IntRange(0, None), default=11, show_default=True, callback=click_callback_code_length_, help='the number of digits in the OLC segment of the UBID string')
@click.option('--fieldname-south-latitude', type=click.STRING, default=None, show_default=True, help='the name of the south latitude field in the input file')
@click.option('--fieldname-west-longitude', type=click.STRING, default=None, show_default=True, help='the name of the west longitude field in the input file')
@click.option('--fieldname-north-latitude', type=click.STRING, default=None, show_default=True, help='the name of the north latitude field in the input file')
@click.option('--fieldname-east-longitude', type=click.STRING, default=None, show_default=True, help='the name of the east longitude field in the input file')
@click.option('--fieldname-center-latitude', type=click.STRING, default='Latitude', show_default=True, help='the name of the center latitude field in the input file')
@click.option('--fieldname-center-longitude', type=click.STRING, default='Longitude', show_default=True, help='the name of the center longitude field in the input file')
@click.option('--fieldname-wkbstr', type=click.STRING, default='WKB', show_default=True, help='the name of the hex-encoded well-known binary (WKB) string field in the input file')
@click.option('--fieldname-wktstr', type=click.STRING, default='WKT', show_default=True, help='the name of the well-known text (WKT) string field in the input file')
@click.option('--fieldname-code', type=click.STRING, default='UBID', show_default=True, help='the name of the UBID field in the output file')
@click.option('--reader-delimiter', type=click.STRING, default=',', show_default=True, help='the delimiter to use for the input file')
@click.option('--reader-quotechar', type=click.STRING, default='"', show_default=True, help='the character used to denote the start and end of a quoted field in the input file')
@click.option('--writer-delimiter', type=click.STRING, default=',', show_default=True, help='the delimiter to use for the output file')
@click.option('--writer-quotechar', type=click.STRING, default='"', show_default=True, help='the character used to denote the start and end of a quoted field in the output file')
@click.pass_context
def run_append_to_csv(ctx: None, dict_decoder_id: str, code_length: int, fieldname_south_latitude: str, fieldname_west_longitude: str, fieldname_north_latitude: str, fieldname_east_longitude: str, fieldname_center_latitude: str, fieldname_center_longitude: str, fieldname_wkbstr: str, fieldname_wktstr: str, fieldname_code: str, reader_delimiter: str, reader_quotechar: str, writer_delimiter: str, writer_quotechar: str) -> None:
    """The \033[1mappend2csv\033[0m command assigns a Unique Building Identifier (UBID) to each row in the input file.

    The input, output and error files are represented in comma-separated values (CSV) format.  The input file is read from the standard input stream.  The output file is written to the standard output stream.  The error file is written to the standard error stream.

    For each row in the input file, the geometry for the row is assigned a UBID.  If a UBID is successfully assigned, then the row is written to the output file with an added "UBID" field (the \033[1m--fieldname-code\033[0m option).  If a UBID is not assigned, for example, if an exception is raised, then the row is written to the error file.

    The following modes are available, where each mode corresponds to a geometry type:

    \033[1mlatlng\033[0m\tPoints; represented as latitude and longitude coordinates, read from the "Latitude" and "Longitude" fields (the \033[1m--fieldname-center-latitude\033[0m and \033[1m--fieldname-center-longitude\033[0m options).

    \033[1mwkb\033[0m\t\tShapes; represented as strings in hex-encoded well-known binary (WKB) format read from the "WKB" field (the \033[1m--fieldname-wkbstr\033[0m option).

    \033[1mwkt\033[0m\t\tShapes; represented as strings in well-known text (WKT) format, read from the "WKT" field (the \033[1m--fieldname-wktstr\033[0m option).

    The number of digits in the Open Location Code (OLC) segment of the UBID string is specified by the \033[1m--code-length\033[0m option.

    The \033[1mappend2csv\033[0m command exits 0 on success, and >0 if an error occurs.
    """

    # Construct `DictDecoder[DictDatum]` for standard input stream.
    if 'latlng' == dict_decoder_id:
        decoder_in = LatLngDictDecoder(fieldname_center_latitude, fieldname_center_longitude, fieldname_north_latitude=fieldname_north_latitude, fieldname_south_latitude=fieldname_south_latitude, fieldname_east_longitude=fieldname_east_longitude, fieldname_west_longitude=fieldname_west_longitude)
    elif 'wkb' == dict_decoder_id:
        decoder_in = WKBDictDecoder(fieldname_wkbstr)
    elif 'wkt' == dict_decoder_id:
        decoder_in = WKTDictDecoder(fieldname_wktstr)
    else:
        pass

    # Construct `DictEncoder[DictDatum]` for standard output stream.
    encoder_out = BaseGeometryDictEncoder(fieldname_code, code_length)

    # Construct `DictEncoder[BaseException]` for standard error stream.
    encoder_err = ErrorDictEncoder(fieldname_code)

    # Construct `DictPipe` for standard input, output and error streams.
    dict_pipe = DictPipe(decoder_in, encoder_out, encoder_err)

    # Standard input, output and error streams.
    io_in = click.get_text_stream('stdin')
    io_out = click.get_text_stream('stdout')
    io_err = click.get_text_stream('stderr')

    # Configuration for `csv.DictReader`.
    args_in = []
    kwargs_in = {
        'delimiter': reader_delimiter,
        'quotechar': reader_quotechar,
    }

    # Configuration for `csv.DictWriter`.
    args_out = []
    kwargs_out = {
        'delimiter': writer_delimiter,
        'quotechar': writer_quotechar,
        # 'quoting': csv.QUOTE_NONNUMERIC,
    }

    try:
        dict_pipe.run(io_in, io_out, io_err, args_in=args_in, kwargs_in=kwargs_in, args_out=args_out, kwargs_out=kwargs_out)
    except CustomException as exception:
        raise click.ClickException(exception)

    # Done!
    return
