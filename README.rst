
PyESCPOS
========

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

This project is inspired on Manuel F. Martinez work for `python-escpos`_
implementation, among other projects, whose specific bits of work (available
here on Github and many other open-source repositories) has helped so much.

The ESC/POS |reg| is a standard that every manufacturer tend to modify to suit
their (even already implemented) needs. Indeed, there is no standard but
something awkward, an illusion of a standard. On the surface, one can say
that it's pretty much the same, but when you look just a little bit more deeper,
you quickly realize that they are almost completely different, even between
models belonging to the same manufacturer.

This project aims to make viable the use, at the *point-of-sale* (POS), of
different printers (the most common ones, at least) that are minimally based on
ESC/POS |reg| standard, without need to modify the client application code. To
achieve this, it is necessary to draw a lowest common denominator between
features and provide implementations that seek to meet this minimum.


Current Implementations
=======================

Current implementations was tested against following hardware:

+-------------------------+-------------------+-------------------+-----------------------------------------+
| Manufacturer            | Models            | Firmware Versions | Notes                                   |
+=========================+===================+===================+=========================================+
| `Bematech S/A`_         | MP-4200 TH        | 1.3, 1.6          |                                         |
|                         |                   |                   |                                         |
+-------------------------+-------------------+-------------------+-----------------------------------------+
| `Epson`_                | TM-T20            | 1.14              |                                         |
|                         |                   |                   |                                         |
+-------------------------+-------------------+-------------------+-----------------------------------------+
| `Elgin`_                | Elgin i9          | CV1.03.20         |                                         |
|                         |                   |                   |                                         |
+-------------------------+-------------------+-------------------+-----------------------------------------+
| `Elgin`_                | Elgin i7          | CV1.00.08         |                                         |
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

You can get a list of all available implementations with the following snippet:

.. sourcecode:: python

    from escpos import helpers

    for impl in helpers.find_implementations(sort_by='model.name'):
        print('{:.<25} {}'.format(impl.model.name, impl.fqname))

Which produces an output similar to::

    Bematech MP-4200 TH...... escpos.impl.bematech.MP4200TH
    CB55-C................... escpos.impl.unknown.CB55C
    Daruma DR700............. escpos.impl.daruma.DR700
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

Serial RS232 Example
--------------------

Serial communications support requires `PySerial`_ version 2.7 or later.

.. sourcecode:: python

    from escpos import SerialConnection
    from escpos.impl.epson import GenericESCPOS

    # assumes RTS/CTS for 'ttyS5' and infers an instance of RTSCTSConnection
    conn = SerialConnection.create('/dev/ttyS5:9600,8,1,N')
    printer = GenericESCPOS(conn)
    printer.init()
    printer.text('Hello World!')


Network TCP/IP Example
----------------------

You can connect to your printer through network TCP/IP interface.

.. sourcecode:: python

    from escpos import NetworkConnection
    from escpos.impl.epson import GenericESCPOS

    conn = NetworkConnection.create('10.0.0.101:9100')
    printer = GenericESCPOS(conn)
    printer.init()
    printer.text('Hello World!')


Bluetooth Example
-----------------

You can connect to your printer through a bluetooth interface (only via RFCOMM).
Bluetooth support requires `PyBluez`_ version 0.22.

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


File Print Example
------------------

This printer “prints” just into a file-handle. Especially on *nix-systems this
comes very handy. A common use case is when you hava parallel port printer or
any other printer that are directly attached to the filesystem. Note that you
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
    from escpos.serial import SerialConnection
    from escpos.impl.epson import GenericESCPOS

    conn = SerialConnection.create('COM1:9600,8,1,N')
    printer = GenericESCPOS(conn)
    printer.init()
    printer.code128('0123456789',
            barcode_height=96, # ~12mm (~1/2")
            barcode_width=barcode.BARCODE_DOUBLE_WIDTH,
            barcode_hri=barcode.BARCODE_HRI_BOTTOM)

    printer.lf()

    printer.ean13('4007817525074',
            barcode_height=120, # ~15mm (~9/16"),
            barcode_width=barcode.BARCODE_NORMAL_WIDTH,
            barcode_hri=barcode.BARCODE_HRI_TOP)

    printer.cut()


The barcode data should be complete, that is, an EAN-13 barcode is formed from
twelve digits plus check-digit. Most of the ESC/POS command implementations
require only twelve digits and automaticaly calculate the check-digit.
If you are dealing with, say, EAN-13 codes without the thirteenth-digit (the
check-digit) just append zero (``0``) to the barcode class (or method) argument,
so they can pass RE validation.

.. sourcecode::

    printer.ean13('4007817525074')  # is OK
    printer.ean13('400781752507')   # raises ValueError
    printer.ean13('4007817525070')  # is OK and prints 4007817525074 as expected


Configuring Resilient Connections
---------------------------------

Network (TCP/IP) and Bluetooth (RFCOMM) connections provided by PyESCPOS both
use a simple `exponential backoff`_ algorithm to implement a (more) resilient
connection to the device. Your application or your users can configure *backoff*
retry parameters through a well-known INI-like file format:

.. sourcecode:: ini

    [retry]
    max_tries = 3
    delay = 3
    factor = 2

Whose parameters are:

* ``max_tries`` (integer ``> 0``) Number of tries before give up;
* ``delay`` (integer ``> 0``) Delay between retries (in seconds);
* ``factor`` (integer ``> 1``) Multiply factor in which delay will be increased
  for the next retry.

Normally that file lives in ``~/.escpos/config.cfg`` but you can determine
where you want to put this file. For that you must call ``config.configure``
function indicating full path to the configuration file, for example:

.. sourcecode:: python

    from escpos import config
    config.configure(filename='/path/to/config.cfg')

Your application must call ``config.configure`` before importing anything else.


More Examples
-------------

Eventually you may find more examples in the `PyESCPOS wiki`_ pages.


Disclaimer
==========

It is important that you read this **disclaimer**.

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
.. _`PySerial`: http://pyserial.sourceforge.net/
.. _`PyBluez`: http://karulis.github.io/pybluez/
.. _`Epson`: http://www.epson.com/
.. _`Elgin`: http://www.elgin.com.br/
.. _`Nitere`: http://www.nitere.com.br/
.. _`Bematech S/A`: http://www.bematechus.com/
.. _`Urmet Daruma`: http://daruma.com.br/
.. _`exponential backoff`: https://en.wikipedia.org/wiki/Exponential_backoff
