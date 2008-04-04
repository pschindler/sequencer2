#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-03-26 09:00:16 c704271"

#  file       logging.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net
import logging

class ptplog:

    def __init__(self, filename=None, level=logging.WARNING):

        logger = logging.getLogger("sequencer2")
        logger.setLevel(level)
        #create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(level)
        #create formatter
        if filename == None:
            formatter = logging.Formatter("%(levelname)s - %(message)s")
        else:
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        #add formatter to ch
        ch.setFormatter(formatter)
        #add ch to logger
        logger.addHandler(ch)
        self.logger = logger

# logging.py ends here
