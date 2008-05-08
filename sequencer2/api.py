#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-05-08 12:50:08 c704271"

#  file       api.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://wiki.havens.de
"""API functions for the DDS / TTL / DAC /Builtin Commands
"""

#from exceptions import *
import instructions
import copy
import logging
import math

class api():
    """api.py the api commands for sequencer2
    """
    def __init__(self, sequencer):
        """A simple initialization
        The LVDS bus opcodes are defined here
        """
        self.sequencer = sequencer
        # The LVDS opcodes
        self.addr_opcode = 0x1
        self.fifo_opcode = 0x2
        self.dds_up_opcode = 0x4
        self.dac_opcode = 0x7
        self.phase_load_opcode = 0xa
        self.phase_pulse_opcode = 0xb
        self.reset_opcode = 0x1f
        # number of branch delay necessary:
        self.branch_delay_slots = 5
        self.logger = logging.getLogger("api")

    def wait(self, wait_cycles):
        """inserts a wait event
        wait_cycles : nr of clock cycles to wait
        needs calibration !!! wait has to be > 4 ?
        """
        nop_insn = instructions.nop()
        if wait_cycles > self.branch_delay_slots:
            wait_insn = instructions.wait(wait_cycles - 4)
            # Do we really need wait_cycles - 4 ??
            self.sequencer.add_insn(wait_insn)
            for i in range(self.branch_delay_slots):
                self.sequencer.add_insn(copy.copy(nop_insn))
        else:
            for i in range(wait_cycles):
                self.sequencer.add_insn(copy.copy(nop_insn))

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
        for index in range(self.branch_delay_slots):
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
        self.sequencer.add_insn(copy.copy(nop_insn))

    def begin_subroutine(self, label_name):
        """inserts a label for a subroutine
        It has to be called with an empty sequencer.current_sequence
        """
        self.sequencer.begin_subroutine()
        self.sequencer.add_insn(instructions.label(label_name))

    def end_subroutine(self):
        """ends the subroutine
        Adds the current sequence to the sequencer.sub_list
        Flushes  sequencer.current_sequence
        """
        self.sequencer.add_insn(instructions.ret())
        self.sequencer.end_subroutine()

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

    def lvds_cmd(self, opcode, address, data, profile=0, control=0, wait=0):
        """Writes data to the lvds bus
        opcode : Bits 31:27
        data_avail : 26
        address: Bits 25:21
        control_val Bits 20:21
        profile_address 19:16
        data: Bits 15:0
        """
        #High Word consists of following values:
        self.logger.info("lvds cmd: op: "+str(hex(opcode)) +" add: "+str(hex(address)) + \
            " prof: "+str(hex(profile)) + " ctl: "+str(hex(control)) + \
            " wait: " +str(hex(wait)))
        avail_val = 1 << 10
        opcode_val = opcode << 11
        address_val = address << 6
        control_val = control << 4
        profile_val = profile
        #The Highword Words calculated:
        high_word = opcode_val | address_val  \
            | profile_val |control_val
        high_word_avail = high_word | avail_val
        self.logger.info("lvds cmd: highword: "+str(hex(high_word)))

        #Low Word
        data_val = data % (2**16)

        # Set the low word first
        low_insn = instructions.p(data_val, 1)
        self.sequencer.add_insn(low_insn)
        # Set the hight words
        high_insn = instructions.p(high_word, 0)
        self.sequencer.add_insn(high_insn)
        high_insn_avail = instructions.p(high_word_avail, 0)
        self.sequencer.add_insn(high_insn_avail)
        self.wait(wait)
        # Add a copy of high_insn
        self.sequencer.add_insn(copy.copy(high_insn))

    def reset_fifo(self, dds_instance):
        """resets the FIFO of the dds"""
        device_address = dds_instance.device_addr
        val = 0
        self.lvds_cmd(self.reset_opcode, device_address, val, wait=2)

    def dds_to_serial(self, word, length, reg_address, dds_address=0):
        """Generates LVDS commands for writing the registers of the DDS
        """
        fifo_wait = 8
        addr_wait = 20 + 30*int(length / 16) * 2
        reg_address = reg_address << 8
        #Our upper 8 Bits are the Address bits  Duuh
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
            self.reset_fifo(dds_instance)
            val = dds_instance.reg_value_dict[register]
            self.dds_to_serial(val, register[1], register[0])

    def update_dds(self, dds_instance):
        "updates the DDS IO registers after a write"
        address = dds_instance.device_addr
        val = 0
        self.lvds_cmd(self.dds_up_opcode, address, val, wait=10)

    def set_dds_freq(self, dds_instance, freq_value, profile=0):
        "Sets the dds frequency of a given profile register"
        self.reset_fifo(dds_instance)
        dds_instance.set_freq_register(profile, freq_value)
        freq_register = dds_instance.PROF_START
        reg_addr = freq_register[0] + profile
        word_length =  freq_register[1]
        reg_value = dds_instance.reg_value_dict[(reg_addr, word_length)]
        self.dds_to_serial(reg_value, word_length, reg_addr)

    def load_phase(self, dds_instance, profile):
        "Loads the phase register with the FTW of the given register"
        # UNTESTED
        device_address = dds_instance.device_addr
        fpga_tuning_word = dds_instance.get_fpga_ftw(profile)
        self.logger.warning("load phase fpga ftw: "+str(hex(fpga_tuning_word)))
        lower_val = fpga_tuning_word % (2**16)
        upper_val = (fpga_tuning_word >> 16) % (2**16)
        #The control is untested !!!
        self.lvds_cmd(self.phase_load_opcode, device_address, upper_val,
                      profile=profile, control=0x0, wait=0)
        # set control word to 1 for set current
        self.lvds_cmd(self.phase_load_opcode, device_address, lower_val,
                      profile=profile, control=0x1, wait=0)
        # set control word to 3 for wren
        self.lvds_cmd(self.phase_load_opcode, device_address, lower_val,
                      profile=profile, control=0x3, wait=0)


    def pulse_phase(self, dds_instance, profile, phase_offset=0):
        """switches to the given phase register with additional phase offset"""
        # UNTESTED
        device_address = dds_instance.device_addr

        val = (phase_offset / math.pi) * (2 ** 16)
        val = int(val) % (2**16)
        self.lvds_cmd(self.phase_pulse_opcode, device_address, val,
                      profile=profile, wait=10)

    def dac_value(self, address, val):
        """Sets the dac on the DDS board
        """
        self.lvds_cmd(self.dac_opcode, address, val)

    def ttl_value(self, value, select=2):
        """Sets the status of a whole 16Bit output system
        """
        ttl_insn = instructions.p(value, select)
        self.sequencer.add_insn(ttl_insn)

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
