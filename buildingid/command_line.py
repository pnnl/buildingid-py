#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pnnl-buildingid: buildingid/command_line.py
#
# Copyright (c) 2018, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE.txt and WARRANTY.txt for details.

import csv
import functools
import sys

import click
import pyproj
import shapefile
import shapely.geometry

from buildingid.context import openlocationcode
from buildingid.version import __version__

import buildingid.v1
import buildingid.v2
import buildingid.v3
import buildingid.wkt

@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.version_option(__version__)
@click.pass_context
def cli(obj):
    """Unique Building Identifier (UBID) Software – Beta Source Code (Battelle IPID 31307-E)

    This Beta version of the Software is provided to you for evaluation and
    suggested improvements.  Battelle plans to release the Software to the
    public as open source software under an Open Source Initiative-approved open
    source license.  The public version will be available on the PNNL GitHub
    page https://github.com/pnnl and through the US DOE Office of Scientific and
    Technical Information DOE Code site at https://www.osti.gov/doecode/.
    """

# Map from command-line option value to UBID codec (i.e., version).
CODEC_MODULES_BY_INDEX_ = {
    '1': buildingid.v1,
    '2': buildingid.v2,
    '3': buildingid.v3,
}

# List of command-line option values for UBID codecs (i.e., versions).
CODEC_MODULE_INDICES_ = click.Choice(CODEC_MODULES_BY_INDEX_.keys())

# The default length for Open Location Codes.
DEFAULT_CODE_LENGTH_ = 11

# The default UBID codec (i.e., version).
DEFAULT_CODEC_ = '3'

# The default one-character string used to separate input fields.
DEFAULT_DELIMITER_READER_ = ','

# The default one-character string used to separate output fields.
DEFAULT_DELIMITER_WRITER_ = ','

# The default field used as input.
DEFAULT_FIELDNAME_READER_ = 'the_geom'

# The default field used as output.
DEFAULT_FIELDNAME_WRITER_ = 'UBID'

# The default projection used as input.
DEFAULT_PROJECTION_READER_ = 'epsg:4326'

# The default one-character string used to quote input fields that contain special characters.
DEFAULT_QUOTECHAR_READER_ = '"'

# The default one-character string used to quote input fields that contain special characters.
DEFAULT_QUOTECHAR_WRITER_ = '"'

from openlocationcode import PAIR_CODE_LENGTH_

def validate_codeLength(ctx, param, value):
    if (value >= 2) and ((value >= PAIR_CODE_LENGTH_) or ((value % 2) == 0)):
        return value
    else:
        raise click.BadParameter('Invalid value for "{0}": Invalid Open Location Code length - {1}'.format(param, str(value)))

