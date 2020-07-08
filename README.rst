
PyESCPOS
========

.. image:: https://travis-ci.org/base4sistemas/pyescpos.svg?branch=master
    :target: https://travis-ci.org/base4sistemas/pyescpos
    :alt: Build status

.. image:: https://img.shields.io/pypi/status/pyescpos.svg
    :target: https://pypi.python.org/pypi/pyescpos/
    :alt: Development status

.. image:: https://img.shields.io/pypi/pyversions/pyescpos.svg
    :target: https://pypi.python.org/pypi/pyescpos/
    :alt: Supported Python versions

.. image:: https://img.shields.io/pypi/l/pyescpos.svg
    :target: https://pypi.python.org/pypi/pyescpos/
    :alt: License

.. image:: https://img.shields.io/pypi/v/pyescpos.svg
    :target: https://pypi.python.org/pypi/pyescpos/
    :alt: Latest version

-------

A Python support for Epson |copy| ESC/POS |reg| compatible printers. Read more
at `Epson ESCPOS FAQ`_ (PDF document).

The ESC/POS |reg| is a standard that every manufacturer work on and modify to
suit their needs. That way, a sequence of commands in one printer does not
necessarily works (or does not work as expected) on another. At a distance, you
can say that all those tricky commands are identical from model to model (a
standard), but when you look just a little bit more deeper, you quickly realize
that they can be completely different, even between models belonging to the
same manufacturer.

This project aims to simplify the usage of printers, seeking for a lowest common
denominator between needed features and providing implementations that meet this
minimum for known models, so you do not have to modify the application code.


Current Implementations
=======================

Current implementations was tested against following hardware:

+-------------------------+-------------------+-------------------+-----------------------------------------+
| Manufacturer            | Models            | Firmware Versions | Notes                                   |
+=========================+===================+===================+=========================================+
| `Bematech S/A`_         | MP-2800 TH        | 2.2.1BQL          |                                         |
|                         |                   |                   |                                         |
+-------------------------+-------------------+-------------------+-----------------------------------------+
| `Bematech S/A`_         | MP-4200 TH        | 1.3, 1.6          |                                         |
|                         |                   |                   |                                         |
+-------------------------+-------------------+-------------------+-----------------------------------------+
| `Epson`_                | TM-T20            | 1.14              |                                         |
|                         |                   |                   |                                         |
+-------------------------+-------------------+-------------------+-----------------------------------------+
| `Elgin`_                | Elgin i9          | 1.03.20,          |                                         |
|                         |                   | 1.03.24,          |                                         |
|                         |                   | 1.03.31           |                                         |
+-------------------------+-------------------+-------------------+-----------------------------------------+
| `Elgin`_                | Elgin i7          | 1.00.08           |                                         |
|                         |                   |                   |                                         |
+-------------------------+-------------------+-------------------+-----------------------------------------+
| `Elgin`_                | Elgin RM-22       | 1.00.09           | Elgin RM-22 portable thermal mini       |
|                         |                   |                   | printer                                 |
+-------------------------+-------------------+-------------------+-----------------------------------------+
| `Nitere`_               | NPDV-1020         | -                 | Multifunction Terminal model TMF-101/IG |
|                         |                   |                   | (an alias for CB55-C model)             |
+-------------------------+-------------------+-------------------+-----------------------------------------+
| Unknown OEM             | CB55-C            | 1.3.5             | Embedded in `Nitere`_ NPDV-1020 (model  |
|                         |                   |                   | TMF-101/IG)                             |
+-------------------------+-------------------+-------------------+-----------------------------------------+
| `Urmet Daruma`_         | DR700 L/H/M and   | 02.51.00,         |                                         |
|                         | DR700 L-e/H-e     | 01.20.00,         |                                         |
|                         |                   | 01.21.00          |                                         |
+-------------------------+-------------------+-------------------+-----------------------------------------+
| `Urmet Daruma`_         | DR800 L/H         | 03.13.01          |                                         |
|                         |                   |                   |                                         |
|                         |                   |                   |                                         |
+-------------------------+-------------------+-------------------+-----------------------------------------+

You can get a list of all available implementations with the following snippet:

.. sourcecode:: python

    from escpos import helpers

    for impl in helpers.find_implementations(sort_by='model.name'):
        print('{:.<25} {}'.format(impl.model.name, impl.fqname))

