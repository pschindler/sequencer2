#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-06-11 16:11:52 c704271"

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

  Nothing to say right now :-(

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
    index_list = {}
    current_transition = "NULL"

    def __str__(self):
        my_str = ""
        for name, item in self.iteritems():
            my_str += str(name) + ", "
        my_str += " || "
        for name, item in self.index_list.iteritems():
            my_str += str(name)
            my_str += " : " + str(item.name) + ", "
        my_str += " || " + str(self.current_transition)
        return my_str

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
        final_array = []
        is_last_array = []
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
                    is_last_array.append(last_insn)
                    if last_insn.is_last:
                        current_time += max_time
                        # Sort the array on the instruction start time
                        is_last_array.sort(sort_method)
                        final_array += is_last_array
                        is_last_array = []
                        max_time = 0
                        break

            except IndexError:
                None

        final_array += is_last_array
        final_array = self.handle_conflicts(final_array)
        if self.logger.level < 11 :
            log_str  = ""
            for i in final_array:
                log_str += str(i) + "\n"
            self.logger.debug(log_str)

        return final_array

    def handle_conflicts(self, final_array):
        """Let's see if we can combine some instructions
        Long story made short: This is not implemented well yet :-(
        The final array is checked for items with the same start time
        If items have the same start time they are added to the conflict_array
        This conflict_array is emptied if an item with a different start time occurs

        Maybe better data structure: use dic for conflict_array
        """
        has_conflict = False
        new_array = []
        conflict_array = []
        final_length = len(final_array) - 1
        final_array.reverse()
        next_item = final_array.pop()
        for index in range(final_length):
            this_item = next_item
            try:
                next_item = final_array.pop()
            except IndexError:
                break

            if (this_item.start_time == next_item.start_time):
                if conflict_array.count(this_item) == 0:
                    conflict_array.append(this_item)
                conflict_array.append(next_item)
            else:
                while conflict_array != []:
                    conf_item = conflict_array.pop()
                    for conf_item2 in conflict_array:
                        is_merged = conf_item.resolve_conflict(conf_item2)
                        if is_merged:
                            self.logger.debug("Combining: "+str(conf_item) \
                                                  +str(conf_item2))
                            conflict_array.remove(conf_item2)
                        else:
                            self.logger.debug("cannot combine: "+str(conf_item.name)\
                                                + " "  +str(conf_item2.name))
                    new_array.append(conf_item)
                    has_conflict = True
                if not has_conflict:
                    new_array.append(this_item)
                else:
                    has_conflict = False
        return new_array

    def send_sequence(self):
        "send the sequence to the Box"
        #Missing: everything
        ptp1 = comm.PTPComm(nonet=self.is_nonet)
        ptp1.send_code(self.sequencer.word_list)

    def generate_frequency(self, api, dds_list):
        "Generates the frequency events"
        # Make sure that the NULL transition is on index 0
        # Missing
        if dds_list == []:
            raise RuntimeError("Cannot create frequencies without any configured dds")
        index = 0
        dds_profile_list = {}
        for name, trans in self.chandler.transitions.iteritems():
            debug_str = str(name)
            frequency = trans.frequency

            if index < 7:
                for dds_instance in  dds_list:
                    self.chandler.transitions.index_list[index] = trans
                    api.set_dds_freq(dds_instance, frequency, index)
            api.load_phase(dds_instance, index)
            dds_profile_list[name] = index
            debug_str = "Transition: " +  str(name) + " | freq: "  \
                +  str(frequency) + " | index: "+ str(index)
            self.logger.debug(debug_str)
            index += 1
            if index > 7:
                raise RuntimeError("Cannot handle more than 7 transitions - YET")
        print self.chandler.transitions
        return dds_profile_list




    ########################################################################
    # General Helper functions
    ########################################################################

    def set_variable(self, var_type, var_name, default_val, \
                         min_val=None, max_val=None):
        "sets a variable from a command string"
        try:
            var_val = self.chandler.variables[var_name]
            cmd_str = str(var_name) + " = " + str(var_val)
            exec cmd_str

        except KeyError:
            # We return the default_val if an unknown variable was asked for.
            self.logger.warn("Variable not found in comand string: " \
                             +str(var_name))
            cmd_str = str(var_name) + "=" +str(default_val)
            exec cmd_str


# The transition main class
class transition:
    '''class for characterizing an atomic transition
    This definition may change'''
    def __init__(self, transition_name, t_rabi,
                 frequency, sweeprange=0, amplitude=1, slope_type="None",
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
