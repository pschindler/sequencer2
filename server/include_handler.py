#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-05-21 13:56:26 c704271"

#  file       include_handler.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net

import os
import logging

class IncludeHandler:
    "Some basic methods for handling include files"
    def __init__(self, include_dir):
        self.include_dir = include_dir
        self.logger = logging.getLogger("server")

    def generate_include_list(self):
        "Returns a list containing of the command strings"
        cmd_list = []
        file_list = self.generate_file_list()
        for file_name in file_list:
            incl_tuple = (file_name, self.get_cmd_str(file_name))
            cmd_list.append(incl_tuple)
        return cmd_list

    def generate_file_list(self):
        "Returns a list of the include files"
        file_list = []
        for f in os.listdir(self.include_dir):
            module_name, ext = os.path.splitext(f) # Handles no-extension files, etc.
            self.logger.debug("Including module: "+str(module_name))
            if ((ext == '.py') and (module_name != "__init__")): # Important, ignore .pyc/other files.
                file_list.append(self.include_dir+module_name+ext)
        return file_list

    def get_cmd_str(self, file_name):
        "returns the include command as a string"
        try:
            file1 = open(file_name)
            cmd_str = file1.read()
            file1.close()
            return cmd_str
        except:
            self.logger.exception("Error cannot read include file: "+str(file_name))






# include_handler.py ends here
