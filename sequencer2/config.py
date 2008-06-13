#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "14-Jun-2008 00:30:56 viellieb"

#  file       config.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net

from outputsystem import TTLChannel
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

    def get_str(self, section, option):
        """returns a string from option
        """
        return str(self.config.get(section, option))

    def get_int(self, section, option):
        """returns an int from option
        """
        return self.config.getint(section, option)

    def get_float(self, section, option):
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
        "Returns a value frrom the dictionary defined in get_all_dict"
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

    def get_digital_channels(self, filename):
        """ Extracts the channel names and numbers from thhe configuration
        file written by QFP"""
        try:
            file = open(filename, 'r')
        except IOError:
            self.logger.error("error while openinng hardware settings file:" \
                                  + str(filename) )
            raise RuntimeError("error while openinng hardware settings file:" \
                                  + str(filename) )

        dictionary = {}
        is_device = False
        content = file.read()
        array = content.split("\n")
        for i in range(len(array)):
            is_PB_device = array[i].find('.Device=PB')
            is_invPB_device = array[i].find('.Device=!PB')
            is_inverted = False
            if (is_invPB_device != -1):
                is_inverted = True
                raise RuntimeError("No inverted digital channels supported yet")
            if (is_PB_device != -1) or (is_invPB_device!=-1):
                to_test = [array[i-1], array[i+1]]
                split1 = array[i].split(".")
                ch_name = split1[0]
                for item in to_test:
                    split2 = item.split(".")
                    if split2[0] == ch_name:
                        split3 = split2[1].split("=")
                        try:
                            if int(split3[1]) < 15:
                                select = 2
                            else:
                                select = 3
                            dictionary[split1[0]] = TTLChannel(split1[0], \
                                                               int(split3[1]), select, is_inverted)
                            self.logger.debug(str(dictionary[split1[0]]))

                        except SyntaxError:
                            self.logger.warn("warning: got a non int channel number"\
                                                 +split2[1])

        return dictionary


# config.py ends here
