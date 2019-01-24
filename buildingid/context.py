# -*- coding: utf-8 -*-
#
# pnnl-buildingid: buildingid/context.py
#
# Copyright (c) 2018, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE.txt and WARRANTY.txt for details.

import os
import sys

openlocationcode_abspath_ = os.path.abspath(os.path.join(os.path.dirname(__file__), '../open-location-code-68ba7ed4c6e7fae41a0255e4394ba1fa0f8435bb/python'))
sys.path.insert(0, openlocationcode_abspath_)
import openlocationcode
sys.path.remove(openlocationcode_abspath_)
