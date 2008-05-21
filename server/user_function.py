#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-05-21 14:59:13 c704271"

#  file       user_function.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net
import logging
from math import *

from  sequencer2 import sequencer
from  sequencer2 import api
from  sequencer2 import instructions
from  sequencer2 import outputsystem
from  sequencer2 import config

import sequence_parser
from sequence_handler import SequenceHandler
from include_handler import IncludeHandler

#Yes we need that cruel import ;-)
from instruction_handler import *

"""
In this file the functions which are available are defined.
Additionally external include files may be used
"""

def test_global(string1):
    global return_str
#    print string1
    return_str += string1

def ttl_pulse(device_key, duration, start_time=0.0, is_last=True):
    global sequence_var
    pulse1 = TTL_Pulse(start_time, duration, device_key, is_last)
    sequence_var.append(pulse1.sequence_var)

def generate_triggers(api, trigger_value):
    # Missing: Line trigger, ttl signal for QFP
    api.label("wait_label_1")
    api.jump_trigger("wait_label_2", trigger_value)
    api.jump("wait_label_1")
    api.label("wait_label_2")

class userAPI(SequenceHandler):
    """This class is instanciated and used by main_program.py"""
    def __init__(self, chandler):
        self.chandler = chandler
        self.sequencer=sequencer.sequencer()
        self.api = api.api(self.sequencer)
        self.config = config.Config()
        self.logger = logging.getLogger("server")
        self.seq_directory = self.config.get_str("SERVER","sequence_dir")
        self.is_nonet = self.config.get_bool("SERVER","nonet")
        include_dir = self.config.get_str("SERVER","include_dir")
        self.include_handler = IncludeHandler(include_dir)
        global return_str
        return_str = ""

    def init_sequence(self, initial_ttl=0x0):
        "generate triggers, frequency initialization and loop targets"
        generate_triggers(self.api, 0x1)
        self.generate_frequency(self.api, self.chandler.transitions)
        # Missing: triggering, frequency initialization
        # What to do with the includes

    def generate_sequence(self):
        "generates the sequence from the command string"
        #Load sequence file

        incl_list = self.include_handler.generate_include_list()
        for file_name, cmd_str in incl_list:
            try:
                exec(cmd_str)
            except:
                self.logger.exception("Error while executing include file: " \
                                          + str(file_name))

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
        self.final_array = self.get_sequence_array(sequence_var)
        return return_str

    def compile_sequence(self):
        "Generates the bytecode for the sequence"
        # Missing: conflict management
        last_stop_time = 0.0
        for instruction in self.final_array:
            wait_time = instruction.start_time - last_stop_time
            if wait_time > 0:
                self.api.wait(wait_time)
            instruction.handle_instruction(self.api)
            last_stop_time = instruction.start_time + instruction.duration

        self.sequencer.compile_sequence()
        if self.logger.level < 9:
            self.sequencer.debug_sequence()

    def end_sequence(self):
        "adds triggers and loop events"
        #Missing everything
        return None


# user_function.py ends here
