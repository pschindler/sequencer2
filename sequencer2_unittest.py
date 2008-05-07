#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-03-26 08:19:47 c704271"

#  file       test_log.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net

import logging
import sequencer2.tests

level = logging.DEBUG

logger = logging.getLogger("sequencer2")
logger.setLevel(level)
#create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(level)
#create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
#add formatter to ch
ch.setFormatter(formatter)
#add ch to logger
logger.addHandler(ch)

# Run tests
sequencer2.tests.run()
# test_log.py ends here
