#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-05-30 11:24:26 c704271"

#  file       config.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net

import ConfigParser


class Config:
    """Simple wrapper class for the Config Parser module
    """
    def __init__(self, filename="./config/sequencer2.ini"):
        self.config = ConfigParser.ConfigParser()
        self.config.read(filename)

    def get_str(self,section, option):
        """returns a string from option
        """
        return str(self.config.get(section, option))

    def get_int(self,section, option):
        """returns an int from option
        """
        return self.config.getint(section, option)

    def get_float(self,section, option):
        """returns an int from option
        """
        return self.config.getfloat(section, option)

    def get_bool(self,section, option):
        """returns a bool from option
        """
        return self.config.getboolean(section, option)
# config.py ends here
