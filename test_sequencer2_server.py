#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-08-13 09:35:52 c704271"

#  file       test_sequencer2_server.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net

import logging

from sequencer2 import ptplog
from server import main_program
logger=ptplog.ptplog(level=logging.DEBUG)

main_program = main_program.MainProgram()
main_program.start_server()

# test_sequencer2_server.py ends here
