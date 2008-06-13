#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "14-Jun-2008 00:26:01 viellieb"

#  file       output_system.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net
"""The digital output system"""
class TTLChannel:
    def __init__(self, name, bit_nr, select, is_inverted=False):
        self.name = name
        self.bit_nr = bit_nr
        self.select = select
        self.is_inverted = is_inverted

    def __str__(self):
        return "nam: "+str(self.name)+" bit_nr: "+str(self.bit_nr)+\
               " sel: "+str(self.select) + " inv: " + str(self.is_inverted)

class OutputSystem:
    """The digital output system. Handles TTL outputs"""
    def __init__(self, ttl_dict=None):
        "if ttl_dict=Nonne a defualt dictionary will be created"
        if ttl_dict == None:
            ttl_dict={}
            for bit_nr in range(16):
                ttl_dict[str(bit_nr)] = TTLChannel(str(bit_nr),bit_nr,2)
                ttl_dict[str(bit_nr+16)] = TTLChannel(str(bit_nr+16),bit_nr,3)

        self.ttl_dict = ttl_dict

    def set_bit(self, key, value, output_status):
        "sets a single bit"
        # Missing: inverted TTL channel
        channel_var = self.ttl_dict[key]
        current_state = output_status[channel_var.select]
        inverted_mask = ~(1 << channel_var.bit_nr)
        # Build new state
        new_state = (current_state & inverted_mask) | value << channel_var.bit_nr
        return (channel_var.select, new_state)

# output_system.py ends here
