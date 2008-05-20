#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-05-20 14:51:54 c704271"

#  file       user_function.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net

import logging
from math import *

from  sequencer2 import sequencer
from  sequencer2 import api
from  sequencer2 import instructions
from  sequencer2 import outputsystem
from  sequencer2 import comm
from  sequencer2 import config

import sequence_parser
from sequence_handler import SequenceHandler
#Yes we need that cruel import
from instruction_handler import *


"""
In this file the functions which are available are defined.
Additionally external include files may be used
"""


def test_global(string1):
    global return_str
    print string1
    return_str += string1

def ttl_pulse(device_key, duration, start_time=0.0, is_last=True):
    global sequence_var
    pulse1 = TTL_Pulse(start_time, duration, device_key, is_last)
    sequence_var.append(pulse1.sequence_var)


class userAPI(SequenceHandler):
    """This class is instanciated and used by main_program.py"""
    def __init__(self, chandler):
        self.chandler = chandler
        self.sequencer=sequencer.sequencer()
        self.api = api.api(self.sequencer)
        self.config = config.Config()
        self.logger = logging.getLogger("server")
        self.seq_directory = self.config.get_str("SERVER","sequence_dir")
        global return_str
        return_str = ""

    def init_sequence(self, initial_ttl=0x0):
        "generate triggers, frequency initialization and loop targets"
        self.api.ttl_value = initial_ttl
        # Missing: triggering, frequency initialization
        # What to do with the includes

    def generate_sequence(self):
        "generates the sequence from the command string"
        # Missing the includes
        #Load sequence file
        self.pulse_program_name = self.chandler.pulse_program_name
        filename = self.seq_directory + self.pulse_program_name
        try:
            fobj = open(filename)
            sequence_string = fobj.read()
            fobj.close()
        except:
            raise RuntimeError("Error while loading sequence:" +str(filename))
        #Parse sequence
        seq_str = sequence_parser.parse_sequence(sequence_string)
        self.logger.debug(seq_str)
        # Generate dictionary for sorting the files
        global sequence_var
        sequence_var = []
        #Execute sequence
        exec(seq_str)
        self.get_sequence_array(sequence_var)
        return return_str


    def end_sequence(self):
        "adds triggers and loop events"
        #Missing everything
        return None

    def compile_sequence(self):
        "Generates the bytecode for the sequence"
        self.sequencer.compile_sequence()

    def send_sequence(self):
        "send the sequence to the Box"
        #Missing: everything
        return None

# user_function.py ends here
