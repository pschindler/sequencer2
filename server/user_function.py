#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2009-07-20 08:56:16 c704271"

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

  The return value for QFP may be set by the function add_to_return_list().
  It is set as follows:

  >>> def test_include(test_string):
  >>>     add_to_return_list("test",er)
  >>>     ttl_pulse("15",300, is_last=True)

  The variables may be read with the function get_return_var(name)


"""

import logging
#from math import *
import math

from  sequencer2 import sequencer
from  sequencer2 import api
from  sequencer2 import ad9910
from  sequencer2 import config

import sequence_parser
from sequence_handler import SequenceHandler, TransitionListObject, do_discover_box
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
#return_str = ""
sequence_var = []
return_list = {}
transitions = TransitionListObject()
logger = logging.getLogger("server")

def test_global(test_string="test"):
    """Helper function needed for unittests"""
    add_to_return_list("test", test_string)

class multiple_pulses:
    """generates an instruction that is repeated 'no_of_pulses' times
    @param no_of_pulses: number of repetition
    usage: for i in multiple_pulse(5):
                ttl_pulse(...)
                rf_pulse(...)
                ttl_pulse(...)

    the maximum number of loop cycles is 255**15 ... 1mus ttl pulses this corresponds to 7e26 years pulse time ... should be enough :-)

    development note:
            the class is initialized and then the next() method is called. After that the code in the loop is executed and the next next() method called.
    """
    def __init__(self, no_of_pulses):

        global automatic_label_list
        self.max_no_of_cycles = 255
        self.no_of_pulses = no_of_pulses

        self.loop_list_counts = self.base10toN(self.no_of_pulses, self.max_no_of_cycles)

        self.last_counter = len(self.loop_list_counts) - 1
        self.new_counter  = self.last_counter

    def base10toN(self, num, n):
        """Change a  to a base-n number.
        Gives out a list with the number in the new system
        e.g. 255**3+10 = [10, 0, 0, 1] = 10*255^0 + 1*255^3
        """
        converted_number = []
        current = num
        while current != 0:
            remainder = current % n
            converted_number.append(remainder)
            current = current / n
        return converted_number

    def open_full_loops(self, cnt):
        for k in range(cnt):
           self.loop_start_finite(self.max_no_of_cycles)
        if self.loop_list_counts[cnt]>1:
           self.loop_start_finite(self.loop_list_counts[cnt])

    def close_full_loops(self, cnt):
        if self.loop_list_counts[cnt]>1:
            self.loop_end_finite()
        for k in range(cnt):
            self.loop_end_finite()

    def find_next_counter(self):
        # searches for the next non-zero value in loop_list_counts
        self.new_counter = self.last_counter - 1
        while (self.loop_list_counts[self.new_counter]==0 and self.new_counter>0):
            self.new_counter = self.new_counter - 1

    def __iter__(self):
        return self

    def next(self):
        if self.new_counter > 0:
            # close last loops if not in first loop
            if self.new_counter < len(self.loop_list_counts) - 1:
                self.close_full_loops(self.last_counter)

            self.open_full_loops(self.new_counter)
            self.last_counter = self.new_counter
            self.find_next_counter()

        else:
            if self.new_counter==0:
                if len(self.loop_list_counts)>1:
                    self.close_full_loops(self.last_counter)
                if self.loop_list_counts[0]>0:
                    self.open_full_loops(0)
                else:
                    raise StopIteration()
                self.new_counter = -1
            else:
                self.close_full_loops(0)
                raise StopIteration()

        return 0

    def loop_start_finite(self, loop_counts):
        global sequence_var
        start_fin = Start_Finite('', loop_counts, automatic_label=True)
        sequence_var.append(start_fin.sequence_var)

    def loop_end_finite(self):
        global sequence_var
        end_fin = End_Finite('', automatic_label=True)
        sequence_var.append(end_fin.sequence_var)


def dds_freq_sweep(dds_address, transition_param, time_array,
                   slope_array, dfreq_pos, dfreq_neg, lower_limit,
                   upper_limit, dt_pos=0, dt_neg=0, phi=0, loop_counts=0, is_last=True):
    """Adds a frequency sweep from frequency upper limit to frequency lower limit"""
    global sequence_var
    global transitions

    if str(transition_param) == transition_param:
        transitions.make_current(transition_param)
        transition_obj = transitions
    else:
        transitions.add_transition(transition_param)
        transitions.make_current(transition_param.name)
        transition_obj = transitions
    ramp_init = DDSSweep('freq', time_array, slope_array, dds_address,
                         transitions, phi, dfreq_pos, dfreq_neg, lower_limit,
                         upper_limit, dt_pos, dt_neg, loop_counts, is_last)
    sequence_var.append(ramp_init.sequence_var)

def dds_ampl_sweep(dds_address, transition_param, time_array, slope_array,
                   dfreq_pos, dfreq_neg, lower_limit, upper_limit, dt_pos=0,
                   dt_neg=0, phi=0, loop_counts=0, is_last=True):
    """Adds an amplitude sweep from amplitude upper_limit to lower_limit"""

    global sequence_var
    global transitions

    if str(transition_param) == transition_param:
        transitions.make_current(transition_param)
        transition_obj = transitions
    else:
        transitions.add_transition(transition_param)
        transitions.make_current(transition_param.name)
        transition_obj = transitions
    ramp_init = DDSSweep('ampl', time_array, slope_array, dds_address,
                         transitions, phi, dfreq_pos, dfreq_neg, lower_limit,
                         upper_limit, dt_pos, dt_neg, loop_counts, is_last)
    sequence_var.append(ramp_init.sequence_var)

def dds_phase_sweep(dds_address, transition_param, time_array, slope_array,
                    dfreq_pos, dfreq_neg, lower_limit, upper_limit, dt_pos=0,
                    dt_neg=0, phi=0,  loop_counts=0, is_last=True):
    """Adds phase sweep from amplitude upper_limit to lower_limit"""
    global sequence_var
    global transitions

    if str(transition_param) == transition_param:
        transitions.make_current(transition_param)
        transition_obj = transitions
    else:
        transitions.add_transition(transition_param)
        transitions.make_current(transition_param.name)
        transition_obj = transitions
    ramp_init = DDSSweep('phase', time_array, slope_array, dds_address, transitions,
                         phi, dfreq_pos, dfreq_neg, lower_limit, upper_limit, dt_pos,
                         dt_neg, loop_counts, is_last)
    sequence_var.append(ramp_init.sequence_var)


def ttl_pulse(device_key, duration, start_time=0.0, is_last=True):
    """generates a sequential ttl pulse
    device_key may be a string or a list of strings indicating
    the used TTL channels

    @param device_key: string identifier of TTL channels or a list of string identifiers
    @param duration: duration of the TTL pulse
    @param start_time: pulse start time with respect to the current frame
    @param is_last: If True a new frame is generated after this event
    """

    global sequence_var
    pulse1 = TTLPulse(start_time, duration, device_key, is_last)
    sequence_var.append(pulse1.sequence_var)

def setTTLOn(device_key, start_time=0.0, is_last=True):
    """sets TTL channel to high

    @param device_key: string identifier of TTL channels or a list of string identifiers
    @param start_time: pulse start time with respect to the current frame
    @param is_last: If True a new frame is generated after this event
    """
    setOn = TTLOn(start_time, device_key, is_last)
    sequence_var.append(setOn.sequence_var)


def setTTLOff(device_key, start_time=0.0, is_last=True):
    """sets TTL channel to low

    @param device_key: string identifier of TTL channels or a list of string identifiers
    @param start_time: pulse start time with respect to the current frame
    @param is_last: If True a new frame is generated after this event
    """
    setOff = TTLOff(start_time, device_key, is_last)
    sequence_var.append(setOff.sequence_var)


def setTTL(device_key, value, start_time=0.0, is_last=True):
    """sets TTL channel to the desired value

    @param device_key: string identifier of TTL channels or a list of string identifiers
    @param value: boolean whether or not the TTL channel should be set
    @param start_time: pulse start time with respect to the current frame
    @param is_last: If True a new frame is generated after this event
    """
    if value:
        setOn = TTLOn(start_time, device_key, is_last)
        sequence_var.append(setOn.sequence_var)
    else:
        setOff = TTLOff(start_time, device_key, is_last)
        sequence_var.append(setOff.sequence_var)

def rf_pulse(theta, phi, ion, transition_param, start_time=0.0, \
                 is_last=True, address=0):
    """Generates an RF pulse
    The transition_param may be either a string or a transition object.
    If a string is given than the according transition object is extracted
    from the data sent by QFP

    @param theta: rotation angle
    @param phi: rf_phase
    @param transition_param: string identifier for the transition or
                             a transition object
    @param start_time: pulse start time with respect to the current frame
    @param is_last: If True a new frame is generated after this event
    @param address: Integer address of the DDS
    """
    global sequence_var
    global transitions

    if str(transition_param) == transition_param:
        transitions.make_current(transition_param)
        transition_obj = transitions
    else:
        transitions.add_transition(transition_param)
        transitions.make_current(transition_param.name)
        transition_obj = transitions

    rf_pulse_insn = RFPulse(start_time, theta, phi, ion, transition_obj, \
                            is_last=is_last, address=address)

    sequence_var.append(rf_pulse_insn.sequence_var)

def rf_on(frequency, amplitude, dds_address=0, start_time = 0.0):
    """Switches on the given dds board.

    Has no start_time or is_last because it is intended to be used only in
    continous mode experiments.

    @param frequency: frequency in MHz
    @param amplitude: amplitude in dB
    @param dds_address: integer dds address
    """
    rf_on_insn = RFOn(start_time, frequency, amplitude, dds_address)
    sequence_var.append(rf_on_insn.sequence_var)

def rf_bichro_pulse(theta, phi, ion, transition_param, transition2_param, \
                    start_time=0.0, is_last=True, address=0, address2=1):
    """Generates a bichromatic RF pulse
    The second frequency has to be given as a separate transition object.
    The shape is controlled by the 1st transition.
    The transition_params must be a string !!!
    No direct transition variables allowed !!!

    @param theta: rotation angle
    @param phi: rf_phase
    @param transition_param: string identifier for the first transition
    @param transition2_param: string identifier for the second transition
    @param start_time: pulse start time with respect to the current frame
    @param is_last: If True a new frame is generated after this event
    @param address: Integer address of the first DDS
    @param address: Integer address of the second DDS
    """
    global sequence_var
    if str(transition_param) == transition_param:
        transitions.make_current(transition_param, transition2_param)
        transition_obj = transitions

    else:
        raise RuntimeError("Bichro Pulse does not support direct transitions")
    rf_bichro_pulse_insn = RFBichroPulse(start_time, theta, phi, ion, transition_obj,
                                         is_last=is_last, address=address,
                                         address2=address2)

    sequence_var.append(rf_bichro_pulse_insn.sequence_var)

def seq_wait(wait_time, start_time=0.0):
    """Generates a waiting time in the sequence
    wait_time is given in museconds
    """
    global sequence_var
    wait_insn = SeqWait(wait_time, start_time)
    sequence_var.append(wait_insn.sequence_var)

def insert_label(label_name, start_time=0.0):
    "Generates a loop target"   
    global sequence_var
    wait_insn = InsertLabel(label_name, start_time)
    sequence_var.append(wait_insn.sequence_var)

def jump_label(label_name, start_time=0.0):
    "Jumps unconditionally to a previously defined label"   
    global sequence_var
    wait_insn = JumpToLabel(label_name, start_time)
    sequence_var.append(wait_insn.sequence_var)

def jump_trigger(label_name, trigger_val, start_time=0.0):
    "Jumps to a previously defined label if trigger condition is met"   
    global sequence_var
    wait_insn = JumpOnTrigger(label_name, trigger_val, start_time)
    sequence_var.append(wait_insn.sequence_var)

################################################################
# Initialization and ending of the sequence
################################################################


def add_to_return_list(name, value):
    """Generates/updates a return variable
    @param name: string identifier
    @param value: value
    """
    global return_list
    return_list[name] = value

def get_return_var(name):
    """Returns value of the return variable with identifier name
    @param name: string identifier
    """
    global return_list
    try:
        return return_list[name]
    except KeyError:
        # Missing: Debug statement
        return None

def generate_triggers(my_api, trigger_value, ttl_trigger_channel, ttl_word, \
                          line_trigger_channel=None, loop_count=1):
    "Generates the triggers for QFP - No line trigger supported YET"
    # Missing: Edge detection ??
    # set ttl output
    # sets the ttl output channels, qfp takes care of the inversion of the ports
    # -> ttl_word is correct
    for dds_device in my_api.dds_list:
        my_api.init_dds(dds_device)
    my_api.ttl_value(ttl_word)


    my_api.label("Infinite_loop_label")
    # sets the channel that tells qfp that the box is busy
    my_api.ttl_set_bit(ttl_trigger_channel, 1)
    my_api.label("wait_label_1")
    # waits for a trigger on channel trigger_value
    my_api.jump_trigger("wait_label_2", trigger_value)
    my_api.jump("wait_label_1")
    my_api.label("wait_label_2")
    my_api.ttl_set_bit(ttl_trigger_channel, 0)
#    my_api.start_finite("test_label", 2)
    my_api.start_finite("finite_label", loop_count)

    if line_trigger_channel != None:
        line_trig_val = trigger_value | line_trigger_channel
        my_api.label("line_wait_label_1")
        # We branch without taking care of the QFP Trigger value
        my_api.jump_trigger("line_wait_label_2", 0)
        my_api.jump_trigger("line_wait_label_2", trigger_value)
        my_api.jump("line_wait_label_1")
        my_api.label("line_wait_label_2")
        # We branch without taking care of the QFP Trigger value
        my_api.jump_trigger("line_wait_label_3", line_trig_val)
        my_api.jump_trigger("line_wait_label_3", line_trigger_channel)
        my_api.jump("line_wait_label_2")
        my_api.label("line_wait_label_3")

def end_of_sequence(my_api, ttl_trigger_channel, ttl_word):
    """Sets ttl_trigger channel to high at the end of the sequence"""

#    my_api.my_bdec("aut_label_1",0)
#    my_api.my_bdec("finite_label",2)

    my_api.end_finite("finite_label")


#    my_api.instructions_bdec("aut_label_1", 2)
#    my_api.instructions_ldc(2, 2)

#    my_api.end_finite("test_label")
    my_api.ttl_set_bit(ttl_trigger_channel, 1)
    my_api.ttl_value(ttl_word)  # resets the ttl output channels
    my_api.jump("Infinite_loop_label")


#def create_transition(*args):
#    """Creates a transition object and addes it to the global transition list

