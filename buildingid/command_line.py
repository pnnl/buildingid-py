#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pnnl-buildingid: buildingid/command_line.py
#
# Copyright (c) 2018, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE.txt and WARRANTY.txt for details.

import click
import csv

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
DEFAULT_CODEC_ = '2'

# The default one-character string used to separate input fields.
DEFAULT_DELIMITER_READER_ = ','

# The default one-character string used to separate output fields.
DEFAULT_DELIMITER_WRITER_ = ','

# The default field used as input.
DEFAULT_FIELDNAME_READER_ = 'the_geom'

# The default field used as output.
DEFAULT_FIELDNAME_WRITER_ = 'UBID'

# The default one-character string used to quote input fields that contain special characters.
DEFAULT_QUOTECHAR_READER_ = '"'

# The default one-character string used to quote input fields that contain special characters.
DEFAULT_QUOTECHAR_WRITER_ = '"'

@cli.command('append2csv', short_help='Read CSV file from stdin, append UBID field, and write CSV file to stdout.')
@click.option('--code-length', type=click.INT, default=DEFAULT_CODE_LENGTH_, show_default=True, help='the Open Location Code length')
@click.option('--codec', type=CODEC_MODULE_INDICES_, default=DEFAULT_CODEC_, show_default=True, help='the UBID codec')
@click.option('--reader-delimiter', type=click.STRING, default=DEFAULT_DELIMITER_READER_, show_default=True, help='the one-character string used to separate input fields')
@click.option('--reader-fieldname', type=click.STRING, default=DEFAULT_FIELDNAME_READER_, show_default=True, help='the field used as input')
@click.option('--reader-quotechar', type=click.STRING, default=DEFAULT_QUOTECHAR_READER_, show_default=True, help='the one-character string used to quote input fields that contain special characters')
@click.option('--writer-delimiter', type=click.STRING, default=DEFAULT_DELIMITER_WRITER_, show_default=True, help='the one-character string used to separate output fields')
@click.option('--writer-fieldname', type=click.STRING, default=DEFAULT_FIELDNAME_WRITER_, show_default=True, help='the field used as output')
@click.option('--writer-quotechar', type=click.STRING, default=DEFAULT_QUOTECHAR_WRITER_, show_default=True, help='the one-character string used to quote output fields that contain special characters')
def run_append_to_csv(code_length, codec, reader_delimiter, reader_fieldname, reader_quotechar, writer_delimiter, writer_fieldname, writer_quotechar):
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
        raise ValueError('Field not found: {0}'.format(reader_fieldname))
    elif writer_fieldname in writer_fieldnames:
        raise ValueError('Duplicate field: {0}'.format(writer_fieldname))

    # Validation successful. Add the field for the CSV writer to the list
    # (safely).
    writer_fieldnames.append(writer_fieldname)

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

if __name__ == '__main__':
    cli()
