#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "14-Jun-2008 00:32:40 viellieb"

#  file       user_function.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net
# pylint: disable-msg=W0603, W0602, W0122, W0702, F0401, W0401, W0614

"""
user_function
=============

In this file the functions which are available are defined.

This files provides only very general functions.
Additionally external include files may be used

Some helper functions are in L{server.sequence_handler}

Basic Functions
===============

Following functions are defined in user_function and may be invoked by
include files as well as directly in the sequence:

  - ttl_pulse(device_key, duration, start_time=0.0, is_last=True)
  - rf_pulse(theta, phi, ion, transition_name, \
                  start_time=0.0, is_last=True, address=0)

Include Files:
==============

  General Usage
  -------------

  The destination of the inclued files is given in the config.ini file:

  C{include_dir = PulseSequences/includes2/}

  Each include file is executed and the defined functions are available in the
  sequence files. An example file is PulseSequences/includes2/test.py

  >>> def test_include(test_string):
  >>>     \"""This is just a test comment
  >>>     This funtion generates a 300us pulse on channel nr "15"
  >>>
  >>>     @param test_string: This is a meaningless test string which is
  >>>    just printed to stdout
  >>>     \"""
  >>>     print test_string
  >>>     ttl_pulse("15",300, is_last=True)

  This generates a 300 us TTL pulse on channel "15" with following command in
  the sequence file:

  >>> test_include("something")

  Documenting include files
  -------------------------

  Documentation of the functions defined in include file is best given in the
  epydoc standard.

  The syntax for the documentation can be found at:
  U{http://epydoc.sourceforge.net/manual-epytext.html}

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
from  sequencer2 import config

import sequence_parser
from sequence_handler import SequenceHandler, TransitionListObject
from include_handler import IncludeHandler

#Yes we need that cruel import ;-)
from instruction_handler import *
###############################################################################
# HIGH LEVEL STUFF ------- DO NOT EDIT ---- USE INCLUDES INSTEAD
#
# DO NOT ADD NEW FUNCTIONS HERE  ---- USE INCLUDES INSTEAD
###############################################################################
return_str = ""
sequence_var = []
transitions = TransitionListObject()

def test_global(string1):
    "Just testing ..."
    global return_str
    return_str += string1

def ttl_pulse(device_key, duration, start_time=0.0, is_last=True):
    """generates a sequential ttl pulse
    device_key may be a string or a list of strings indicating
    the used TTL channels"""
    global sequence_var
    pulse1 = TTLPulse(start_time, duration, device_key, is_last)
    sequence_var.append(pulse1.sequence_var)

def rf_pulse(theta, phi, ion, transition_param, start_time=0.0, \
                 is_last=True, address=0):
    """Generates an RF pulse
    The transition_param may be either a string or a transition object.
    If a string is given than the according transition object is extracted
    from the data sent by QFP
    """
    global sequence_var
    if str(transition_param) == transition_param:
        transitions.current_transition = transition_param
        transition_obj = transitions

    else:
        transition_obj = transition_param
    rf_pulse_insn = RFPulse(start_time, theta, phi, ion, transition_obj, \
                            is_last=is_last, address=address)

    sequence_var.append(rf_pulse_insn.sequence_var)

def generate_triggers(my_api, trigger_value):
    "Generates the triggers for QFP"
    # Missing: Line trigger, ttl signal for QFP
    my_api.label("wait_label_1")
    my_api.jump_trigger("wait_label_2", trigger_value)
    my_api.jump("wait_label_1")
    my_api.label("wait_label_2")
    my_api.label("finite_label")

################################################################################
# LOW LEVEL STUFF ------- DO NOT EDIT ---- YOU DON'T NEED TO
###############################################################################

class userAPI(SequenceHandler):
    """This class is instanciated and used by main_program.py"""
    def __init__(self, chandler, dds_count=1, ttl_dict=None):
        # The command handler
        self.chandler = chandler
        # The sequencer and the API
        self.sequencer = sequencer.sequencer()
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
        self.api.dds_list = []
        ref_freq = self.config.get_float("SERVER","reference_frequency")
        for dds_addr in range(dds_count):
            self.api.dds_list.append(ad9910.AD9910(dds_addr, ref_freq))

        self.pulse_program_name = ""
        self.final_array = []

    def init_sequence(self, initial_ttl=0x0):
        "generate triggers, frequency initialization and loop targets"
        generate_triggers(self.api, 0x1)
        self.api.dds_profile_list = self.generate_frequency(self.api, \
                                                                self.api.dds_list)
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
        # Here all the magic of sequence creation is done
        # see sequence_handler.py for details
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
