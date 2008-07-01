#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-06-24 13:14:48 c704271"

#  file       __init__.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net
"""server
======

  This is the server package for the sequencer2.

  It depends on the sequencer2 module

  G{packagetree}

  Basic usage:
  ------------

    >>> import logging
    >>> from sequencer2 import ptplog
    >>> from server import main_program
    >>> logger=ptplog.ptplog(level=logging.DEBUG)
    >>> main_program = main_program.MainProgram()
    >>> main_program.start_server()

  Documentation
  -------------

    Documentation on the include files may be found in the user_function
    module documentation:
    L{server.user_function}

    Documentation about the main loop of the server are found in L{server.main_program}

    Documentation regarding the compiler can be found in L{sequencer2}

  Configuration
  -------------

    The Configuration is managed by the C{sequencer2/config} module.
    The default config file location is config/sequencer2.ini

    An example configration is:

    >>> Example Config
    [PTP]
    box_ip_address   = 192.168.0.229
    [SERVER]
    server_port = 8880
    server_answer = True
    server_pre_return = True
    DIO_configuration_file = None
    sequence_dir = PulseSequences/protected/
    include_dir = PulseSequences/includes2/
    nonet = True
    reference_frequency = 800.0

  The import relations
  --------------------

  G{importgraph user_function}

  Testing
  -------

    Basic unittests are defined in server/tests
"""

# __init__.py ends here