@cli.command('append2csv', short_help='Read CSV file from stdin, append UBID field, and write CSV file to stdout.')
@click.option('--code-length', type=click.IntRange(0, None), callback=validate_codeLength, default=DEFAULT_CODE_LENGTH_, show_default=True, help='the Open Location Code length')
@click.option('--codec', type=CODEC_MODULE_INDICES_, default=DEFAULT_CODEC_, show_default=True, help='the UBID codec')
@click.option('--reader-delimiter', type=click.STRING, default=DEFAULT_DELIMITER_READER_, show_default=True, help='the one-character string used to separate input fields')
@click.option('--reader-fieldname', type=click.STRING, default=DEFAULT_FIELDNAME_READER_, show_default=True, help='the field used as input')
@click.option('--reader-quotechar', type=click.STRING, default=DEFAULT_QUOTECHAR_READER_, show_default=True, help='the one-character string used to quote input fields that contain special characters')
@click.option('--writer-delimiter', type=click.STRING, default=DEFAULT_DELIMITER_WRITER_, show_default=True, help='the one-character string used to separate output fields')
@click.option('--writer-fieldname', type=click.STRING, default=DEFAULT_FIELDNAME_WRITER_, show_default=True, help='the field used as output')
@click.option('--writer-quotechar', type=click.STRING, default=DEFAULT_QUOTECHAR_WRITER_, show_default=True, help='the one-character string used to quote output fields that contain special characters')
@click.option('--wkt/--no-wkt', default=True, show_default=True, help='include Well-known Text (WKT) in the output')
@click.option('--wkt-fieldname-bbox', type=click.STRING, default='{0}_bbox'.format(DEFAULT_FIELDNAME_WRITER_), show_default=True, help='the field used as output for the WKT representation of the bounding box of the geometry of the UBID')
@click.option('--wkt-fieldname-centroid', type=click.STRING, default='{0}_centroid'.format(DEFAULT_FIELDNAME_WRITER_), show_default=True, help='the field used as output for the WKT representation of the centroid of the geometry of the UBID')
def run_append_to_csv(code_length, codec, reader_delimiter, reader_fieldname, reader_quotechar, writer_delimiter, writer_fieldname, writer_quotechar, wkt, wkt_fieldname_bbox, wkt_fieldname_centroid):
    # Look-up the codec module.
    codec_module = CODEC_MODULES_BY_INDEX_[codec]

    # Initialize the CSV reader for the standard-input stream.
    reader_kwargs = {
        'delimiter': reader_delimiter,
        'quotechar': reader_quotechar,
    }
    # NOTE Use of 'csv.DictReader' assumes presence of CSV header row.
    reader = csv.DictReader(click.get_text_stream('stdin'), **reader_kwargs)

    # Initialize the list of fields for the CSV writer.
    #
    # NOTE Use 'list' function to clone list of fields (e.g., so that changes do
    # not affect the behavior of the CSV reader).
    writer_fieldnames = list(reader.fieldnames)

    # Validate the fields for the CSV reader and writer.
    if not reader_fieldname in writer_fieldnames:
        raise click.ClickException('Invalid value for "reader-fieldname": Field not found: {0}'.format(reader_fieldname))
    elif writer_fieldname in writer_fieldnames:
        raise click.ClickException('Invalid value for "writer-fieldname": Duplicate field: {0}'.format(writer_fieldname))

    # Validation successful. Add the field for the CSV writer to the list
    # (safely).
    writer_fieldnames.append(writer_fieldname)

    if wkt:
        # Validate WKT fields.
        if wkt_fieldname_bbox in writer_fieldnames:
            raise click.ClickException('Invalid value for "wkt-fieldname-bbox": Duplicate field: {0}'.format(wkt_fieldname_bbox))
        if wkt_fieldname_centroid in writer_fieldnames:
            raise click.ClickException('Invalid value for "wkt-fieldname-centroid": Duplicate field: {0}'.format(wkt_fieldname_centroid))

        # Validation successful. Add the WKT fields for the CSV writer to the
        # list (safely).
        writer_fieldnames.append(wkt_fieldname_bbox)
        writer_fieldnames.append(wkt_fieldname_centroid)

    # Initialize the CSV writer for the standard-output stream.
    writer_kwargs = {
        'delimiter': writer_delimiter,
        'quotechar': writer_quotechar,
        # NOTE Use of 'csv.QUOTE_NONNUMERIC' ensures that UBID is quoted.
        'quoting': csv.QUOTE_NONNUMERIC,
    }
    writer = csv.DictWriter(click.get_text_stream('stdout'), writer_fieldnames, **writer_kwargs)

    # NOTE If at least one row is written, then write the header row. Otherwise,
    # do not write the header row (to the standard-output stream).
    writer_writerheader_called = False

    # Initialize the CSV writer for the standard-error stream.
    err_writer = csv.DictWriter(click.get_text_stream('stderr'), reader.fieldnames, **writer_kwargs)

    # NOTE If at least one row is written, then write the header row. Otherwise,
    # do not write the header row (to the standard-error stream).
    err_writer_writeheader_called = False

    for row in reader:
        # Look-up the value of the field.
        reader_fieldname_value = row[reader_fieldname]

        try:
            # Parse the value of the field, assuming Well-known Text (WKT)
            # format, and then encode the result as a UBID.
            writer_fieldname_value = codec_module.encode(*buildingid.wkt.parse(reader_fieldname_value), codeLength=code_length)

            if wkt:
                # Decode the UBID.
                writer_fieldname_value_CodeArea = codec_module.decode(writer_fieldname_value)

                # Encode the UBID bounding box and centroid as WKT.
                row[wkt_fieldname_bbox] = str(shapely.geometry.box(writer_fieldname_value_CodeArea.longitudeLo, writer_fieldname_value_CodeArea.latitudeLo, writer_fieldname_value_CodeArea.longitudeHi, writer_fieldname_value_CodeArea.latitudeHi))
                row[wkt_fieldname_centroid] = str(shapely.geometry.box(writer_fieldname_value_CodeArea.child.longitudeLo, writer_fieldname_value_CodeArea.child.latitudeLo, writer_fieldname_value_CodeArea.child.longitudeHi, writer_fieldname_value_CodeArea.child.latitudeHi))
        except:
            # If an exception is raised (and caught), then write the CSV header
            # row (to the standard-error stream).
            if not err_writer_writeheader_called:
                # Set the flag.
                err_writer_writeheader_called = True

                err_writer.writeheader()

            # Write the row (to the standard-error stream).
            err_writer.writerow(row)
        else:
            # Set the value of the field.
            row[writer_fieldname] = writer_fieldname_value

            # Write the CSV header row (to the standard-output stream.)
            if not writer_writerheader_called:
                # Set the flag.
                writer_writerheader_called = True

                writer.writeheader()

            # Write the row (to the standard output stream).
            writer.writerow(row)

    # Done!
    return

