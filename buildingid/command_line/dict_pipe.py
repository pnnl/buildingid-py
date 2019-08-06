# -*- coding: utf-8 -*-
#
# pnnl-buildingid: buildingid/command_line/dict_pipe.py
#
# Copyright (c) 2019, Battelle Memorial Institute
# All rights reserved.
#
# See LICENSE.txt and WARRANTY.txt for details.

import abc
import csv
import typing

from .exceptions import FieldNotFoundError, FieldNotUniqueError

T = typing.TypeVar('T')

class DictDecoder(abc.ABC, typing.Generic[T]):
    def __init__(self) -> None:
        super(DictDecoder, self).__init__()

    @abc.abstractmethod
    def decode(self, row: typing.Dict[str, str]) -> T:
        raise MethodNotImplemented()  # pragma: no cover

    @property
    @abc.abstractmethod
    def fieldnames(self) -> typing.List[str]:
        raise MethodNotImplemented()  # pragma: no cover

class DictEncoder(abc.ABC, typing.Generic[T]):
    def __init__(self) -> None:
        super(DictEncoder, self).__init__()

    @abc.abstractmethod
    def encode(self, inst: T) -> typing.Dict[str, typing.Any]:
        raise MethodNotImplemented()  # pragma: no cover

    @property
    @abc.abstractmethod
    def fieldnames(self) -> typing.List[str]:
        raise MethodNotImplemented()  # pragma: no cover

class DictPipe:
    def __init__(self, decoder_in: DictDecoder[T], encoder_out: DictEncoder[T], encoder_err: DictEncoder[BaseException]) -> None:
        super(DictPipe, self).__init__()

        self.decoder_in = decoder_in
        self.encoder_out = encoder_out
        self.encoder_err = encoder_err

    def run(self, io_in: typing.TextIO, io_out: typing.TextIO, io_err: typing.TextIO, args_in: list = [], kwargs_in: dict = {}, args_out: list = [], kwargs_out: dict = {}) -> None:
        csv_in = csv.DictReader(io_in, *args_in, **kwargs_in)

        fieldnames_in = csv_in.fieldnames
        fieldnames_in = [] if (fieldnames_in is None) else list(fieldnames_in)

        for fieldname in self.decoder_in.fieldnames:
            if not fieldname in fieldnames_in:
                raise FieldNotFoundError(fieldname)

        fieldnames_out = fieldnames_in.copy()

        for fieldname in self.encoder_out.fieldnames:
            if fieldname in fieldnames_out:
                raise FieldNotUniqueError(fieldname)

            fieldnames_out.append(fieldname)

        fieldnames_err = fieldnames_in.copy()

        for fieldname in self.encoder_err.fieldnames:
            if fieldname in fieldnames_err:
                raise FieldNotUniqueError(fieldname)

            fieldnames_err.append(fieldname)

        csv_out = csv.DictWriter(io_out, fieldnames_out, *args_out, **kwargs_out)
        csv_err = csv.DictWriter(io_err, fieldnames_err, *args_out, **kwargs_out)

        csv_out_writeheader_called = False
        csv_err_writeheader_called = False

        for in_row in csv_in:
            try:
                inst = self.decoder_in.decode(in_row)

                out_row = in_row.copy()
                out_row.update(self.encoder_out.encode(inst))
            except BaseException as exception:
                err_row = in_row.copy()
                err_row.update(self.encoder_err.encode(exception))

                if not csv_err_writeheader_called:
                    csv_err_writeheader_called = True

                    csv_err.writeheader()

                csv_err.writerow(err_row)
            else:
                if not csv_out_writeheader_called:
                    csv_out_writeheader_called = True

                    csv_out.writeheader()

                csv_out.writerow(out_row)

        return
