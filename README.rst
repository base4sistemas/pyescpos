
PyESCPOS
========

.. image:: https://pypip.in/status/pyescpos/badge.svg
    :target: https://pypi.python.org/pypi/pyescpos/
    :alt: Development status

.. image:: https://pypip.in/py_versions/pyescpos/badge.svg
    :target: https://pypi.python.org/pypi/pyescpos/
    :alt: Supported Python versions

.. image:: https://pypip.in/license/pyescpos/badge.svg
    :target: https://pypi.python.org/pypi/pyescpos/
    :alt: License

.. image:: https://pypip.in/version/pyescpos/badge.svg
    :target: https://pypi.python.org/pypi/pyescpos/
    :alt: Latest version

-------

A Python support for Epson |copy| ESC/POS |reg| compatible printers.

Read more at `Epson ESCPOS FAQ`_ (PDF document).

This library is inspired on Manuel F. Martinez work for `python-escpos`_
implementation.


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

Printing ESC/POS barcodes is straightforward. Instantiate desired symbology,
and call `barcode()` method. Or simply call convenient barcode methods
``ean13``, ``ean8`` and ``code128``.

.. sourcecode:: python

    from escpos.serial import SerialSettings
    from escpos.barcode import BarcodeEAN13
    from escpos.impl.epson import GenericESCPOS

    conn = SerialSettings.as_from('/dev/ttyS5:9600:8:1:N').get_connection()
    printer = GenericESCPOS(conn)
    printer.init()

    ean13 = BarcodeEAN13('4007817525074')
    printer.barcode(ean13)

    # conveniently, use the shortcut method
    printer.ean13('4007817525074')

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
