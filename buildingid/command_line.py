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
import pandas

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

@cli.command('csvmatch-exact', short_help='Merge the records in two CSV files by exactly matching the UBIDs.')
@click.option('--how', type=click.Choice(['left', 'right', 'outer', 'inner']), default='inner', show_default=True, help='the database-style join operation')
@click.option('--left-on', type=click.STRING, default=DEFAULT_FIELDNAME_WRITER_, show_default=True, help='the field name for the column to join on for the "LEFT" CSV file')
@click.option('--right-on', type=click.STRING, default=DEFAULT_FIELDNAME_WRITER_, show_default=True, help='the field name for the column to join on for the "RIGHT" CSV file')
@click.argument('left', type=click.File('r'))
@click.argument('right', type=click.File('r'))
def run_csv_match_exact(how, left_on, right_on, left, right):
    # Read the left and right CSV files.
    left_data_frame = pandas.read_csv(filepath_or_buffer=left)
    right_data_frame = pandas.read_csv(filepath_or_buffer=right)

    # Merge the left and right CSV files.
    merged_data_frame = left_data_frame.merge(right_data_frame, how=how, left_on=left_on, right_on=right_on)

    # Write the merged CSV file to the standard output stream.
    merged_data_frame.to_csv(path_or_buf=click.get_text_stream('stdout'), index=False, quoting=csv.QUOTE_NONNUMERIC)

    # Done!
    return

