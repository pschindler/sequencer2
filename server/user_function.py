#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-06-02 11:06:07 c704271"

#  file       user_function.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net

"""
user_function
=============

In this file the functions which are available are defined.

This files provides only very general functions.
Additionally external include files may be used

Basic Functions
===============

Following functions are defined in user_function and may be invoked by
include files as well as directly in the sequence:

  - ttl_pulse(device_key, duration, start_time=0.0, is_last=True)
  - rf_pulse(theta, phi, ion, transition_name, start_time=0.0, is_last=True, address=0)

Include Files:
==============

  General Usage
  -------------

  The destination of the inclued files is given in the config.ini file:

  C{include_dir = PulseSequences/includes2/}

  Each include file is executed and the defined functions are available in the
  sequence files. An example file is PulseSequences/includes2/test.py

  >>> def test_include(test_string):
  >>>     print test_string
  >>>     ttl_pulse("15",300, is_last=True)

  This generates a 300 us TTL pulse on channel "15" with following command in
  the sequence file:

  >>> test_include("something")

  Return Values
  -------------

  The return value for QFP may be set by the global vbariable return str.
  It is set as follows:

  >>> def test_include(test_string):
  >>>     global return_str
  >>>     return_str += test_string
  >>>     ttl_pulse("15",300, is_last=True)


"""

import logging
from math import *

from  sequencer2 import sequencer
from  sequencer2 import api
from  sequencer2 import ad9910
from  sequencer2 import instructions
from  sequencer2 import outputsystem
from  sequencer2 import config

import sequence_parser
from sequence_handler import SequenceHandler
from include_handler import IncludeHandler

#Yes we need that cruel import ;-)
from instruction_handler import *

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
        try:
            transition_obj = transitions[transition_name]
        except:
            raise RuntimeError("Transition name not found: "+str(transition_name))

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
    def __init__(self, chandler, dds_count=1):
        # The command handler
        self.chandler = chandler
        # The sequencer and the API
        self.sequencer=sequencer.sequencer()
        self.api = api.api(self.sequencer)
        # Load the configuration
        self.config = config.Config()
        self.logger = logging.getLogger("server")
        self.seq_directory = self.config.get_str("SERVER","sequence_dir")
        self.is_nonet = self.config.get_bool("SERVER","nonet")
        # Instnciate the IncludeHandler
        include_dir = self.config.get_str("SERVER","include_dir")
        self.include_handler = IncludeHandler(include_dir)
        # The Return string
        global return_str
        return_str = ""
        # Configure the DDS devices
        self.api.dds_list=[]
        ref_freq = self.config.get_float("SERVER","reference_frequency")
        for dds_addr in range(dds_count):
            self.api.dds_list.append(ad9910.AD9910(dds_addr, ref_freq))


    def init_sequence(self, initial_ttl=0x0):
        "generate triggers, frequency initialization and loop targets"
        generate_triggers(self.api, 0x1)
        self.api.dds_profile_list = self.generate_frequency(self.api, self.chandler.transitions, self.api.dds_list)
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
        return None


# user_function.py ends here
