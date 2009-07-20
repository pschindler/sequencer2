#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2009-07-20 12:12:55 c704271"

#  file       logging.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net
"""Generates a logging object for the python logging framework"""

import logging
import logging.handlers

class ptplog:
    """Generate a Logger with the names defined in logger_list
    """
    def __init__(self, filename=None, level=logging.WARNING, level_dict={},
                 combine_level=logging.DEBUG):

        logger_list = ["sequencer2", "api", "server", "DACcontrol"]
        for logger_name in logger_list:
            logger = logging.getLogger(logger_name)
            try:
                level1 = level_dict[logger_name]
                logger.setLevel(level1)
            except KeyError:
                logger.setLevel(level)
#            if logger_name == "":
#                logger.set_level(combine_level)

            if filename == None:
                #create console handler and set level to debug
                stream_handler = logging.StreamHandler()
                stream_handler.setLevel(level)
                #create formatter
                formatter = logging.Formatter(logger_name + ": %(levelname)s - %(message)s")
            else:
                logger_filename = filename + "_" + logger_name + ".log"
                stream_handler = logging.handlers.RotatingFileHandler(logger_filename,
                                                 maxBytes=1e6, backupCount=5)
                stream_handler.setLevel(level)
                formatter = logging.Formatter("!#%(levelname)s || %(name)s || %(asctime)s %(message)s", )
#                formatter = logging.Formatter("%(levelname)s - %(asctime)s - %(name)s - %(message)s")
            #add formatter to stream_handler
            stream_handler.setFormatter(formatter)
            #add stream_handler to logger
            logger.addHandler(stream_handler)
            self.logger = logger
            logger.info("restart")

        if filename:
           # Also init a global logger
            formatter = logging.Formatter(": %(levelname)s - %(name)s - %(message)s")
            glob_logger = logging.getLogger()
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            stream_handler.setLevel(combine_level)
            mem_stream  = logging.handlers.RotatingFileHandler(filename + "_all.log",
                                                               maxBytes=1e6, backupCount=5)
            formatter2 = logging.Formatter("!#%(levelname)s || %(name)s || %(message)s", )
            mem_stream.setFormatter(formatter2)
            memory_handler = logging.handlers.MemoryHandler(1e6, target=mem_stream)
            memory_handler.setLevel(logging.DEBUG)
            #add stream_handler to logger
            glob_logger.setLevel(combine_level)
            glob_logger.addHandler(stream_handler)
            glob_logger.addHandler(memory_handler)


# logging.py ends here
