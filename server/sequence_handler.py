#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-07-08 10:38:38 c704271"

#  file       sequence_handler.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net
# pylint: disable-msg=W0122, F0401
"""
This module contains helper functions

Overview
========

  TransitionListObject
  --------------------

  Enhanced dict with support for an index list containing the used transitions

  SequenceDict
  ------------

  Enhanced dict with a method for adding events and included conflict resolving

  SequenceHandler
  ---------------

  The base class for the userAPI.
  The sequence generation and conflict handling is done here

  transition
  ----------

  The transition object. At the moment this is just copied
  from the old server. This class definition may change.
"""
from  sequencer2 import comm

def sort_method(insn1, insn2):
    "helper function for sorting the time arrays"
    if insn1.start_time > insn2.start_time:
        return 1
    if insn1.start_time == insn2.start_time:
        return 0
    if insn1.start_time < insn2.start_time:
        return -1


class TransitionListObject(dict):
    """An enhanced Transition dictionary class with support for the DDS
    additionaly to the standard dictionary it features a dictionary dds_list
    in this dictionary the registers in the dds are stored"""
    index_list = []
    current_transition = "NULL"
    transition2_name = None
    max_transition = 7

    def __init__(self):
        """empty the index list"""
        dict.__init__({})
        self.index_list = []
        self.transition2_name = None

    def make_current(self, transition_name, transition2_name=None):
        "set current transition and add it to the index_list"
        trans_list = [transition_name]
        if transition2_name != None:
            trans_list.append(transition2_name)
            self.transition2_name = transition2_name
        else:
            self.transition2_name = None
        for item_name in trans_list:
            if self.index_list.count(item_name) == 0:
                self.index_list.append(item_name)
        self.current_transition = transition_name
        if len(self.index_list) > self.max_transition:
            raise RuntimeError("Cannot handle more than 7 transitions in one sequence")

    def __str__(self):
        my_str = "items:"
        for name, item in self.iteritems():
            my_str += str(name) + ", "
        my_str += " || index: "
        for item in self.index_list:
            my_str += " : " + str(item) + ", "
        my_str += " || curr: " + str(self.current_transition)
        return my_str


class SequenceDict(dict):
    """An enhanced dictionary with methods for adding events
    and resolving some conflicts"""
    logger = None
    def add_event(self, event):
        "Adds an event to the sequence dictionary"
        # Missing: rounding of start time
        my_key = event.start_time
        if self.has_key(my_key):
            self.resolve_conflict(event)
        else:
            self[my_key] = [event]

    def resolve_conflict(self, event):
        "Resolve conflicts immediate"
        my_key = event.start_time
        conflict_array = self[my_key]
        for conf_item2 in conflict_array:
            is_merged = event.resolve_conflict(conf_item2)
            if is_merged:
                if self.logger != None:
                    self.logger.debug("Combining: "+str(event) \
                                      +str(conf_item2))
                conflict_array.remove(conf_item2)
                break #Only merge once
            else:
                if self.logger != None:
                    self.logger.debug("cannot combine: "+str(event.name)\
                                      + " "  +str(conf_item2.name))
        conflict_array.append(event)


class SequenceHandler(object):
    "Base class for the user api"
    logger = None
    is_nonet = None
    chandler = None

    def __init__(self):
        "We're an abstract class and shouldn't be instanciated"
        raise NotImplementedError

    def get_sequence_array(self, seq_array):
        "Sorts the sequence array and sets the real start times"
        final_dict = SequenceDict()
        final_dict.logger = self.logger
        final_array = []
        log_str = ""
        current_time = 0.0
        max_time = 0.0
        # loop over all insn arrays
        for insn_array in seq_array:
            insn_array.reverse()
            # Pop out the insns until the array is finished
            # or an is_last is given
            try:
                while True:
                    last_insn = insn_array.pop()
                    #Set max time per is_last
                    if last_insn.start_time + last_insn.duration > max_time:
                        max_time = last_insn.start_time + last_insn.duration
                    # Increase start time of instruction
                    last_insn.start_time += current_time
                    final_dict.add_event(last_insn)
                    if last_insn.is_last:
                        current_time += max_time
                        # Sort the array on the instruction start time
                        max_time = 0
                        break

            except IndexError:
                None

        dict_list = final_dict.items()
        dict_list.sort()
        for key, event_list in dict_list:
            for event in event_list:
                final_array.append(event)
                if self.logger.level < 11 :
                    log_str += str(event) + "\n"
        self.logger.debug(log_str)

        return final_array


    def send_sequence(self):
        "send the sequence to the Box"
        #Missing: everything
        ptp1 = comm.PTPComm(nonet=self.is_nonet)
        ptp1.send_code(self.sequencer.word_list)

    def generate_frequency(self, api, dds_list):
        "Generates the frequency events"
        # Make sure that the NULL transition is on index 0
        # Missing
        assert dds_list != [], "Cannot create frequencies without any configured dds"
        self.chandler.transitions.index_list.append("NULL")
        dds_profile_list = {}
        index = 0
        for index_name in self.chandler.transitions.index_list:
            trans_name = self.chandler.transitions.index_list[index]
            trans_obj = self.chandler.transitions[trans_name]
            frequency = trans_obj.frequency

            for dds_instance in  dds_list:
                api.set_dds_freq(dds_instance, frequency, index)
            api.load_phase(dds_instance, index)
            dds_profile_list[trans_name] = index
            debug_str = "Transition: " +  str(trans_name) + " | freq: "  \
                +  str(frequency) + " | index: "+ str(index)
            self.logger.debug(debug_str)
            index += 1

        return dds_profile_list




    ########################################################################
    # General Helper functions
    ########################################################################

    def set_variable(self, var_type, var_name, default_val, \
                         min_val=None, max_val=None):
        "sets a variable from a command string"
        try:
            var_val = self.chandler.variables[var_name]
            cmd_str = "var_obj = " + str(var_val)
            exec cmd_str
        except:
            # We return the default_val if an unknown variable was asked for.
            self.logger.warn("Variable not found in comand string: " \
                             +str(var_name))
            var_obj = default_val
        return var_obj

# The transition main class
class transition:
    '''class for characterizing an atomic transition
    This definition may change'''
    def __init__(self, transition_name, t_rabi,
                 frequency, sweeprange=0, amplitude=0, slope_type="None",
                 slope_duration=0, ion_list=None, amplitude2=-1, frequency2=0,
                 port=0, multiplier=.5, offset=0):

        # The rabi frequency is unique for each ion !!!!
#        configuration=innsbruck.configuration
        self.name = str(transition_name)
#        if ion_list == None:
#            ion_list=configuration.ion_list
        self.ion_list = ion_list
        self.t_rabi = t_rabi
        self.frequency = frequency
        self.sweeprange = sweeprange
        self.amplitude = float(amplitude)
        self.slope_type = slope_type
        self.slope_duration = slope_duration
        self.amplitude2 = amplitude2
        self.frequency2 = frequency2
        self.offset = offset
        self.multiplier = multiplier
        self.freq_is_init = False
        self.port = port

# sequence_handler.py ends here
