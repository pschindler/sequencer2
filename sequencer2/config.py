#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "11-Jän-2010 21:59:47 viellieb"

#  file       config.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net

from sequencer2.outputsystem import TTLChannel
from optparse import OptionParser
import ConfigParser
import logging
import re

LOG_DICT = {"DEBUG" : logging.DEBUG,
            "INFO" : logging.INFO,
            "WARNING" : logging.WARNING,
            "ERROR" : logging.ERROR            
    }

class Config:
    """Simple wrapper class for the Config Parser module
    """
    def __init__(self, filename=["config/sequencer2.ini", "config/user_sequencer2.ini"]):
        self.config = ConfigParser.ConfigParser()
        self.config.read(filename)
        self.item_dict = {}
        self.logger = logging.getLogger("server")
        self.rf_setup_file = "config/rf_setup.py"
        self.nonet = None

    def parse_cmd_line(self):
        """Parses the command line arguments
        --nonet: switches off box communication; overrides setting in config file
        --force-net: switches on box communication; overrides setting in config file"""
        parser = OptionParser()
        parser.add_option("--nonet", dest="nonet", action="store_true", default=None\
                              ,help="Forces the TCP connection to be inactive")
        parser.add_option("--force-net", dest="forcenet", action="store_true",\
                              help="Forces the TCP connection to be active")
        parser.add_option("--save", dest="savebin", action="store_true",\
                              help="saves the binary output to the file sequencer2.bin")

        (options, args) = parser.parse_args()

        if options.nonet:
            self.nonet = True
        if options.forcenet:
            self.nonet = False

        if options.savebin:
            self.savebin = True
        else:
            self.savebin = False

    def is_nonet(self):
        self.parse_cmd_line()
        if self.nonet == None:
            return self.get_bool("SERVER","nonet")
        else:
            return self.nonet

    def is_savebin(self):
        self.parse_cmd_line()
        return self.savebin

    def get_str(self, section, option):
        """returns a string from option
        """
        return str(self.config.get(section, option))

    def get_log_level(self, option):
        """returns the log level from option
        uses only the section LOGGING
        """
        section = "LOGGING"
        lvl_str = str(self.config.get(section, option))
        return LOG_DICT[lvl_str]
    
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

    def get_float_dict_val(self, key):
        "Returns a value frrom the dictionary defined in get_all_dict"
        try:
            val = float(self.item_dict[key])
        except KeyError:
            self.logger.info("Cannot find duration information for key: "+str(key))
            val = 1
        return val


    def get_bool(self,section, option):
        """returns a bool from option
        """
        return self.config.getboolean(section, option)

    def get_rf_settings(self, key):
        "Returns [offset, multiplier]"
        try:
            f1= open(self.rf_setup_file)
            exec(f1)
            f1.close()
            return [offset[key], multiplier[key]]
        except:
            raise RuntimeError("Error while setting RF mode to: "+str(key))

    def get_digital_channels(self, filename):
        """ Extracts the channel names and numbers from the configuration
        file written by QFP"""
        try:
            file = open(filename, 'r')
        except IOError:
            self.logger.error("error while opening hardware settings file:" \
                                  + str(filename) )
            raise RuntimeError("error while opening hardware settings file:" \
                                  + str(filename) )

        dictionary = {}
        is_device = False
        content = file.read()
        array = content.split("\n")

        for i in range(len(array)):

            if self.get_str('OTHER','how_to_parse_hardware_settings')=='qfp_new':

                is_PB_device = array[i].find('.dev name=PB')
                is_invPB_device = array[i].find('.dev name=!PB')
                is_inverted = False
                if (is_invPB_device != -1):
                    is_inverted = True
                if (is_PB_device != -1) or (is_invPB_device!=-1):
                    split_ch_name = array[i-2].split(".")
                    split_ch_name = split_ch_name[1].split("=")
                    ch_name       = split_ch_name[1]
                    # check for quotation marks in the channel name
                    m = re.search('"?([^"]*)"?',ch_name)
                    ch_name=m.group(1)


                    split_ch_number = array[i+2].split(".")
                    split_ch_number = split_ch_number[1].split("=")
                    ch_number       = split_ch_number[1]
                
                    try:
                        if int(ch_number) <= 16:
                            select = 2
                        else:
                            select = 3
                        dictionary[ch_name] = TTLChannel(ch_name, int(ch_number) % 16, select, is_inverted)
                        self.logger.debug(str(dictionary[ch_name]))
 
                    except:
                        self.logger.warn("got a non int channel number"+split2[1])

            if self.get_str('OTHER','how_to_parse_hardware_settings')=='qfp_old':
                is_PB_device = array[i].find('.Device=PB')
                is_invPB_device = array[i].find('.Device=!PB')
                is_inverted = False
                if (is_invPB_device != -1):
                    is_inverted = True
                if (is_PB_device != -1) or (is_invPB_device!=-1):
                    to_test = [array[i-1], array[i+1]]
                    split1 = array[i].split(".")
                    ch_name = split1[0]
                    for item in to_test:
                        split2 = item.split(".")
                        if split2[0] == ch_name:
                            split3 = split2[1].split("=")
                            try:
                                if int(split3[1]) < 16:
                                    select = 2
                                else:
                                    select = 3
                                dictionary[split1[0]] = TTLChannel(split1[0], \
                                                                   int(split3[1]) % 16, select, is_inverted)
                                self.logger.debug(str(dictionary[split1[0]]))

                            except SyntaxError:
                                self.logger.warn("got a non int channel number"\
                                                     +split2[1])

        return dictionary


    def recalibration(self, x):
        """ calibration fot the DAC"""
        max_dac_value = 14000
        min_dac_value = 100
        if x > 0:
            self.logger.warn("Got a DAC amplitude bigger than 0dB: "+str(x))
            x = 0
        value = int((x + 50) * max_dac_value / 50.0)
        if value < min_dac_value:
            value = min_dac_value
        return value



# config.py ends here
