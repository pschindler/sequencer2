#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-05-30 13:06:14 c704271"

#  file       sequence_handler.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net
from  sequencer2 import comm

"Base class for the user_api main object"

class SequenceHandler:
    "Base class for the user api"

    def get_sequence_array(self, seq_array):
        "Sorts the sequence array and sets the real start times"
        final_array = []
        is_last_array = []
        current_time = 0.0
        max_time = 0.0
        # loop over all insn arrays
        for insn_array in seq_array:
            insn_array.reverse()
            # Pop out the insns until the array is finished or an is_last is given
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
                        is_last_array.sort(self.sort_method)
                        final_array += is_last_array
                        is_last_array = []
                        max_time = 0
                        break
            except IndexError:
                None
        final_array += is_last_array
        if self.logger.level < 11:
            log_str  = ""
            for i in final_array:
                log_str += str(i) + "\n"
            self.logger.debug(log_str)
        return final_array

    def send_sequence(self):
        "send the sequence to the Box"
        #Missing: everything
        ptp1 = comm.PTPComm(nonet=self.is_nonet)
        ptp1.send_code(self.sequencer.word_list)

    def generate_frequency(self, api, transition_list, dds_list):
        "Generates the frequency events"
        # Missing: DDS ADDRESSES
        #raise RuntimeError("DDS instance not implemented yet")
        index = 0
        dds_profile_list = {}
        for name, trans in transition_list.iteritems():
            frequency = trans.frequency
            for dds_instance in  dds_list:
                api.set_dds_freq(dds_instance, frequency, index)
            api.load_phase(dds_instance, index)
            dds_profile_list[name] = index
            index += 1
            if index > 7:
                raise RuntimeError("Cannot handle more than 7 transitions")
        return dds_profile_list




    ####################################################################################
    # General Helper functions
    #####################################################################################

    def set_variable(self, var_type, var_name, default_val, min_val=None, max_val=None):
        "sets a variable from a command string"
        try:
            var_val = self.chandler.variables[var_name]
            cmd_str = str(var_name) + " = " + str(var_val)
            exec cmd_str
        except KeyError:
            self.logger.warn("Variable not found in comand string: "+str(var_name))

    def sort_method(self, insn1, insn2):
        "helper method for sorting the time arrays"
        if insn1.start_time > insn2.start_time:
            return 1
        if insn1.start_time == insn2.start_time:
            return 0
        if insn1.start_time < insn2.start_time:
            return -1

# The transition main class
class transition:
    '''class for characterizing an atomic transition'''
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