@cli.command('append2shp', short_help='Read ESRI Shapefile from "SRC", append UBID field, and write ESRI Shapefile to "DST".')
@click.argument('src', type=click.Path())
@click.argument('dst', type=click.Path())
@click.option('--code-length', type=click.IntRange(0, None), callback=validate_codeLength, default=DEFAULT_CODE_LENGTH_, show_default=True, help='the Open Location Code length')
@click.option('--codec', type=CODEC_MODULE_INDICES_, default=DEFAULT_CODEC_, show_default=True, help='the UBID codec')
@click.option('--reader-projection', type=click.STRING, default=DEFAULT_PROJECTION_READER_, show_default=True, help='the projection for the points in shapes in the input ESRI Shapefile, e.g., WGS-84')
@click.option('--reader-projection-preserve-units/--no-reader-projection-preserve-units', default=True, show_default=True, help='if set, then the units of the projection are not forced to be meters')
@click.option('--writer-fieldname', type=click.STRING, default=DEFAULT_FIELDNAME_WRITER_, show_default=True, help='the field used as output')
def run_append_to_shp(src, dst, code_length, codec, reader_projection, reader_projection_preserve_units, writer_fieldname):
    # Look-up the codec module.
    codec_module = CODEC_MODULES_BY_INDEX_[codec]

    # Configure the projection from the source to WGS-84.
    p1 = pyproj.Proj(init=reader_projection, preserve_units=reader_projection_preserve_units)
    p2 = pyproj.Proj(init=DEFAULT_PROJECTION_READER_) # WGS-84
    transform = functools.partial(pyproj.transform, p1, p2)

    # Initialize the ESRI Shapefile reader.
    shapereader = shapefile.Reader(src)

    if shapereader.shapeType == shapefile.POLYGON:
        # Initialize the ESRI Shapefile writer.
        shapewriter = shapefile.Writer()
        shapewriter.fields = shapereader.fields[1:] # skip first deletion field
        shapewriter.field(writer_fieldname, 'C')
        shapewriter.shapeType = shapereader.shapeType

        for shapeRecord in shapereader.shapeRecords():
            assert shapeRecord.shape.shapeType == shapefile.POLYGON

            # Look-up the value of the field.
            reader_fieldname_value = str(shapely.geometry.Polygon(map(lambda coords: transform(*coords), list(shapeRecord.shape.points))))

            try:
                # Parse the value of the field, assuming Well-known Text (WKT)
                # format, and then encode the result as a UBID.
                writer_fieldname_value = codec_module.encode(*buildingid.wkt.parse(reader_fieldname_value), codeLength=code_length)
            except:
                # If an exception is raised (and caught), then write the record
                # without the UBID.
                shapewriter.record(*(shapeRecord.record + [None]))
            else:
                # Otherwise, write the record with the UBID.
                shapewriter.record(*(shapeRecord.record + [writer_fieldname_value]))

            # BUG https://github.com/GeospatialPython/pyshp/issues/100
            shapewriter._shapes.append(shapeRecord.shape)

        # Close the ESRI Shapefile writer.
        shapewriter.save(dst)
    else:
        # TODO Warning: Invalid ESRI Shapefile (not POLYGON).
        pass

    # Done!
    return

