#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-05-30 11:32:58 c704271"

#  file       logging.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net
"""Generates a loging object for the python logging framework"""

import logging

class ptplog:
    """Generate a Logger with the name sequencer2
    """
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

        level2 = level
        logger2 = logging.getLogger("api")
        logger2.setLevel(logging.WARN)
        ch2 = logging.StreamHandler()
        ch2.setLevel(level)
        #create formatter
        if filename == None:
            formatter = logging.Formatter("API :  %(message)s")
        else:
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        #add formatter to ch
        ch2.setFormatter(formatter)
        #add ch to logger
        #create console handler and set level to debug
        logger2.addHandler(ch2)
        self.logger2 = logger2

        level3 = level
        logger3 = logging.getLogger("server")
        logger3.setLevel(level2)
        ch3 = logging.StreamHandler()
        ch3.setLevel(level)
        #create formatter
        if filename == None:
            formatter = logging.Formatter("SERVER : %(levelname)s  %(message)s")
        else:
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        #add formatter to ch
        ch3.setFormatter(formatter)
        #add ch to logger
        #create console handler and set level to debug
        logger3.addHandler(ch3)
        self.logger3 = logger3

        level4 = level
        logger4 = logging.getLogger("DACcontrol")
        logger4.setLevel(level3)
        ch4 = logging.StreamHandler()
        ch4.setLevel(level)
        #create formatter
        if filename == None:
            formatter = logging.Formatter("DACcontrol : %(levelname)s  %(message)s")
        else:
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        #add formatter to ch
        ch4.setFormatter(formatter)
        #add ch to logger
        #create console handler and set level to debug
        logger4.addHandler(ch4)
        self.logger4 = logger4
# logging.py ends here