#    Arguments are directly passed to the generator of the transition object.
#    Example: create_transition(transition_name, t_rabi, frequency)
#    """
#    global transitions

#    trans_obj = transition(args)
#    trans_name = trans_obj.name
#    transitions[trans_name] = trans_obj
    

def set_transition(transition_name, name_str="729"):
    """Sets the frequency modifiers of the transition
    For configuration see config/rf_setup.py

    DOES not generate a new transition"""
    global transitions
    assert type(transition_name)==str, \
        "set_transition needs string identifier for transition"
    my_config = config.Config()
    [offset, multiplier] = my_config.get_rf_settings(name_str)
    try:
        transitions[transition_name].set_freq_modifier(multiplier, offset)
        logger.debug("setting transition: "+str(transitions[transition_name]))
    except KeyError:
        raise RuntimeError("Error while setting transition" + str(transition_name))


# DO NOT remove the line below - This is needed by the ipython debugger
#--1
################################################################################
# LOW LEVEL STUFF ------- DO NOT EDIT ---- YOU DON'T NEED TO
###############################################################################

class userAPI(SequenceHandler):
    """This class is instanciated and used by main_program.py
    The base class SequenceHandler is defined in the file sequence_handler.py
    """
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
        self.is_nonet = self.config.is_nonet()
        # Instnciate the IncludeHandler
        include_dir = self.config.get_str("SERVER","include_dir")
        self.include_handler = IncludeHandler(include_dir)
        # The Return string
        global return_str
        return_str = ""
        # Configure the DDS devices
        self.api.dds_list = []
        ref_freq = self.config.get_float("SERVER","reference_frequency")
        clk_div = self.config.get_float("SERVER","clk_divider")
        for dds_addr in range(dds_count):
            self.api.dds_list.append(ad9910.AD9910(dds_addr, ref_freq, clk_div))
        # Set the parameters for the
        self.pulse_program_name = ""
        self.final_array = []
        self.busy_ttl_channel = self.config.get_str("SERVER","busy_ttl_channel")
        self.qfp_trigger_value = self.config.get_int("SERVER","qfp_trigger_value")
        self.line_trigger_value = self.config.get_int("SERVER","line_trigger_value")

        self.sequence_parser = sequence_parser.parse_sequence

    def clear(self):
        "Clear all the local and global variables"
        self.sequencer.clear()
        self.api.clear()
        self.final_array = []
        global transitions
        transitions.clear()
        global sequence_var
        sequence_var = []
        global return_list
        return_list = {}


    def init_sequence(self):
        "generate triggers, frequency initialization and loop targets"
        if self.chandler.is_triggered:
            line_trigger_val = self.line_trigger_value
        else:
            line_trigger_val = None
        generate_triggers(self.api, self.qfp_trigger_value, self.busy_ttl_channel, \
                              self.chandler.ttl_word, line_trigger_val, \
                              self.chandler.cycles)
        if self.api.dds_list != []:
            self.api.dds_profile_list = self.generate_frequency(self.api, \
                                                                self.api.dds_list)
        # Missing: triggering, frequency initialization

    def generate_sequence(self):
        """Generates the sequence from the command string
        This method executes the include files
        Global variables for transitions and the sequence list are defined and reset.
        The sequence file is loaded and executed
        """
        # define a local chandler
        local_chandler = self.chandler

        # Try to execute include files
        incl_list = self.include_handler.generate_include_list()
        for file_name, cmd_str in incl_list:
            try:
                exec(cmd_str)
            except:
                self.logger.exception("Error while executing include file: " \
                                          + str(file_name))

        # Loading the sequence file
        self.pulse_program_name = self.chandler.pulse_program_name
        filename = self.seq_directory + self.pulse_program_name
        try:
            fobj = open(filename)
            sequence_string = fobj.read()
            fobj.close()
        except:
            raise RuntimeError("Error while loading sequence:" +str(filename))
        # Parse sequence
        seq_str = self.sequence_parser(sequence_string)
        self.logger.debug("Received sequence: \n" + seq_str)
        # Generate dictionary for sorting the files
        global sequence_var
        sequence_var = []
        global transitions
        transitions.clear()
        transitions = self.chandler.transitions
        # We have to set all known DDS devices to the NULL transition!
        for dds_address in range(len(self.api.dds_list)):
            rf_pulse(1, 0, 1, "NULL",  address=dds_address)
        # Execute sequence
        exec(seq_str)
        if sequence_var == []:
            raise RuntimeError("Cannot generate an empty sequence")
        # Here all the magic of sequence creation is done
        # see sequence_handler.py for details
        assert len(sequence_var) > 0, "Empty sequence"
        self.final_array, sequence_duration = self.get_sequence_array(sequence_var)
        local_return_str = self.get_return_string(return_list)
        return local_return_str + 'sequence_duration,'+str(sequence_duration)+';'

    def compile_sequence(self):
        "Generates the bytecode for the sequence"
        self.init_sequence()
        last_stop_time = 0.0
        # loop through list of generated sequence instructions
        # and add wait events corresponding to the duration of each event
        for instruction in self.final_array:
            wait_time = instruction.start_time - last_stop_time
            if wait_time > 0:
                self.api.wait(wait_time)
            instruction.handle_instruction(self.api)
            last_stop_time = instruction.start_time + instruction.duration
        end_of_sequence(self.api, self.busy_ttl_channel, self.chandler.ttl_word)
        self.sequencer.compile_sequence()
        if self.logger.level < 9:
            self.sequencer.debug_sequence()

#        self.sequencer.debug_sequence()

    def end_sequence(self):
        "adds triggers and loop events"
        #Missing everything
        pass



def discover_box(nonet=False):
    do_discover_box(nonet)

# user_function.py ends here
