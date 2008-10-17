#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-08-22 15:21:08 c704271"

#  file       output_system.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net
"""The digital output system"""
class TTLChannel:
    "Object for single bit TTL channels"
    def __init__(self, name, bit_nr, select, is_inverted=False):
        """Object for single bit TTL channels
        @param name: String identifier for the channel
        @param bit_nr: Location on the 16bit subgroup
        @param select: Subgroup of channel (normally 2 or 3)
        @param is_inverted: Boolean indicating if channel is inverted
        """
        self.name = name
        self.bit_nr = bit_nr
        self.select = select
        self.is_inverted = is_inverted

    def __str__(self):
        return "nam: "+str(self.name) + (15-len(self.name))*' ' + " bit_nr: "+ (2-len(str(self.bit_nr)))*' ' +str(self.bit_nr)+\
               " sel: "+str(self.select) + " inv: " + str(self.is_inverted)

class OutputSystem:
    """The digital output system. Handles TTL outputs
    If not ttl_dictionary is given a default TTL dictionary will be generated
    In the default dictionary the channel number will equal the identifier:
    "12" will point to channel nr 12 on select 2,
    "16" will point to channel nr 1 on select3
    @param ttl_dict: Dictionary of TTL channels.
                     The key is the channel identifier string and the
                     corresponding item is a TTLChannel object
                     { "channel_name" : TTLChannel_obj}"""


    def __init__(self, ttl_dict=None):
        "if ttl_dict=None a default dictionary will be created"
        if ttl_dict == None:
            ttl_dict = {}
            for bit_nr in range(16):
                ttl_dict[str(bit_nr)] = TTLChannel(str(bit_nr), bit_nr, 2)
                ttl_dict[str(bit_nr+16)] = TTLChannel(str(bit_nr+16), bit_nr, 3)
            ttl_dict["QFP_Trig"] = TTLChannel("QFP_Trig", 15, 2)

        self.ttl_dict = ttl_dict

    def set_bit(self, key, value, output_status):
        """Generates the output mask if a single bit is changed
        @param key: String identifier for the channel
        @param value: integer 1 or 0
        @param output_status: current status of all output subgroups
        @return: (subgroup_number of channel, new state of subgroup)"""
        try:
            channel_var = self.ttl_dict[key]
        except KeyError:
            raise RuntimeError("Can not find TTL channel " + str(key))

        if channel_var.is_inverted:
            value = abs(value - 1)
        current_state = output_status[channel_var.select]
        inverted_mask = ~(1 << channel_var.bit_nr)
        # Build new state
        new_state = (current_state & inverted_mask) | value << channel_var.bit_nr
        return (channel_var.select, new_state)


# output_system.py ends here
