#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-03-07 13:10:27 c704271"

#  file       api.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://wiki.havens.de

# Missing: subroutine handling

#from exceptions import *
import instructions
import copy

class api():
    """api.py the api commands for sequencer2
    """
    def __init__(self, sequencer):
        """A simple initialization
        The LVDS bus opcodes are defined here
        """
        self.sequencer = sequencer
        self.is_subroutine = False
        # The LVDS opcodes
        self.fifo_opcode = 0x2
        self.addr_opcode = 0x1


    def dac_value(self, dac_nr, val):
        """simple example for a DAC event
        NOT usable for the LVDS bus
        """
        #insert the chainboard address event
        addr_insn = instructions.p(dac_nr << 12, 3)
        self.sequencer.add_insn(addr_insn)
        #Set the data bus
        data_insn = instructions.p(val << 2, 0)
        self.sequencer.add_insn(data_insn)
        #Set the WRB
        data2_insn = copy.copy(data_insn)
        data2_insn.output_state = val << 2 | 2
        self.sequencer.add_insn(data2_insn)

    def ttl_value(self, value):
        """simple example for a TTL event
        NOT usable for the LVDS bus
        """
        ttl_insn = instructions.p(value, 2)
        self.sequencer.add_insn(ttl_insn)

    def label(self, label_name):
        """inserts a label and a NOP
        """
        label_insn = instructions.label(label_name)
        self.sequencer.add_insn(label_insn)

    def jump(self, target_name):
        """jumps to label
        """
        jump_insn = instructions.j(target_name)
        nop_insn = instructions.nop()
        self.sequencer.add_insn(jump_insn)
        self.sequencer.add_insn(nop_insn)
        self.sequencer.add_insn(copy.copy(nop_insn))
        self.sequencer.add_insn(copy.copy(nop_insn))

    def jump_trigger(self, target_name, trigger):
        """branch on trigger
        Adds a conditional jump
        trigger : trigger state in hex
        """
        jump_insn = instructions.btr(target_name, trigger)
        nop_insn = instructions.nop()
        self.sequencer.add_insn(jump_insn)
        self.sequencer.add_insn(nop_insn)
        self.sequencer.add_insn(copy.copy(nop_insn))
        self.sequencer.add_insn(copy.copy(nop_insn))

    def begin_subroutine(self, label_name):
        """inserts a label for a subroutine
        label_name
        """
        if self.is_subroutine:
            raise RuntimeError, "Previous subroutine not ended"
        if self.sequencer.current_sequence != []:
            raise RuntimeError, "Subroutine can only be started at beginnig of sequence"
        self.sequencer.add_insn(instructions.label(label_name))

    def end_subroutine(self):
        """ends the subroutine
        """
        self.sequencer.add_insn(instructions.ret())
        self.sequencer.sub_list.append(copy.copy(self.sequencer.current_sequence))
        self.sequencer.current_sequence = []

    def call_subroutine(self, label_name):
        """calls a subroutine
        label_name
        """
        call_insn = instructions.call(label_name)
        nop_insn = instructions.nop()
        self.sequencer.add_insn(call_insn)
        self.sequencer.add_insn(nop_insn)
        self.sequencer.add_insn(copy.copy(nop_insn))
        self.sequencer.add_insn(copy.copy(nop_insn))

    def lvds_cmd(self, opcode, address, data, control=0, wait=0):
        """Writes data to the lvds bus
        opcode : Bits 31:26
        address: Bits 24:21
        data: Bits 15:0
        control_val Bits 20:16
        """
        #High Word consists of following values:
        avail_val = 1 << 10
        opcode_val = opcode << 11
        address_val = address << 6
        control_val = control
        #The Highword Words calculated:
        high_word = opcode_val | address_val | control_val
        high_word_avail = high_word | avail_val
        #Low Word
        data_val = data % (2**16)

        # Set the low word first
        low_insn = instructions.p(data_val, 0)
        self.sequencer.add_insn(low_insn)
        # Set the hight words
        high_insn = instructions.p(high_word, 1)
        self.sequencer.add_insn(high_insn)
        high_insn_avail = instructions.p(high_word_avail, 1)
        self.sequencer.add_insn(high_insn_avail)
        # ?? Missing add wait command
        # Add a copy of high_insn
        self.sequencer.add_insn(copy.copy(high_insn))

    def dds_to_serial(self, word, length, reg_address, dds_address=0):
        """Generates LVDS commands for writing the registers of the DDS
        """
        fifo_wait = 1
        addr_wait = 20 + 30*int(length / 16)

        num_words = int(length) / 16
        # Write the FIFO with the data
        for i in range(num_words):
            value = (word >>( 16*(num_words-i-1)  ))% 2**16
            self.lvds_cmd(self.fifo_opcode, dds_address, value, wait=fifo_wait)
        # Set the register address and wait until finished
        self.lvds_cmd(self.addr_opcode, dds_address, reg_address, wait=addr_wait)

    def init_dds(self, dds_instance):
        """Writes the CFR registers of the DDS
        dds_instance : ad9910 object
        """
        for register  in dds_instance.reg_value_dict:
            val = dds_instance.reg_value_dict[register]
            self.dds_to_serial(val, register[1], register[0])



##
## api.py
## Login : <viellieb@ohm>
## Started on  Tue Jan 29 17:15:37 2008 Philipp Schindler
## $Id$
##
## Copyright (C) 2008 Philipp Schindler
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##


# api.py ends here
