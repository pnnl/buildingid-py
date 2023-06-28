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
import typing

import click
import click_log
import pandas
import pyqtree

from tqdm import tqdm
tqdm.pandas()

from .dict_decoders import LatLngDictDecoder, WKBDictDecoder, WKTDictDecoder
from .dict_encoders import BaseGeometryDictEncoder, ErrorDictEncoder
from .dict_pipe import DictPipe
from .exceptions import CustomException, FieldNotFoundError, FieldNotUniqueError
from .set_csv_field_size_limit import set_csv_field_size_limit

from ..code import Code, CodeArea, decode
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

@cli.command('crossref', short_help='cross-reference "UBID" fields in rows of two CSV files')
@click.argument('left', type=click.File('r'))
@click.argument('right', type=click.File('r'))
@click.argument('dst', type=click.File('w'))
@click.option('--fieldname-jaccard', type=click.STRING, default='IoU', show_default=True, help='the name of the Jaccard similarity coefficient (viz., "intersection over union" or "IoU") in the output file')
@click.option('--include-jaccard-field', is_flag=True, default=False, show_default=True, help='include the Jaccard similarity coefficient in the output file')
@click.option('--include-index-fields', is_flag=True, default=False, show_default=True, help='include the index field in the output file')
@click.option('--include-left-field', type=click.STRING, multiple=True, help='include the named field of the left input file in the output file')
@click.option('--include-right-field', type=click.STRING, multiple=True, help='include the named field of the right input file in the output file')
@click.option('--jaccard-min', type=click.FloatRange(min=0.0, max=1.0), default=0.0, show_default=True, help='the minimum value of the Jaccard similarity coefficient')
@click.option('--jaccard-max', type=click.FloatRange(min=0.0, max=1.0), default=1.0, show_default=True, help='the maximum value of the Jaccard similarity coefficient')
@click.option('--sort-by-jaccard', is_flag=True, default=False, show_default=True, help='sort the rows of the output file by the Jaccard similarity coefficient')
@click.option('--sort-order', type=click.Choice(['ASC', 'DESC'], case_sensitive=True), default='ASC', show_default=True, help='the sort order for the rows of the output file')
@click.option('--left-group-by-jaccard', is_flag=True, default=False, show_default=True, help='group the rows of the left input file by their UBID strings')
@click.option('--left-group-order', type=click.Choice(['ASC', 'DESC'], case_sensitive=True), default='ASC', show_default=True, help='the sort order for the groups of rows of the left input file')
@click.option('--right-group-by-jaccard', is_flag=True, default=False, show_default=True, help='group the rows of the right input file by their UBID string')
@click.option('--right-group-order', type=click.Choice(['ASC', 'DESC'], case_sensitive=True), default='ASC', show_default=True, help='the sort order for the groups of rows of the right input file')
@click.option('--left-fieldname-code', type=click.STRING, default='UBID', show_default=True, help='the name of the UBID field in the left input file')
@click.option('--left-fieldname-index', type=click.STRING, default='index', show_default=True, help='the name of the index field in the left input file')
@click.option('--left-fieldname-openlocationcode', type=click.STRING, default='__openlocationcode__', show_default=True, help='the name of the temporary field for decoded UBID strings in the left input file')
@click.option('--left-suffix', type=click.STRING, default='_x', show_default=True, help='the suffix for field names in the left input file')
@click.option('--left-reader-delimiter', type=click.STRING, default=',', show_default=True, help='the delimiter to use for the left input file')
@click.option('--left-reader-quotechar', type=click.STRING, default='"', show_default=True, help='the character used to denote the start and end of a quoted field in the left input file')
@click.option('--right-fieldname-code', type=click.STRING, default='UBID', show_default=True, help='the name of the UBID field in the right input file')
@click.option('--right-fieldname-index', type=click.STRING, default='index', show_default=True, help='the name of the index field in the right input file')
@click.option('--right-fieldname-openlocationcode', type=click.STRING, default='__openlocationcode__', show_default=True, help='the name of the temporary field for decoded UBID strings in the right input file')
@click.option('--right-suffix', type=click.STRING, default='_y', show_default=True, help='the suffix for field names in the right input file')
@click.option('--right-reader-delimiter', type=click.STRING, default=',', show_default=True, help='the delimiter to use for the right input file')
@click.option('--right-reader-quotechar', type=click.STRING, default='"', show_default=True, help='the character used to denote the start and end of a quoted field in the right input file')
@click.option('--writer-delimiter', type=click.STRING, default=',', show_default=True, help='the delimiter to use for the output file')
@click.option('--writer-quotechar', type=click.STRING, default='"', show_default=True, help='the character used to denote the start and end of a quoted field in the output file')
@click.pass_context
def run_crossref(ctx: None, left: typing.TextIO, right: typing.TextIO, dst: typing.TextIO, fieldname_jaccard: str, include_jaccard_field: bool, include_index_fields: bool, include_left_field: typing.List[str], include_right_field: typing.List[str], jaccard_min: float, jaccard_max: float, sort_by_jaccard: bool, sort_order: str, left_group_by_jaccard: bool, left_group_order: str, right_group_by_jaccard: bool, right_group_order: str, left_fieldname_code: str, left_fieldname_index: str, left_fieldname_openlocationcode: str, left_suffix: str, left_reader_delimiter: str, left_reader_quotechar: str, right_fieldname_code: str, right_fieldname_index: str, right_fieldname_openlocationcode: str, right_suffix: str, right_reader_delimiter: str, right_reader_quotechar: str, writer_delimiter: str, writer_quotechar: str) -> None:
    """The \033[1mcrossref\033[0m command cross-references the Unique Building Identifiers (UBIDs) in the rows of the left and right input files.

    The left input, right input and output files are represented in comma-separated values (CSV) format.  The left and right input files are read from either the standard input stream (using "-") or the specified path.  The output file is written to either the standard output stream (using "-") or the specified path.

    The larger of the two input files is used to construct a quadtree-based spatial index.  The smaller of the two input files is traversed, row at a time, to identify intersecting UBID bounding boxes.  For each intersection, the Jaccard similarity coefficient (viz., "intersection over union" or "IoU") is calculated, and the row is written to the output file.

    The \033[1mcrossref\033[0m command exits 0 on success, and >0 if an error occurs.
    """

    # Configuration for `pandas.read_csv` for left input file.
    kwargs_for_read_csv_left: typing.Dict[str, typing.Any] = {
        'dtype': {
            left_fieldname_code: str,
        },
        'quotechar': left_reader_quotechar,
        'sep': left_reader_delimiter,
        'usecols': [
            left_fieldname_code,
        ] + list(include_left_field),
    }

    # Configuration for `pandas.read_csv` for right input file.
    kwargs_for_read_csv_right: typing.Dict[str, typing.Any] = {
        'dtype': {
            right_fieldname_code: str,
        },
        'quotechar': right_reader_quotechar,
        'sep': right_reader_delimiter,
        'usecols': [
            right_fieldname_code,
        ] + list(include_right_field),
    }

    # Configuration for `pandas.to_csv` for output file.
    kwargs_for_to_csv_dst: typing.Dict[str, typing.Any] = {
        'quotechar': writer_quotechar,
        # 'quoting': csv.QUOTE_NONNUMERIC,
        'sep': writer_delimiter,
    }

    # Names for "index" fields for left and right input files.
    left_fieldname_index_with_suffix: str = '{0}{1}'.format(left_fieldname_index, left_suffix)
    right_fieldname_index_with_suffix: str = '{0}{1}'.format(right_fieldname_index, right_suffix)

    # Names for "__openlocationcode__" fields for left and right input files.
    left_fieldname_openlocationcode_with_suffix: str = '{0}{1}'.format(left_fieldname_openlocationcode, left_suffix)
    right_fieldname_openlocationcode_with_suffix: str = '{0}{1}'.format(right_fieldname_openlocationcode, right_suffix)

    def callback_decode_(code: Code) -> typing.Optional[CodeArea]:
        """Return the decoded 'CodeArea' for the given 'Code', or 'None' if an error occurs.
        """

        if code is None:
            return None

        try:
            codeArea = decode(code)
        except (AssertionError, ValueError, ):
            return None

        return codeArea

    def sort_order_to_ascending_(value: str) -> typing.Optional[bool]:
        """Return the "ascending" argument for the `pandas.DataFrame.sort_values` method.
        """

        if value == 'ASC':
            return True
        elif value == 'DESC':
            return False
        else:
            return None

    try:
        # Construct 'pandas.DataFrame' for left input file.
        #
        # Ensure that "UBID" field is present and that "index" and "__openlocationcode__" fields are not present.
        #
        # Finally, construct 'pandas.Series' for 'CodeArea' by decoding "UBID" field.
        logger.info('[crossref] Reading left input file: "{0}"'.format(str(left.name).replace('"', '\\"')))
        left_data_frame: pandas.DataFrame = pandas.read_csv(filepath_or_buffer=left, **kwargs_for_read_csv_left)
        if left_fieldname_code not in left_data_frame:
            raise FieldNotFoundError(left_fieldname_code)
        elif left_fieldname_index_with_suffix in left_data_frame:
            raise FieldNotUniqueError(left_fieldname_index_with_suffix)
        elif left_fieldname_openlocationcode_with_suffix in left_data_frame:
            raise FieldNotUniqueError(left_fieldname_openlocationcode_with_suffix)
        left_series_codeArea: pandas.Series = left_data_frame[left_fieldname_code].progress_apply(callback_decode_)
        logger.info('[crossref] Decoded \033[1m{0}/{1} ({2}%)\033[0m rows of left input file'.format(left_series_codeArea.count(), len(left_data_frame), round((left_series_codeArea.count() / len(left_data_frame)) * 100, 2)))

        # Construct 'pandas.DataFrame' for right input file.
        #
        # Ensure that "UBID" field is present and that "index" and "__openlocationcode__" fields are not present.
        #
        # Finally, construct 'pandas.Series' for 'CodeArea' by decoding "UBID" field.
        logger.info('[crossref] Reading right input file: "{0}"'.format(str(right.name).replace('"', '\\"')))
        right_data_frame: pandas.DataFrame = pandas.read_csv(filepath_or_buffer=right, **kwargs_for_read_csv_right)
        if right_fieldname_code not in right_data_frame:
            raise FieldNotFoundError(right_fieldname_code)
        elif right_fieldname_index_with_suffix in right_data_frame:
            raise FieldNotUniqueError(right_fieldname_index_with_suffix)
        elif right_fieldname_openlocationcode_with_suffix in right_data_frame:
            raise FieldNotUniqueError(right_fieldname_openlocationcode_with_suffix)
        right_series_codeArea: pandas.Series = right_data_frame[right_fieldname_code].progress_apply(callback_decode_)
        logger.info('[crossref] Decoded \033[1m{0}/{1} ({2}%)\033[0m rows of right input file'.format(right_series_codeArea.count(), len(right_data_frame), round((right_series_codeArea.count() / len(right_data_frame)) * 100, 2)))

        # Construct quadtree-based spatial index.
        if len(left_series_codeArea) >= len(right_series_codeArea):
            # If left input file has more rows than right input file, then construct
            # spatial index using left input file and cross-reference with rows of
            # right input file.

            logger.info('[crossref] Constructing quadtree for left input file')
            left_spindex: pyqtree.Index = pyqtree.Index(bbox=[
                left_series_codeArea.progress_apply(lambda codeArea: codeArea.longitudeLo).min(),
                left_series_codeArea.progress_apply(lambda codeArea: codeArea.latitudeLo).min(),
                left_series_codeArea.progress_apply(lambda codeArea: codeArea.longitudeHi).max(),
                left_series_codeArea.progress_apply(lambda codeArea: codeArea.latitudeHi).max(),
            ])
            for left_index, left_codeArea in tqdm(left_series_codeArea.items(), total=len(left_series_codeArea)):
                if left_codeArea is not None:
                    left_spindex.insert(item=(left_index, left_codeArea), bbox=[left_codeArea.longitudeLo, left_codeArea.latitudeLo, left_codeArea.longitudeHi, left_codeArea.latitudeHi])

            logger.info('[crossref] Cross-referencing rows of right input file against quadtree for left input file')
            dst_data: typing.List[typing.Tuple[int, int, CodeArea, CodeArea]] = [
                (left_index, right_index, left_codeArea, right_codeArea)
                for right_index, right_codeArea
                in tqdm(right_series_codeArea.items(), total=len(right_series_codeArea))
                if right_codeArea is not None
                for (left_index, left_codeArea)
                in left_spindex.intersect([right_codeArea.longitudeLo, right_codeArea.latitudeLo, right_codeArea.longitudeHi, right_codeArea.latitudeHi])
                if left_codeArea is not None
            ]
        else:
            # If right input file has more rows than left input file, then construct
            # spatial index using right input file and cross-reference with rows of
            # left input file.

            logger.info('[crossref] Constructing quadtree for right input file')
            right_spindex: pyqtree.Index = pyqtree.Index(bbox=[
                right_series_codeArea.progress_apply(lambda codeArea: codeArea.longitudeLo).min(),
                right_series_codeArea.progress_apply(lambda codeArea: codeArea.latitudeLo).min(),
                right_series_codeArea.progress_apply(lambda codeArea: codeArea.longitudeHi).max(),
                right_series_codeArea.progress_apply(lambda codeArea: codeArea.latitudeHi).max(),
            ])
            for right_index, right_codeArea in tqdm(right_series_codeArea.items(), total=len(right_series_codeArea)):
                if right_codeArea is not None:
                    right_spindex.insert(item=(right_index, right_codeArea), bbox=[right_codeArea.longitudeLo, right_codeArea.latitudeLo, right_codeArea.longitudeHi, right_codeArea.latitudeHi])

            logger.info('[crossref] Cross-referencing rows of left input file against quadtree for right input file')
            dst_data: typing.List[typing.Tuple[int, int, CodeArea, CodeArea]] = [
                (left_index, right_index, left_codeArea, right_codeArea)
                for left_index, left_codeArea
                in tqdm(left_series_codeArea.items(), total=len(left_series_codeArea))
                if left_codeArea is not None
                for (right_index, right_codeArea)
                in right_spindex.intersect([left_codeArea.longitudeLo, left_codeArea.latitudeLo, left_codeArea.longitudeHi, left_codeArea.latitudeHi])
                if right_codeArea is not None
            ]

        # Construct 'pandas.DataFrame' for cross-reference results (viz., "intersections").
        dst_data_frame: pandas.DataFrame = pandas.DataFrame(data=dst_data, columns=[
            left_fieldname_index_with_suffix,
            right_fieldname_index_with_suffix,
            left_fieldname_openlocationcode_with_suffix,
            right_fieldname_openlocationcode_with_suffix,
        ])

        # If there are no cross-reference results, then exit.
        len_dst_data_frame0: int = len(dst_data_frame)
        logger.info('[crossref] Found \033[1m{0}\033[0m intersection{1}'.format(len_dst_data_frame0, '' if len_dst_data_frame0 == 1 else 's'))
        if len_dst_data_frame0 == 0:
            return

        # Calculate Jaccard similarity coefficient (viz., "intersection over union", "IoU", etc.) for each cross-reference result.
        logger.info('[crossref] Calculating field: "{0}"'.format(fieldname_jaccard.replace('"', '\\"')))
        if fieldname_jaccard in dst_data_frame:
            raise FieldNotUniqueError(fieldname_jaccard)
        dst_data_frame[fieldname_jaccard] = dst_data_frame.progress_apply(lambda row: row[left_fieldname_openlocationcode_with_suffix].jaccard(row[right_fieldname_openlocationcode_with_suffix]), axis=1)

        # Select cross-reference results within the specified open interval.
        logger.info('[crossref] Filtering intersections: {1} <= "{0}" <= {2}'.format(fieldname_jaccard.replace('"', '\\"'), jaccard_min, jaccard_max))
        dst_data_frame: pandas.DataFrame = dst_data_frame[dst_data_frame[fieldname_jaccard].notnull() & (jaccard_min <= dst_data_frame[fieldname_jaccard]) & (dst_data_frame[fieldname_jaccard] <= jaccard_max)]

        # If there are no cross-reference results, then exit.
        len_dst_data_frame1: int = len(dst_data_frame)
        logger.info('[crossref] Found \033[1m{0}/{1} ({2}%)\033[0m intersection{3}: "{4}"'.format(len_dst_data_frame1, len_dst_data_frame0, round((len_dst_data_frame1 / len_dst_data_frame0) * 100, 2), '' if len_dst_data_frame0 == 1 else 's', fieldname_jaccard.replace('"', '\\"')))
        if len_dst_data_frame1 == 0:
            return

        # Merge left and right input files with cross-reference results using an inner join.
        logger.info('[crossref] Merging intersections with left input file')
        dst_data_frame: pandas.DataFrame = dst_data_frame.merge(left_data_frame.reset_index().rename(index=str, columns={
            'index': left_fieldname_index_with_suffix,
        }), how='inner', left_on=left_fieldname_index_with_suffix, right_on=left_fieldname_index_with_suffix, suffixes=(False, False))
        logger.info('[crossref] Merging intersections with right input file')
        dst_data_frame: pandas.DataFrame = dst_data_frame.merge(right_data_frame.reset_index().rename(index=str, columns={
            'index': right_fieldname_index_with_suffix,
        }), how='inner', left_on=right_fieldname_index_with_suffix, right_on=right_fieldname_index_with_suffix, suffixes=(left_suffix, right_suffix))

        # Sort cross-reference results by Jaccard similarity coefficient.
        if sort_by_jaccard:
            logger.info('[crossref] Sorting: "{0}" {1}'.format(fieldname_jaccard.replace('"', '\\"'), sort_order))
            dst_data_frame.sort_values(fieldname_jaccard, axis=0, ascending=sort_order_to_ascending_(sort_order), inplace=True)

        # Group cross-reference results by left "index" and then, for each group,
        # select cross-reference result with least ("ASC") or greatest ("DESC") value.
        if left_group_by_jaccard:
            logger.info('[crossref] Grouping on left: "{0}" {1}'.format(fieldname_jaccard.replace('"', '\\"'), left_group_order))
            left_group_by_series: pandas.Series = dst_data_frame.groupby([left_fieldname_index_with_suffix])[fieldname_jaccard]
            if left_group_order == 'ASC':
                dst_data_frame: pandas.DataFrame = dst_data_frame.loc[left_group_by_series.idxmin()]
            elif left_group_order == 'DESC':
                dst_data_frame: pandas.DataFrame = dst_data_frame.loc[left_group_by_series.idxmax()]
            else:
                pass

        # Group cross-reference results by right "index" and then, for each group,
        # select cross-reference result with least ("ASC") or greatest ("DESC") value.
        if right_group_by_jaccard:
            logger.info('[crossref] Grouping on right: "{0}" {1}'.format(fieldname_jaccard.replace('"', '\\"'), right_group_order))
            right_group_by_series: pandas.Series = dst_data_frame.groupby([right_fieldname_index_with_suffix])[fieldname_jaccard]
            if right_group_order == 'ASC':
                dst_data_frame: pandas.DataFrame = dst_data_frame.loc[right_group_by_series.idxmin()]
            elif right_group_order == 'DESC':
                dst_data_frame: pandas.DataFrame = dst_data_frame.loc[right_group_by_series.idxmax()]
            else:
                pass

        # Delete left and right "__openlocationcode__" fields.
        del dst_data_frame[left_fieldname_openlocationcode_with_suffix]
        del dst_data_frame[right_fieldname_openlocationcode_with_suffix]

        # Delete "IoU" field.
        if not include_jaccard_field:
            del dst_data_frame[fieldname_jaccard]

        # Delete left and right "index" fields.
        if not include_index_fields:
            del dst_data_frame[left_fieldname_index_with_suffix]
            del dst_data_frame[right_fieldname_index_with_suffix]

        # Write output file.
        logger.info('[crossref] Writing output file: "{0}"'.format(str(dst.name).replace('"', '\\"')))
        dst_data_frame.to_csv(path_or_buf=dst, header=True, index=False, **kwargs_for_to_csv_dst)
    except BaseException as exception:
        raise click.ClickException(exception)

    # Done!
    return
