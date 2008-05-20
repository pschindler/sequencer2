#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-05-20 14:56:03 c704271"

#  file       sequence_handler.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net
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
                    if last_insn.start_time > max_time:
                        max_time = last_insn.start_time + last_insn.duration
                    # Increase start time of instruction
                    last_insn.start_time += current_time
                    is_last_array.append(last_insn)
                    if last_insn.is_last:
                        current_time = max_time
                        is_last_array.sort(self.sort_method)
                        final_array += is_last_array
                        is_last_array = []
                        max_time = 0
                        break
            except IndexError:
                None
        final_array += is_last_array
        print "FINAL"
        for i in final_array:
            print i

    def set_variable(self, var_type, var_name, var_val, min_val=None, max_val=None):
        "sets a variable from a command string"
        cmd_str = str(var_name) + " = " + str(var_val)
        exec cmd_str

    def sort_method(self, insn1, insn2):
        "helper method for sorting the time arrays"
        if insn1.start_time > insn2.start_time:
            return 1
        if insn1.start_time == insn2.start_time:
            return 0
        if insn1.start_time < insn2.start_time:
            return -1
# sequence_handler.py ends here
