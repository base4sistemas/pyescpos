
PyESCPOS
========

.. image:: https://img.shields.io/badge/status-planning-red.svg
    :target: https://pypi.python.org/pypi/pyescpos/
    :alt: Development status

.. image:: https://img.shields.io/badge/python%20version-2.7-blue.svg
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
features and provide implementations that seek to meet this minimum. At this
stage of the project, "minimum" is still a fuzzy word.


Tested Hardware
===============

Current implementation was tested against following hardwares:

+-------------------------+-------------------+-------------------+
| Manufacturer            | Models            | Firmware Versions |
+=========================+===================+===================+
| `Epson`_                | TM-T20            | 1.14              |
|                         |                   |                   |
+-------------------------+-------------------+-------------------+
| `Elgin`_                | Elgin i9          | CV1.03.20         |
|                         |                   |                   |
+-------------------------+-------------------+-------------------+
| `Urmet Daruma`_         | DR700 L/H/M and   | 02.51.00,         |
|                         | DR700 L-e/H-e     | 01.20.00,         |
|                         |                   | 01.21.00          |
+-------------------------+-------------------+-------------------+
| `Bematech S/A`_         | MP-4200 TH        | 1.3, 1.6          |
|                         |                   |                   |
+-------------------------+-------------------+-------------------+


Example Usage
=============

Serial RS232 Example
--------------------

Serial communications support requires `PySerial`_ version 2.7 or later.

.. sourcecode:: python

    from escpos.serial import SerialSettings
    from escpos.impl.epson import GenericESCPOS

    # assumes RTS/CTS for 'ttyS5' and infers an instance of RTSCTSConnection
    conn = SerialSettings.as_from('/dev/ttyS5:9600,8,1,N').get_connection()
    printer = GenericESCPOS(conn)
    printer.init()
    printer.text('Hello World!')


USB Example
-----------

USB support requires `PyUSB`_.

.. sourcecode:: python

    # TODO: USB support example.


Bluetooth Example
-----------------

Bluetooth support requires `PyBlueZ`_ (*not yet implemented*).

.. sourcecode:: python

    from escpos.bluetooth import BluetoothConnection
    from escpos.impl.epson import GenericESCPOS

    printer = GenericESCPOS(BluetoothConnection('01:0a:02:0b:03:0c'))
    printer.init()
    printer.text('Hello World!')


Printing Barcodes
-----------------

There is a default set of parameters for printing barcodes. Each ESC/POS
implementation will take care of the details and try their best to print your
barcode as you asked.

.. sourcecode:: python

    from escpos import barcode
    from escpos.serial import SerialSettings
    from escpos.impl.epson import GenericESCPOS

    conn = SerialSettings.as_from('COM1:9600:8:1:N').get_connection()
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
twelve digits plus check-digit. Most of the ESC/POS commands implementations
requires only twelve digits and automaticaly calculate the check-digit.
If you are dealing with, say, EAN-13 codes without the thirteenth-digit (the
check-digit) just append zero (``0``) to the barcode class (or method) argument,
so they can pass RE validation.

.. sourcecode::

    printer.ean13('4007817525074')  # is OK
    printer.ean13('400781752507')   # raises ValueError
    printer.ean13('4007817525070')  # is OK and prints 4007817525074 as expected


Disclaimer
==========

It is important that you read this **disclaimer**.

    None of the vendors or manufacturers cited in this entire project
    agree or endorse any of the patterns or implementations used. its
    names are used only where it makes sense and/or to maintain context.

..
    Sphinx Documentation: Substitutions at
    http://sphinx-doc.org/rest.html#substitutions
    Codes copied from reStructuredText Standard Definition Files at
    http://docutils.sourceforge.net/docutils/parsers/rst/include/isonum.txt

.. |copy| unicode:: U+00A9 .. COPYRIGHT SIGN
    :ltrim:

.. |reg|  unicode:: U+00AE .. REGISTERED SIGN
    :ltrim:

.. _`Epson ESCPOS FAQ`: http://content.epson.de/fileadmin/content/files/RSD/downloads/escpos.pdf
.. _`python-escpos`: https://github.com/manpaz/python-escpos
.. _`PySerial`: http://pyserial.sourceforge.net/
.. _`PyUSB`: http://walac.github.io/pyusb/
.. _`PyBlueZ`: https://github.com/manuelnaranjo/PyBlueZ
.. _`Epson`: http://www.epson.com/
.. _`Elgin`: http://www.elgin.com.br/
.. _`Urmet Daruma`: http://daruma.com.br/
.. _`Bematech S/A`: http://www.bematechus.com/