Which produces an output similar to::

    Bematech MP-2800 TH...... escpos.impl.bematech.MP2800TH
    Bematech MP-4200 TH...... escpos.impl.bematech.MP4200TH
    CB55-C................... escpos.impl.unknown.CB55C
    Daruma DR700............. escpos.impl.daruma.DR700
    Daruma DR800............. escpos.impl.daruma.DR800
    Elgin I7................. escpos.impl.elgin.ElginI7
    Elgin I9................. escpos.impl.elgin.ElginI9
    Elgin RM-22.............. escpos.impl.elgin.ElginRM22
    Epson TM-T20............. escpos.impl.epson.TMT20
    Generic Daruma........... escpos.impl.daruma.DarumaGeneric
    Generic ESC/POS.......... escpos.impl.epson.GenericESCPOS
    Generic Elgin............ escpos.impl.elgin.ElginGeneric
    Nitere NPDV-1020......... escpos.impl.nitere.NitereNPDV1020


Usage Examples
==============

Network TCP/IP Example
----------------------

You can connect to your printer through network TCP/IP interface:

.. sourcecode:: python

    from escpos import NetworkConnection
    from escpos.impl.epson import GenericESCPOS

    conn = NetworkConnection.create('10.0.0.101:9100')
    printer = GenericESCPOS(conn)
    printer.init()
    printer.text('Hello World!')


Serial Example
--------------

Support for Serial connections is optional. If you need it you should have
`PySerial`_ library installed. You may do it through PIP issuing ``pip install
PyESCPOS[serial]``.

Here is how you can make a Serial connection:

.. sourcecode:: python

    from escpos import SerialConnection
    from escpos.impl.epson import GenericESCPOS

    # connect to port 'ttyS5' @ 9600 Bps, assuming RTS/CTS for handshaking
    conn = SerialConnection.create('/dev/ttyS5:9600,8,1,N')
    printer = GenericESCPOS(conn)
    printer.init()
    printer.text('Hello World!')


Bluetooth Example
-----------------

Support for Bluetooth (via RFCOMM) connection is optional. If you need it you
should have `PyBluez`_ library installed. One option may be installing PyESCPOS
through PIP issuing ``pip install PyESCPOS[bluetooth]``.

Here is how you can make a Bluetooth connection:

.. sourcecode:: python

    from escpos import BluetoothConnection
    from escpos.impl.epson import GenericESCPOS

    # uses SPD (service port discovery) services to find which port to connect to
    conn = BluetoothConnection.create('00:01:02:03:04:05')
    printer = GenericESCPOS(conn)
    printer.init()
    printer.text('Hello World!')

If you know in which port you can connect beforehand, just pass its number after
device address using a forward slash, for example ``00:01:02:03:04:05/4``, will
connect to port ``4`` on ``00:01:02:03:04:05`` address.


USB Example
-----------

Support for USB connections is optional. If you need it you should have
`PyUSB`_ library installed. You may do it through PIP issuing ``pip install
PyESCPOS[usb]``. Be aware for printers with more than one USB interface, so
you may have to configure which interface is active.

Here is how you can make an USB connection:

.. sourcecode:: python

    from escpos.ifusb import USBConnection
    from escpos.impl.elgin import ElginRM22

    conn = USBConnection.create('20d1:7008,interface=0,ep_out=3,ep_in=0')
    printer = ElginRM22(conn)
    printer.init()
    printer.text('Hello World!')


File Print Example
------------------

This printer “prints” just into a file-handle. Especially on \*nix-systems this
comes very handy. A common use case is when you have a parallel port printer or
any other printer that are directly attached to the file system. Note that you
may want to stay away from using USB-to- Parallel-Adapters since they are
extremely unreliable and produce many arbitrary errors.

.. sourcecode:: python

    from escpos import FileConnection
    from escpos.impl.elgin import ElginI9

    conn = FileConnection('/dev/usb/lp1')
    printer = ElginI9(conn)
    printer.init()
    printer.text('Hello World!')
    print(printer.device.output)


Dummy Print Example
-------------------

The Dummy-printer is mainly for testing- and debugging-purposes. It stores all
of the “output” as raw ESC/POS in a string and returns that.

.. sourcecode:: python

    from escpos import DummyConnection
    from escpos.impl.epson import GenericESCPOS

    conn = DummyConnection()
    printer = GenericESCPOS(conn)
    printer.init()
    printer.text('Hello World!')
    print(printer.device.output)


Printing Barcodes
-----------------

