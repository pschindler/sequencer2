#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "19-Jul-2009 13:28:58 viellieb"

#  file       test_log.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net

import logging
import sequencer2.tests
import server.tests
from sequencer2 import ptplog

logger=ptplog.ptplog(level=logging.INFO)

# Run tests
sequencer2.tests.run()
server.tests.run()
# test_log.py ends here