@cli.command('shp2csv', short_help='Read ESRI Shapefile from "SRC" and write CSV file with Well-known Text (WKT) field to stdout.')
@click.argument('src', type=click.Path())
@click.option('--reader-projection', type=click.STRING, default=DEFAULT_PROJECTION_READER_, show_default=True, help='the projection for the points in shapes in the input ESRI Shapefile, e.g., WGS-84')
@click.option('--reader-projection-preserve-units/--no-reader-projection-preserve-units', default=True, show_default=True, help='if set, then the units of the projection are not forced to be meters')
@click.option('--writer-delimiter', type=click.STRING, default=DEFAULT_DELIMITER_WRITER_, show_default=True, help='the one-character string used to separate output fields')
@click.option('--writer-fieldname', type=click.STRING, default=DEFAULT_FIELDNAME_READER_, show_default=True, help='the field used as output')
@click.option('--writer-quotechar', type=click.STRING, default=DEFAULT_QUOTECHAR_WRITER_, show_default=True, help='the one-character string used to quote output fields that contain special characters')
def run_shp_to_csv(src, reader_projection, reader_projection_preserve_units, writer_delimiter, writer_fieldname, writer_quotechar):
    # Configure the projection from the source to WGS-84.
    p1 = pyproj.Proj(init=reader_projection, preserve_units=reader_projection_preserve_units)
    p2 = pyproj.Proj(init=DEFAULT_PROJECTION_READER_) # WGS-84
    transform = functools.partial(pyproj.transform, p1, p2)

    # Initialize the ESRI Shapefile reader.
    shapereader = shapefile.Reader(src)

    # Initialize the list of fields in the ESRI Shapefile.
    shapereader_fieldnames = list(map(lambda field: field[0], list(shapereader.fields)))

    # Remove the first element of the list.
    del shapereader_fieldnames[0] # DeletionFlag

    # Initialize the list of fields for the CSV writer.
    csvwriter_fieldnames = shapereader_fieldnames + [writer_fieldname]

    # Initialize the CSV writer for the standard-output stream.
    csvwriter = csv.DictWriter(click.get_text_stream('stdout'), delimiter=writer_delimiter, fieldnames=csvwriter_fieldnames, quotechar=writer_quotechar)

    csvwriter.writeheader()

    if shapereader.shapeType == shapefile.POLYGON:
        for shapeRecord in shapereader.shapeRecords():
            assert shapeRecord.shape.shapeType == shapefile.POLYGON

            # Initialize new CSV row.
            csvrow = dict(zip(shapereader_fieldnames, list(shapeRecord.record)))

            # Look-up the value of the field.
            #
            # NOTE The length of the string may exceed the CSV field size limit.
            csvrow[writer_fieldname] = str(shapely.geometry.Polygon(map(lambda coords: transform(*coords), list(shapeRecord.shape.points))))

            # Write the row (to the standard output stream).
            csvwriter.writerow(csvrow)
    else:
        # TODO Warning: Invalid ESRI Shapefile (not POLYGON).
        pass

    # Done!
    return

@cli.command('convert', short_help='Read UBID (one per line) from stdin, convert UBID, and write UBID (one per line) to stdout. Write invalid UBID (one per line) to stderr.')
@click.option('--source', type=CODEC_MODULE_INDICES_, help='the input UBID codec')
@click.option('--target', type=CODEC_MODULE_INDICES_, help='the output UBID codec')
def run_convert(source, target):
    # Look-up the input and output codec modules.
    source_codec_module = CODEC_MODULES_BY_INDEX_[source]
    target_codec_module = CODEC_MODULES_BY_INDEX_[target]

    # Pointers to stream handles.
    stdin = click.get_text_stream('stdin')
    stdout = click.get_text_stream('stdout')
    stderr = click.get_text_stream('stderr')

    # Iterate over each line.
    for count, source_code in enumerate(stdin):
        # Strip leading and trailing white-space.
        #
        # NOTE When used in conjunction with the `echo` command, this is needed
        # in order to remove the trailing end-of-line character(s).
        source_code = source_code.strip()

        try:
            # Decode the input UBID code and then resize the resulting UBID code
            # area.
            code_area = source_codec_module.decode(source_code)
            code_area = code_area.resize()

            # Encode the output UBID code.
            target_code = target_codec_module.encodeCodeArea(code_area)
        except:
            # If an error is raised, write the input UBID code to the standard
            # error stream.
            print(source_code, file=stderr)
        else:
            # Otherwise, write the output UBID code to the standard output
            # stream.
            print(target_code, file=stdout)

    # Done!
    return

# c.f., https://stackoverflow.com/questions/15063936/csv-error-field-larger-than-field-limit-131072
def set_csv_field_size_limit(maxsize = sys.maxsize):
    decrement = True

    while decrement:
        try:
            csv.field_size_limit(maxsize)
        except OverflowError:
            maxsize = int(maxsize / 10)

            decrement = True
        else:
            decrement = False

    return

if __name__ == '__main__':
    set_csv_field_size_limit()

    cli()
