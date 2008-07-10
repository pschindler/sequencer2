#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-07-10 13:43:39 c704271"

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
# DO NOT remove the line below - This is needed by the ipython debugger
#--1
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
        transitions.make_current(transition_param)
        transition_obj = transitions

    else:
        transition_obj = transition_param
    rf_pulse_insn = RFPulse(start_time, theta, phi, ion, transition_obj, \
                            is_last=is_last, address=address)

    sequence_var.append(rf_pulse_insn.sequence_var)

def rf_bichro_pulse(theta, phi, ion, transition_param, transition2_param, \
                    start_time=0.0, is_last=True, address=0, address2=1):
    """Generates a bichromatic RF pulse
    The second frequency has to be given as a separate transition object.
    The shape is controlled by the 1st transition.
    The transition_params must be a string !!!
    No direct transition variables allowed !!!
    """
    global sequence_var
    if str(transition_param) == transition_param:
        transitions.make_current(transition_param, transition2_param)
        transition_obj = transitions

    else:
        raise RuntimeError("Bichro Pulse does not support direct transitions")
    rf_bichro_pulse_insn = RFBichroPulse(start_time, theta, phi, ion, transition_obj, \
                                         is_last=is_last, address=address, address2=address2)

    sequence_var.append(rf_bichro_pulse_insn.sequence_var)
#################################################################
# Initialization and ending of the sequence
################################################################

def generate_triggers(my_api, trigger_value, ttl_trigger_channel, \
                          line_trigger_channel=None, loop_count=1):
    "Generates the triggers for QFP - No line trigger supported YET"
    # Missing: Edge detection ??
    my_api.ttl_set_bit(ttl_trigger_channel, 1)
    my_api.label("wait_label_1")
    my_api.jump_trigger("wait_label_2", trigger_value)
    my_api.jump("wait_label_1")
    my_api.label("wait_label_2")
    my_api.ttl_set_bit(ttl_trigger_channel, 0)
    my_api.start_finite("finite_label", loop_count)

    if line_trigger_channel != None:
        line_trig_val = trigger_value | line_trigger_channel
        my_api.label("line_wait_label_1")
        # We branch without taking care of the QFP Trigger value
        my_api.jump_trigger("line_wait_label_2", line_trig_val)
        my_api.jump_trigger("line_wait_label_2", line_trigger_channel)
        my_api.jump("line_wait_label_1")
        my_api.label("line_wait_label_2")

def end_of_sequence(my_api, ttl_trigger_channel):
    """Sets ttl_trigger channel to high at the end of the sequence"""
    my_api.end_finite("finite_label")
    my_api.ttl_set_bit(ttl_trigger_channel, 1)

# DO NOT remove the line below - This is needed by the ipython debugger
#--1
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
        self.api = api.api(self.sequencer, ttl_dict)
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
        self.busy_ttl_channel = self.config.get_str("SERVER","busy_ttl_channel")
        self.qfp_trigger_value = self.config.get_int("SERVER","qfp_trigger_value")
        self.line_trigger_value = self.config.get_int("SERVER","line_trigger_value")

        self.sequence_parser = sequence_parser.parse_sequence

    def clear(self):
        self.sequencer.clear()
        self.api.clear()
        self.final_array = []

    def init_sequence(self, initial_ttl=0x0):
        "generate triggers, frequency initialization and loop targets"
        if initial_ttl != 0:
            raise RuntimeError("Initial TTL not supported YET")
        if self.chandler.is_triggered:
            line_trigger_val = self.line_trigger_value
        else:
            line_trigger_val = None
        generate_triggers(self.api, 0x1, self.busy_ttl_channel, \
                              line_trigger_val,  self.chandler.cycles)
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
        seq_str = self.sequence_parser(sequence_string)
        self.logger.debug(seq_str)
        # Generate dictionary for sorting the files
        global sequence_var
        sequence_var = []
        global transitions
        transitions.clear()
        transitions = self.chandler.transitions
        #Execute sequence
        exec(seq_str)
        if sequence_var == []:
            raise RuntimeError("Cannot generate an empty sequence")
        # Here all the magic of sequence creation is done
        # see sequence_handler.py for details
        assert len(sequence_var) > 0, "Empty sequence"
        self.final_array = self.get_sequence_array(sequence_var)
        return return_str

    def compile_sequence(self):
        "Generates the bytecode for the sequence"
        self.init_sequence()
        last_stop_time = 0.0
        for instruction in self.final_array:
            wait_time = instruction.start_time - last_stop_time
            if wait_time > 0:
                self.api.wait(wait_time)
            instruction.handle_instruction(self.api)
            last_stop_time = instruction.start_time + instruction.duration
        end_of_sequence(self.api, self.busy_ttl_channel)

        self.sequencer.compile_sequence()
        if self.logger.level < 9:
            self.sequencer.debug_sequence()

    def end_sequence(self):
        "adds triggers and loop events"
        #Missing everything
        pass
# user_function.py ends here
