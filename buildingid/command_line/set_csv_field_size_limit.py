# -*- coding: utf-8 -*-
#
# pnnl-buildingid: buildingid/command_line/set_csv_field_size_limit.py
#
# Copyright (c) 2019, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE.txt and WARRANTY.txt for details.

import csv
import sys

# c.f., https://stackoverflow.com/questions/15063936/csv-error-field-larger-than-field-limit-131072
def set_csv_field_size_limit(maxsize: int = sys.maxsize) -> None:
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
