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

  git clone https://github.com/pnnl/buildingid
  cd buildingid
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

Test the ``pnnl-buildingid`` package using the `unittest <https://docs.python.org/3/library/unittest.html>`_ package from the standard library:

::

  python3 -m "unittest" tests/*

Usage
=====

The ``pnnl-buildingid`` package supports two usages:

* Application programming interface (API)
* Command-line interface (CLI; the ``buildingid`` command)

The API
```````

UBID codecs are encapsulated in separate modules:

* ``buildingid.v1`` (format: "C-h-w"; **deprecated**)
* ``buildingid.v2`` (format: "C-NW-SE")
* ``buildingid.v3`` (format: "C-n-e-s-w")

Modules export the same API:

* ``decode(code: str) -> buildingid.CodeArea``
* ``encode(latitudeLo: float, longitudeLo: float, latitudeHi: float, longitudeHi: float, latitudeCenter: float, longitudeCenter: float, **kwargs) -> str``
* ``encodeCodeArea(parent: buildingid.CodeArea) -> str``
* ``isValid(code: str) -> bool``

In the following example, a UBID code is decoded and then re-encoded:

::

  #!/usr/bin/env python3

  # Use the "C-NW-SE" format for UBID codes.
  import buildingid.v2

  if __name__ == '__main__':
    # Initialize UBID code.
    code = '849VQJH6+95J-849VQJH5+VGW-849VQJG6+XV8'
    print(code)

    # Decode the UBID code.
    code_area = buildingid.v2.decode(code)
    print(code_area)

    # Resize the resulting UBID code area.
    #
    # The effect of this operation is that the height and width of the UBID code
    # area are reduced by half an OLC code area.
    new_code_area = code_area.resize()
    print(new_code_area)

    # Encode the new UBID code area.
    new_code = buildingid.v2.encodeCodeArea(new_code_area)
    print(new_code)

    # Test that the new UBID code and code area match the originals.
    print(code_area == new_code_area)
    print(code == new_code)

The CLI
```````

View the documentation for the ``buildingid`` command using the ``--help`` command-line option:

::

  buildingid --help
  #=> Usage: buildingid [OPTIONS] COMMAND [ARGS]...
  #=> <<more lines of output>>

View the documentation for a sub-command of the ``buildingid`` command using the ``--help`` command-line option.
For example, to view the documentation for the "convert" sub-command:

::

  buildingid convert --help
  #=> Usage: buildingid convert [OPTIONS]
  #=> <<more lines of output>>

Commands
^^^^^^^^

+---------------------+--------------------------------------------------------+
| Command name        | Description                                            |
+=====================+========================================================+
| append2csv          | Read CSV file from stdin, append UBID field, and write |
|                     | CSV file to stdout.                                    |
+---------------------+--------------------------------------------------------+
| convert             | Read UBID (one per line) from stdin, convert UBID, and |
|                     | write UBID (one per line) to stdout. Write invalid UBID|
|                     | (one per line) to stderr.                              |
+---------------------+--------------------------------------------------------+
| csvmatch-exact      | Merge the records in two CSV files by exactly matching |
|                     | the UBIDs.                                             |
+---------------------+--------------------------------------------------------+
| csvmatch-partial-v2 | Merge the records in two CSV files by partially        |
|                     | matching the version-2 UBIDs (format: "C-NE-SE").      |
+---------------------+--------------------------------------------------------+
| csvmatch-partial-v3 | Merge the records in two CSV files by partially        |
|                     | matching the version-3 UBIDs (format: "C-n-e-s-w").    |
+---------------------+--------------------------------------------------------+

----
Data
----

A shell script that downloads publicly-available data and assigns UBID codes is
located in the ``bin/get_buildingid_data.sh`` source file.

-------
License
-------

BSD 3-clause "New" or "Revised" license.

-------------
Contributions
-------------

Contributions are accepted on `GitHub <https://github.com/>`_ via the fork and pull request workflow.
See `here <https://help.github.com/articles/using-pull-requests/>`_ for more information.
