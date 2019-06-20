# -*- coding: utf-8 -*-
#
# pnnl-buildingid: buildingid/command_line/exceptions.py
#
# Copyright (c) 2019, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE.txt and WARRANTY.txt for details.

class CustomException(Exception):
    def __init__(self, msg: str) -> None:
        super(CustomException, self).__init__()

        self.msg = msg

    def __str__(self) -> str:
        return self.msg

class FieldNotFoundError(CustomException):
    def __init__(self, fieldname: str) -> None:
        msg = 'field \'{0}\' is not defined'.format(fieldname.replace('\'','\\\''))

        super(FieldNotFoundError, self).__init__(msg)

        self.fieldname = fieldname

class FieldNotUniqueError(CustomException):
    def __init__(self, fieldname: str) -> None:
        msg = 'field \'{0}\' has already been taken'.format(fieldname.replace('\'','\\\''))

        super(FieldNotUniqueError, self).__init__(msg)

        self.fieldname = fieldname