@cli.command('csvmatch-partial-v2', short_help='Merge the records in two CSV files by partially matching the version-2 UBIDs (format: "C-NE-SE").')
@click.option('--how', type=click.Choice(['left', 'right', 'outer', 'inner']), default='inner', show_default=True, help='the database-style join operation')
@click.option('--left-on', type=click.STRING, default=DEFAULT_FIELDNAME_WRITER_, show_default=True, help='the field name for the column to join on for the "LEFT" CSV file')
@click.option('--right-on', type=click.STRING, default=DEFAULT_FIELDNAME_WRITER_, show_default=True, help='the field name for the column to join on for the "RIGHT" CSV file')
@click.option('--left-temp-fieldname', type=click.STRING, default='__temp__', show_default=True, help='the new field to be created and used for temporarily storing the matching data for the "LEFT" CSV file')
@click.option('--right-temp-fieldname', type=click.STRING, default='__temp__', show_default=True, help='the new field to be created and used for temporarily storing the matching data for the "RIGHT" CSV file')
@click.option('--centroid/--no-centroid', default=False, help='whether or not to match the Open Location Code for the centroid')
@click.option('--northwest/--no-northwest', default=False, help='whether or not to match the Open Location Code for the northwest corner')
@click.option('--southeast/--no-southeast', default=False, help='whether or not to match the Open Location Code for the southeast corner')
@click.option('--drop-suffix-centroid', type=click.IntRange(0, None), default=0, show_default=True, help='the number of characters to drop (from the right) of the Open Location Code for the centroid')
@click.option('--drop-suffix-northwest', type=click.IntRange(0, None), default=0, show_default=True, help='the number of characters to drop (from the right) of the Open Location Code for the northwest corner')
@click.option('--drop-suffix-southeast', type=click.IntRange(0, None), default=0, show_default=True, help='the number of characters to drop (from the right) of the Open Location Code for the southeast corner')
@click.argument('left', type=click.File('r'))
@click.argument('right', type=click.File('r'))
def run_csv_match_partial_v2(how, left_on, right_on, left_temp_fieldname, right_temp_fieldname, centroid, northwest, southeast, drop_suffix_centroid, drop_suffix_northwest, drop_suffix_southeast, left, right):
    def temp_(code):
        """Generate value for temporary column.

        Arguments:
        code -- the UBID code

        Returns:
        The value for the temporary column.
        """

        # Does the partial match criteria include at least one OLC code?
        if centroid or northwest or southeast:
            # Is the specified UBID code valid?
            if buildingid.v2.isValid(code):
                # Separate the UBID code into three OLC codes.
                openlocationcodes = code.split(buildingid.v2.SEPARATOR_)

                # Extract the OLC codes.
                centroid_openlocationcode = openlocationcodes[buildingid.v2.INDEX_CENTROID_]
                northwest_openlocationcode = openlocationcodes[buildingid.v2.INDEX_NORTHWEST_]
                southeast_openlocationcode = openlocationcodes[buildingid.v2.INDEX_SOUTHEAST_]

                # Initialize new list of OLC codes.
                new_openlocationcodes = []

                if centroid:
                    if drop_suffix_centroid > 0:
                        # If the "--centroid" flag is set and the "--drop-suffix-centroid"
                        # option is non-zero, then drop the required number of
                        # characters, and append the new OLC code to the list.
                        new_openlocationcodes.append(centroid_openlocationcode[:(-1 * drop_suffix_centroid)])
                    else:
                        # Otherwise, append the unmodified OLC code to the list.
                        new_openlocationcodes.append(centroid_openlocationcode)

                if northwest:
                    if drop_suffix_northwest > 0:
                        # If the "--northwest" flag is set and the "--drop-suffix-northwest"
                        # option is non-zero, then drop the required number of
                        # characters, and append the new OLC code to the list.
                        new_openlocationcodes.append(northwest_openlocationcode[:(-1 * drop_suffix_northwest)])
                    else:
                        # Otherwise, append the unmodified OLC code to the list.
                        new_openlocationcodes.append(northwest_openlocationcode)

                if southeast:
                    if drop_suffix_southeast > 0:
                        # If the "--southeast" flag is set and the "--drop-suffix-southeast"
                        # option is non-zero, then drop the required number of
                        # characters, and append the new OLC code to the list.
                        new_openlocationcodes.append(southeast_openlocationcode[:(-1 * drop_suffix_southeast)])
                    else:
                        # Otherwise, append the unmodified OLC code to the list.
                        new_openlocationcodes.append(southeast_openlocationcode)

                if len(new_openlocationcodes) > 0:
                    # If the new list of OLC codes is non-empty, then join
                    # the OLC codes, and then return the result.
                    return buildingid.v2.SEPARATOR_.join(new_openlocationcodes)
                else:
                    # No result.
                    return None
            else:
                # No result.
                return None
        else:
            # No result.
            return None

    # Read the left and right CSV files.
    left_data_frame = pandas.read_csv(filepath_or_buffer=left)
    right_data_frame = pandas.read_csv(filepath_or_buffer=right)

    if left_temp_fieldname in left_data_frame:
        raise ValueError('Duplicate field in "LEFT" CSV file: {0}'.format(left_temp_fieldname))

    if right_temp_fieldname in right_data_frame:
        raise ValueError('Duplicate field in "RIGHT" CSV file: {0}'.format(right_temp_fieldname))

    # Create temporary columns.
    left_data_frame[left_temp_fieldname] = left_data_frame[left_on].map(lambda x: temp_(x))
    right_data_frame[right_temp_fieldname] = right_data_frame[right_on].map(lambda x: temp_(x))

    # Merge the left and right CSV files (using temporary columns).
    merged_data_frame = left_data_frame.merge(right_data_frame, how=how, left_on=left_temp_fieldname, right_on=right_temp_fieldname)

    # Delete temporary column for left CSV file.
    if left_temp_fieldname in merged_data_frame:
        del merged_data_frame[left_temp_fieldname]

    # Delete temporary column for right CSV file.
    if right_temp_fieldname in merged_data_frame:
        del merged_data_frame[right_temp_fieldname]

    # Write the merged CSV file to the standard output stream.
    merged_data_frame.to_csv(path_or_buf=click.get_text_stream('stdout'), index=False, quoting=csv.QUOTE_NONNUMERIC)

    # Done!
    return

