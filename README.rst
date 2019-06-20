=================================
Unique Building Identifier (UBID)
=================================

**Website:** https://buildingid.pnnl.gov/

-------------
Documentation
-------------

Install
=======

To complete this guide, `Git <https://git-scm.com/>`_ and `Python 3 <https://www.python.org/>`_ are required.
Dependencies are automatically installed using `pip <https://pypi.python.org/pypi/pip>`_.

Clone the repository and submodules, and then install the ``pnnl-buildingid`` package:

::

  git clone https://github.com/pnnl/buildingid-py
  cd buildingid-py
  git submodule update --init
  pip3 install -e .

Verify the location of the ``buildingid`` command:

::

  which buildingid
  #=> /usr/local/bin/buildingid

Uninstall
=========

Use `pip <https://pypi.python.org/pypi/pip>`_ to remove the ``pnnl-buildingid`` package:

::

  pip3 uninstall pnnl-buildingid

Test
====

Test the ``pnnl-buildingid`` package using the `nose <https://pypi.org/project/nose/>`_ package:

::

  nosetests tests/

Coverage testing is enabled using the `coverage <https://pypi.org/project/coverage/>`_ package:

::

  nosetests --with-coverage --cover-html --cover-package=buildingid tests/

Usage
=====

The ``pnnl-buildingid`` package supports two usages:

* Application programming interface (API)
* Command-line interface (CLI; the ``buildingid`` command)

The API
```````

* ``buildingid.code``

  - ``Code``

  - ``CodeArea``

    + ``encode() -> Code``

    + ``resize() -> CodeArea``

  - ``decode(Code) -> CodeArea``

  - ``encode(float, float, float, float, float, float, **kwargs) -> Code``

  - ``isValid(Code) -> bool``

In the following example, a UBID code is decoded and then re-encoded:

::

  #!/usr/bin/env python3
  # -*- coding: utf-8 -*-

  import buildingid.code

  if __name__ == '__main__':
    # Initialize UBID code.
    orig_code = '849VQJH6+95J-51-58-42-50'
    print(orig_code)

    # Decode UBID code.
    orig_code_area = buildingid.code.decode(orig_code)
    print(orig_code_area)

    # Resize resulting UBID code area.
    #
    # The effect of this operation is that the length and width of the UBID code
    # area are reduced by half an OLC code area.
    new_code_area = orig_code_area.resize()
    print(new_code_area)

    # Encode new UBID code area.
    new_code = new_code_area.encode()
    print(new_code)

    # Test that new UBID code and UBID code area match the originals.
    assert (orig_code == new_code)
    assert (orig_code_area == new_code_area)

The CLI
```````

View the documentation for the ``buildingid`` command using the ``--help`` command-line option:

::

  buildingid --help
  #=> Usage: buildingid [OPTIONS] COMMAND [ARGS]...
  #=> <<more lines of output>>

View the documentation for a sub-command of the ``buildingid`` command using the ``--help`` command-line option.
For example, to view the documentation for the "append2csv" sub-command:

::

  buildingid append2csv --help
  #=> Usage: buildingid append2csv [OPTIONS] [latlng|wkb|wkt]
  #=> <<more lines of output>>

Commands
^^^^^^^^

+---------------------+--------------------------------------------------------+
| Command name        | Description                                            |
+=====================+========================================================+
| append2csv          | Read CSV file from stdin, append UBID field, and write |
|                     | CSV file to stdout.                                    |
+---------------------+--------------------------------------------------------+

-------
License
-------

`The 2-Clause BSD License <https://opensource.org/licenses/BSD-2-Clause>`_

-------------
Contributions
-------------

Contributions are accepted on `GitHub <https://github.com/>`_ via the fork and pull request workflow.
See `here <https://help.github.com/articles/using-pull-requests/>`_ for more information.
