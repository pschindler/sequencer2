#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-07-16 11:07:51 c704271"

#  file       api.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net

"""
API
===

  API functions for the DDS / TTL / DAC /Builtin Commands

  Important functions
  -------------------

    Following functions are most commonly used:
      - wait(wait_time)
      - dac_value(db_value)
      - ttl_set_multiple(value_dict)

"""

import math
import copy
import logging

# sequencer2 classes:
import outputsystem
import instructions
import config

class api:
    """api.py the api commands for sequencer2
    """
    def __init__(self, sequencer, ttl_dict=None):
        """A simple initialization
        The LVDS bus opcodes are defined here
        """
        self.config = config.Config()
        self.cycle_time = self.config.get_float("SERVER", "cycle_time")
        self.branch_delay_slots = self.config.get_int("PCP", "branch_delay_slots")
        self.max_wait_cycles = self.config.get_int("PCP", "max_wait_cycles")

        self.sequencer = sequencer
        # The LVDS opcodes
        # These may be defined in the configuration files ??
        self.addr_opcode = 0x1
        self.fifo_opcode = 0x2
        self.dds_profile_opcode = 0x3
        self.dds_up_opcode = 0x4
        self.dac_opcode = 0x7
        self.phase_load_opcode = 0xa
        self.phase_pulse_opcode = 0xb
        self.reset_opcode = 0x1f

        self.logger = logging.getLogger("api")
        self.ttl_sys = outputsystem.OutputSystem(ttl_dict)

        self.recalibration = self.config.recalibration
        self.dds_list = []

    def clear(self):
        "Reset the dds list"
        self.dds_list = []

    #################################################################
    #   The general PCP instructions
    #################################################################
    def wait(self, wait_time):
        """inserts a wait event
        wait_cycles : time in ns to wait
        needs calibration !!! wait has to be > 4 ?
        """
        wait_cycles = int(wait_time/self.cycle_time)
        if wait_cycles < 1.0:
            self.logger.info("Cannot wait for less than one cycle")
            return

        nop_insn = instructions.nop()
        if wait_cycles > self.branch_delay_slots:
            wait_cycles -= self.branch_delay_slots - 1
            while wait_cycles > 0:
                if wait_cycles > self.max_wait_cycles:
                    my_wait = self.max_wait_cycles
                else:
                    my_wait = wait_cycles

                wait_insn = instructions.wait(my_wait)
                #Do we really need wait_cycles - 4 ??
                self.sequencer.add_insn(wait_insn)
                wait_cycles -= my_wait
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
        for index in range(self.branch_delay_slots):
            self.sequencer.add_insn(copy.copy(nop_insn))

    def start_finite(self, label_name, loop_count):
        """at the beginning of a finite loop
        adds a ldc instruction and a label intruction"""
        self.sequencer.bdec_register.append(loop_count)
        register_addr = len(self.sequencer.bdec_register) - 1
        ldc_insn = instructions.ldc(register_addr, loop_count)
        self.sequencer.add_insn(ldc_insn)
        label_insn = instructions.label(label_name)
        self.sequencer.add_insn(label_insn)

    def end_finite(self, label_name):
        """At the einding of a finite loop
        Adds a bdec instruction and fills the branch delay slots
        """
        register_addr = len(self.sequencer.bdec_register) - 1
        if register_addr < 0:
            raise RuntimeError("Cannot pop from empty loop stack")
        self.sequencer.bdec_register.pop()

        bdec_insn = instructions.bdec(label_name, register_addr)
        nop_insn = instructions.nop()
        self.sequencer.add_insn(bdec_insn)
        for index in range(self.branch_delay_slots):
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

    def ttl_value(self, value, select=2):
        """Sets the status of a whole 16Bit output system
        """
        ttl_insn = instructions.p(value, select)
        self.sequencer.add_insn(ttl_insn)

    #################################################################
    # The LVDS functions for the ad9910 board
    #################################################################

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
        self.logger.debug("lvds cmd: op: "+str(hex(opcode)) +" add: "+str(hex(address)) + \
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
        self.logger.debug("lvds cmd: highword: "+str(hex(high_word)))

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

    def dac_value(self, address, val):
        """Sets the dac on the DDS board
        """
        val = self.recalibration(val)
        self.lvds_cmd(self.dac_opcode, address, val)

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

    #################################################################
    # Functions for the AD9910 DDS
    #################################################################

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

    def set_dds_profile(self, dds_instance, profile=0):
        "Sets the dds profile pin on the DDS"
        dds_address = dds_instance.device_addr
        self.lvds_cmd(self.dds_profile_opcode, dds_address, profile)

    def set_dds_freq(self, dds_instance, freq_value, profile=0):
        "Sets the dds frequency of a given profile register"
        self.reset_fifo(dds_instance)
        dds_instance.set_freq_register(profile, freq_value)
        freq_register = dds_instance.PROF_START
        reg_addr = freq_register[0] + profile
        word_length =  freq_register[1]
        reg_value = dds_instance.reg_value_dict[(reg_addr, word_length)]
        self.dds_to_serial(reg_value, word_length, reg_addr)

    def load_phase(self, dds_instance, profile=0):
        "Loads the phase register with the FTW of the given register"
        # UNTESTED
        device_address = dds_instance.device_addr
        fpga_tuning_word = dds_instance.get_fpga_ftw(profile)
        self.logger.debug("load phase fpga ftw: "+str(hex(fpga_tuning_word)))
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

    def init_frequency(self, dds_instance, freq_value, profile=0):
        """Writes the frequency into the DDS and initializes a phase register in the FPGA
        If a frequency is already initialized it is simply overwritten"""
        # UNTESTED
        self.set_dds_freq(dds_instance, freq_value, profile)
        self.load_phase(dds_instance, profile)

    def switch_frequency(self, dds_instance, profile, phase_offset=0):
        """Sets the profile pins of the DDS and generates a pulse phase instruction"""
        # UNTESTED
        self.set_dds_profile(dds_instance, profile)
        self.update_dds(dds_instance)
        self.pulse_phase(dds_instance, profile, phase_offset)

    #################################################################
    # Functions for the TTL output system
    #################################################################
    def ttl_set_bit(self, key, value):
        """Sets a single bit of the TTL outputs
        """
        # UNTESTED
        output_state = self.sequencer.current_output
        (select, new_state) = self.ttl_sys.set_bit(key, value, output_state)
        self.sequencer.current_output[select] = new_state
        self.ttl_value(new_state, select)

    def ttl_set_multiple(self, value_dict):
        """Sets multiple pins of the TTL outputs simultanious
        The values are given in the dictionary value_dict
        """
        # save select is missing !!
        select_list=[]
        for  key in value_dict:
            value = value_dict[key]
            output_state = self.sequencer.current_output
            (select, new_state) = self.ttl_sys.set_bit(key, value, output_state)
            self.sequencer.current_output[select] = new_state
            if select_list.count(select) == 0:
                select_list.append(select)
        for select in select_list:
            value = self.sequencer.current_output[select]
            self.ttl_value(value, select)
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