There is a default set of parameters for printing barcodes. Each ESC/POS
implementation will take care of the details and try their best to print your
barcode as you asked.

.. sourcecode:: python

    from escpos import barcode
    from escpos import SerialConnection
    from escpos.impl.epson import GenericESCPOS

    conn = SerialConnection.create('COM1:9600,8,1,N')
    printer = GenericESCPOS(conn)
    printer.init()
    printer.code128(
            '0123456789',
            barcode_height=96,  # ~12mm (~1/2")
            barcode_width=barcode.BARCODE_DOUBLE_WIDTH,
            barcode_hri=barcode.BARCODE_HRI_BOTTOM
        )

    printer.lf()

    printer.ean13(
            '4007817525074',
            barcode_height=120,  # ~15mm (~9/16"),
            barcode_width=barcode.BARCODE_NORMAL_WIDTH,
            barcode_hri=barcode.BARCODE_HRI_TOP
        )

    printer.cut()

The barcode data you pass as a parameter should be complete including check
digits and any other payload data required that makes that data valid for the
symbology you're dealing with. Thus, if you need to print an EAN-13 barcode,
for example, you need to provide all thirteen digits.


Configuring Resilient Connections
---------------------------------

Network (TCP/IP) and Bluetooth (RFCOMM) connections provided by PyESCPOS both
use a simple `exponential backoff`_ algorithm to implement a (more) resilient
connection to the device. Your application or your users can configure retry
parameters through environment variables (or files):

* ``ESCPOS_BACKOFF_MAXTRIES`` (int ``> 0``, defaults to ``3``) Number of tries
  before give up;

* ``ESCPOS_BACKOFF_DELAY`` (int ``> 0``, defaults to ``3``) Delay in seconds
  between retries;

* ``ESCPOS_BACKOFF_FACTOR`` (int ``> 1``, defaults to ``2``) Multiply factor
  in which delay will be increased each retry.

This library may use `python-decouple`_ if available to grab those
configuration values from environment variables or from a settings file,
depending on how you have configured ``decouple``. If not, it falls back to
standard lib ``os.getenv``.


More Information
----------------

You will find more information in the `PyESCPOS wiki`_ pages.


You are Welcome to Help
=======================

Here is how you setup a development enviroment:

.. sourcecode:: sh

    git clone git@github.com:base4sistemas/pyescpos.git
    cd pyescpos
    python -m venv .env_escpos
    source .env_escpos/bin/activate
    pip install -r requirements/dev.txt
    tox

If you gonna work with a specific type of connection (eg. Bluetooth or Serial)
you may use ``requirements/bluetooth.txt`` or ``requirements/serial.txt``.
Have a look inside ``requirements/`` directory for the options available.


Acknowledgement
===============

This project is inspired on Manuel F. Martinez work for `python-escpos`_
implementation, among other projects, whose specific bits of work (available
here on Github and many other open-source repositories) has helped so much.


Disclaimer
==========

Please, read this **disclaimer**.

    None of the vendors cited in this project agree or endorse any of the
    patterns or implementations. Its names are used only to maintain context.

..
    Sphinx Documentation: Substitutions at
    http://sphinx-doc.org/rest.html#substitutions
    Codes copied from reStructuredText Standard Definition Files at
    http://docutils.sourceforge.net/docutils/parsers/rst/include/isonum.txt

.. |copy| unicode:: U+00A9 .. COPYRIGHT SIGN
    :ltrim:

.. |reg|  unicode:: U+00AE .. REGISTERED SIGN
    :ltrim:

.. _`PyESCPOS wiki`: https://github.com/base4sistemas/pyescpos/wiki
.. _`Epson ESCPOS FAQ`: http://content.epson.de/fileadmin/content/files/RSD/downloads/escpos.pdf
.. _`python-escpos`: https://github.com/manpaz/python-escpos
.. _`python-decouple`: https://github.com/henriquebastos/python-decouple
.. _`PySerial`: https://pyserial.readthedocs.io/en/latest/
.. _`PyBluez`: http://karulis.github.io/pybluez/
.. _`PyUSB`: https://pyusb.github.io/pyusb/
.. _`Epson`: http://www.epson.com/
.. _`Elgin`: http://www.elgin.com.br/
.. _`Nitere`: http://www.nitere.com.br/
.. _`Bematech S/A`: http://www.bematechus.com/
.. _`Urmet Daruma`: http://daruma.com.br/
.. _`exponential backoff`: https://en.wikipedia.org/wiki/Exponential_backoff
