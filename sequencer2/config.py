#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-06-06 09:53:23 c704271"

#  file       config.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net

import ConfigParser
import logging

class Config:
    """Simple wrapper class for the Config Parser module
    """
    def __init__(self, filename="./config/sequencer2.ini"):
        self.config = ConfigParser.ConfigParser()
        self.config.read(filename)
        self.item_dict = {}
        self.logger = logging.getLogger("server")

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

    def get_all_dict(self, section):
        "returns all items of a section as a dictionary"
        self.item_dict = {}
        item_list = self.config.items(section)
        for name, value in item_list:
            self.item_dict[name] = value


    def get_int_dict_val(self, key):
        try:
            val = int(self.item_dict[key])
        except KeyError:
            self.logger.info("Cannot find duration information for key: "+str(key))
            val = 1
        return val
    def get_bool(self,section, option):
        """returns a bool from option
        """
        return self.config.getboolean(section, option)
# config.py ends here
