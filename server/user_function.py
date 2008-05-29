#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-05-29 12:39:16 c704271"

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

##################################################################################################
# HIGH LEVEL STUFF ------- DO NOT EDIT ---- USE INCLUDES INSTEAD
##################################################################################################


def test_global(string1):
    "Just testing ..."
    global return_str
#    print string1
    return_str += string1

def ttl_pulse(device_key, duration, start_time=0.0, is_last=True):
    """generates a sequential ttl pulse"""
    global sequence_var
    pulse1 = TTL_Pulse(start_time, duration, device_key, is_last)
    sequence_var.append(pulse1.sequence_var)

def rf_pulse(theta, phi, ion, transition_name, start_time=0.0, is_last=True, address=0):
    "Generates a RF pulse"
    global sequence_var
    global transitions
    if str(transition_name) == transition_name:
        transition_obj = transitions[transition_name]
    else:
        transition_obj = transition_name
    rf_pulse = RF_Pulse(start_time, theta, phi, ion, transition_obj, is_last=is_last, address=address)
    sequence_var.append(rf_pulse.sequence_var)

def generate_triggers(api, trigger_value):
    "Generates the triggers for QFP"
    # Missing: Line trigger, ttl signal for QFP
    api.label("wait_label_1")
    api.jump_trigger("wait_label_2", trigger_value)
    api.jump("wait_label_1")
    api.label("wait_label_2")
    api.label("finite_label")

##################################################################################################
# LOW LEVEL STUFF ------- DO NOT EDIT ---- YOU DON'T NEED TO
##################################################################################################

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

    def generate_sequence(self):
        """Generates the sequence from the command string
        This method executes the include files
        Global variables for transitions and the sequence list are defined and reset.
        The sequence file is loaded and executed
        """
        # Try to execute include files
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
        global transitions
        transitions = self.chandler.transitions
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
#        self.api.
        return None


# user_function.py ends here