@cli.command('csvmatch-partial-v3', short_help='Merge the records in two CSV files by partially matching the version-3 UBIDs (format: "C-n-e-s-w").')
@click.option('--how', type=click.Choice(['left', 'right', 'outer', 'inner']), default='inner', show_default=True, help='the database-style join operation')
@click.option('--left-on', type=click.STRING, default=DEFAULT_FIELDNAME_WRITER_, show_default=True, help='the field name for the column to join on for the "LEFT" CSV file')
@click.option('--right-on', type=click.STRING, default=DEFAULT_FIELDNAME_WRITER_, show_default=True, help='the field name for the column to join on for the "RIGHT" CSV file')
@click.option('--left-temp-fieldname', type=click.STRING, default='__temp__', show_default=True, help='the new field to be created and used for temporarily storing the matching data for the "LEFT" CSV file')
@click.option('--right-temp-fieldname', type=click.STRING, default='__temp__', show_default=True, help='the new field to be created and used for temporarily storing the matching data for the "RIGHT" CSV file')
@click.option('--centroid/--no-centroid', default=False, help='whether or not to match the Open Location Code for the centroid')
@click.option('--north/--no-north', default=False, help='whether or not to match the Chebyshev distance to the northern extent')
@click.option('--east/--no-east', default=False, help='whether or not to match the Chebyshev distance to the eastern extent')
@click.option('--south/--no-south', default=False, help='whether or not to match the Chebyshev distance to the southern extent')
@click.option('--west/--no-west', default=False, help='whether or not to match the Chebyshev distance to the western extent')
@click.option('--drop-suffix-centroid', type=click.IntRange(0, None), default=0, show_default=True, help='the number of characters to drop (from the right) of the Open Location Code for the centroid')
@click.argument('left', type=click.File('r'))
@click.argument('right', type=click.File('r'))
def run_csv_match_partial_v3(how, left_on, right_on, left_temp_fieldname, right_temp_fieldname, centroid, north, east, south, west, drop_suffix_centroid, left, right):
    def temp_(code):
        """Generate value for temporary column.

        Arguments:
        code -- the UBID code

        Returns:
        The value for the temporary column.
        """

        # Does the partial match criteria include at least one criterion?
        if centroid or north or east or south or west:
            match = buildingid.v3.RE_PATTERN_.match(code)

            # Is the specified UBID code valid?
            if match is None:
                return None
            else:
                # Initialize new list of OLC codes.
                new_openlocationcodes = []

                if centroid:
                    centroid_openlocationcode = match.group(buildingid.v3.RE_GROUP_OPENLOCATIONCODE_)

                    if drop_suffix_centroid > 0:
                        # If the "--centroid" flag is set and the "--drop-suffix-centroid"
                        # option is non-zero, then drop the required number of
                        # characters, and append the new OLC code to the list.
                        new_openlocationcodes.append(centroid_openlocationcode[:(-1 * drop_suffix_centroid)])
                    else:
                        # Otherwise, append the unmodified OLC code to the list.
                        new_openlocationcodes.append(centroid_openlocationcode)

                if north:
                    # If the "--north" flag is set, then append the Chebyshev
                    # distance to the northern extent to the list.
                    new_openlocationcodes.append(match.group(buildingid.v3.RE_GROUP_NORTH_))

                if east:
                    # If the "--east" flag is set, then append the Chebyshev
                    # distance to the eastern extent to the list.
                    new_openlocationcodes.append(match.group(buildingid.v3.RE_GROUP_EAST_))

                if south:
                    # If the "--south" flag is set, then append the Chebyshev
                    # distance to the southern extent to the list.
                    new_openlocationcodes.append(match.group(buildingid.v3.RE_GROUP_SOUTH_))

                if west:
                    # If the "--west" flag is set, then append the Chebyshev
                    # distance to the western extent to the list.
                    new_openlocationcodes.append(match.group(buildingid.v3.RE_GROUP_WEST_))

                if len(new_openlocationcodes) > 0:
                    # If the new list of OLC codes is non-empty, then join
                    # the OLC codes, and then return the result.
                    return buildingid.v3.SEPARATOR_.join(new_openlocationcodes)
                else:
                    # No result.
                    return None
        else:
            # No result.
            return None

    # Read the left and right CSV files.
    left_data_frame = pandas.read_csv(filepath_or_buffer=left)
    right_data_frame = pandas.read_csv(filepath_or_buffer=right)

    if left_temp_fieldname in left_data_frame:
        raise ValueError('Duplicate field in "LEFT" CSV file: {0}'.format(left_temp_fieldname))

    if right_temp_fieldname in right_data_frame:
        raise ValueError('Duplicate field in "RIGHT" CSV file: {0}'.format(right_temp_fieldname))

    # Create temporary columns.
    left_data_frame[left_temp_fieldname] = left_data_frame[left_on].map(lambda x: temp_(x))
    right_data_frame[right_temp_fieldname] = right_data_frame[right_on].map(lambda x: temp_(x))

    # Merge the left and right CSV files (using temporary columns).
    merged_data_frame = left_data_frame.merge(right_data_frame, how=how, left_on=left_temp_fieldname, right_on=right_temp_fieldname)

    # Delete temporary column for left CSV file.
    if left_temp_fieldname in merged_data_frame:
        del merged_data_frame[left_temp_fieldname]

    # Delete temporary column for right CSV file.
    if right_temp_fieldname in merged_data_frame:
        del merged_data_frame[right_temp_fieldname]

    # Write the merged CSV file to the standard output stream.
    merged_data_frame.to_csv(path_or_buf=click.get_text_stream('stdout'), index=False, quoting=csv.QUOTE_NONNUMERIC)

    # Done!
    return

if __name__ == '__main__':
    cli()
