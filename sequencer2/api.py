#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-09-15 13:04:42 c704271"

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
    This class contains functions to directly access the
    hardware of the sequencer. This functions are used by
    the high level functions definde in  server.instruction_handler

    This functions may also be used for testing the hardware
    """
    def __init__(self, sequencer, ttl_dict=None):
        """Initialization of the API
        @param sequencer: a sequencer2.sequencer object
        @param ttl_dict: A TTL channel dictionary as defined in
                   sequencer2.outputsystem
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
        self.fifo_reset_opcode = 0x1f


        # bitmasks for the digital ramp generator
        self.DRCTL_bit = 16
        self.DRHOLD_bit = 17
        self.DDSRAMPCONF_bit = 18


        self.logger = logging.getLogger("api")
        self.ttl_sys = outputsystem.OutputSystem(ttl_dict)

        self.recalibration = self.config.recalibration
        self.dds_list = []


    def clear(self):
        "Reset the dds list"
        pass
        #self.dds_list = []

    #################################################################
    #   The general PCP instructions
    #################################################################
    def wait(self, wait_time, use_cycles=False):
        """inserts a wait event
        needs calibration !!! wait has to be > 4 ?
        @param wait_time : time in us to wait
        @param use_cycles: If set to True the wait_time will be interpreted as cycles
        """
        if use_cycles:
            wait_cycles = wait_time
        else:
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
                # Do we really need wait_cycles - 4 ??
                self.sequencer.add_insn(wait_insn)
                wait_cycles -= my_wait
                for i in range(self.branch_delay_slots):
                    self.sequencer.add_insn(copy.copy(nop_insn))
        else:
            for i in range(wait_cycles):
                self.sequencer.add_insn(copy.copy(nop_insn))

    def label(self, label_name):
        """inserts a label and a NOP
        @param label_name: String identifier for the Label
        """
        label_insn = instructions.label(label_name)
        self.sequencer.add_insn(label_insn)

    def jump(self, target_name):
        """unconditional jump to label
        @param target_name: String identifier of the label to jump to
        """
        jump_insn = instructions.j(target_name)
        nop_insn = instructions.nop()
        self.sequencer.add_insn(jump_insn)
        for index in range(self.branch_delay_slots):
            self.sequencer.add_insn(copy.copy(nop_insn))

    def jump_trigger(self, target_name, trigger):
        """branch on trigger
        Adds a conditional jump
        @param target_name:  String identifier of the label to jump to
        @param trigger : trigger state in hex
        """
        jump_insn = instructions.btr(target_name, trigger)
        nop_insn = instructions.nop()
        self.sequencer.add_insn(jump_insn)
        for index in range(self.branch_delay_slots):
            self.sequencer.add_insn(copy.copy(nop_insn))

    def start_finite(self, target_name, loop_count):
        """at the beginning of a finite loop
        adds a ldc instruction and a label intruction
        @param target_name: String identifier of the label to jump to
        @param loop_count: Desired number of loops
        """
        self.sequencer.bdec_register.append(loop_count)
        register_addr = len(self.sequencer.bdec_register) - 1

        ldc_insn = instructions.ldc(register_addr, loop_count)
        self.sequencer.add_insn(ldc_insn)

        label_insn = instructions.label(target_name)
        self.sequencer.add_insn(label_insn)

    def end_finite(self, target_name):
        """At the ending of a finite loop
        Adds a bdec instruction and fills the branch delay slots
        @param target_name: String identifier of the label to jump to
        """
        register_addr = len(self.sequencer.bdec_register) - 1
        if register_addr < 0:
            raise RuntimeError("Cannot pop from empty loop stack")
        self.sequencer.bdec_register.pop()

        bdec_insn = instructions.bdec(target_name, register_addr)

        nop_insn = instructions.nop()
        self.sequencer.add_insn(bdec_insn)
        for index in range(self.branch_delay_slots):
            self.sequencer.add_insn(copy.copy(nop_insn))







    def instructions_bdec(self, target_name, reg_addr):
        bdec_insn = instructions.bdec(target_name, reg_addr)
        nop_insn = instructions.nop()
        self.sequencer.add_insn(bdec_insn)

    def instructions_ldc(self, reg_addr, loop_count):
        ldc_insn = instructions.ldc(reg_addr, loop_count)
        nop_insn = instructions.nop()
        self.sequencer.add_insn(ldc_insn)









    def begin_subroutine(self, sub_name):
        """inserts a label for a subroutine
        It has to be called with an empty sequencer.current_sequence
        @param sub_name:  String identifier of the subroutine
        """
        self.sequencer.begin_subroutine()
        self.sequencer.add_insn(instructions.label(sub_name))

    def end_subroutine(self):
        """ends the subroutine
        Adds the current sequence to the sequencer.sub_list
        Flushes  sequencer.current_sequence
        """
        self.sequencer.add_insn(instructions.ret())
        self.sequencer.end_subroutine()

    def call_subroutine(self, sub_name):
        """calls a subroutine
        sub_name
        @param sub_name:  String identifier of the subroutine to call
        """
        call_insn = instructions.call(sub_name)
        nop_insn = instructions.nop()
        self.sequencer.add_insn(call_insn)
        self.sequencer.add_insn(nop_insn)
        self.sequencer.add_insn(copy.copy(nop_insn))
        self.sequencer.add_insn(copy.copy(nop_insn))

    def ttl_value(self, value, select=2):
        """Sets the status of a whole 16Bit output system
        @param value: Integer value corresponding to the 16bit output
        @param select: Selects which of the 4 16bit subgroups to use
        """
        ttl_insn = instructions.p(value, select)
        self.sequencer.add_insn(ttl_insn)

    #################################################################
    # The LVDS functions for the ad9910 board
    #################################################################

    def __lvds_cmd(self, opcode, address, data, phase_profile=0, control=0, wait=0):
        """Writes data to the lvds bus
        The data_avail (Bit 26) is set for each command
        @param opcode: Bits 31:27
        @param address: Bits 25:22
        @param data: Bits 15:0
        @param phase_profile: Bits 19:16 Phase profile for FPGA
        @param control: Bits 20:21
        @param wait: Time to wait in us after the command is sent
        avail_val: Bit 26
        """

        # Check the input numbers for errors
        assert address<2**4, "LVDS: DDS address >= 2**4!"
        assert opcode<2**5 , "LVDS: Opcode bigger >= 2**5!"
        assert data<2**16, "LVDS: Data bigger >= 2**16!"
        assert phase_profile<2**4, "LVDS: Phase profile bigger >= 2**4!"
        assert data<2**16, "LVDS: Data bigger >= 2**16!"
        assert control<2**4, "LVDS: Data bigger >= 2**16!"

        #High Word consists of following values:
        self.logger.debug("lvds cmd: op: "+str(hex(opcode)) +" add: "+str(hex(address)) + \
            " prof: "+str(hex(phase_profile)) + " ctl: "+str(hex(control)) + \
            " wait: " +str(hex(wait)))
        avail_val = 1 << 10
        opcode_val = opcode << 11
        address_val = address << 6
        control_val = control << 4
        phase_profile_val = phase_profile
        #The Highword Words calculated:
        high_word = opcode_val | address_val  \
            | phase_profile_val |control_val
        high_word_avail = high_word | avail_val
        self.logger.debug("lvds cmd: highword: "+str(hex(high_word)))


        #Low Word
        data_val = data % (2**16)

        # Set the low word first
        low_insn = instructions.p(data_val, 1)
        self.sequencer.add_insn(low_insn)
        # Set the high words
        high_insn = instructions.p(high_word, 0)
        self.sequencer.add_insn(high_insn)
        high_insn_avail = instructions.p(high_word_avail, 0)

        self.wait(3, use_cycles=True)

        self.sequencer.add_insn(high_insn_avail)
        self.wait(wait, use_cycles=True)
        # Add a copy of high_insn
        self.sequencer.add_insn(copy.copy(high_insn))

    def dac_value(self, val, address):
        """Sets the dac on the DDS board
        @param val: value of the dac in db
        @param address: logic address of the dds board
        """
        val = self.recalibration(val)
        self.__lvds_cmd(self.dac_opcode, address, val)

    def reset_fifo(self, dds_instance):
        """resets the FIFO of the dds"""
        device_address = dds_instance.device_addr
        val = 0
        self.__lvds_cmd(self.fifo_reset_opcode, device_address, val, wait=2)

    def dds_to_serial(self, word, length, reg_address, dds_address=0):
        """Generates LVDS commands for writing the registers of the DDS
        word = value written in the register
        length = length of word or length of register, respectively
        """
        fifo_wait = 8
        addr_wait = 20 + 30*int(length / 16) * 2
        reg_address = reg_address << 8
        #Our upper 8 Bits are the Address bits  Duuh
        num_words = int(length) / 16
        # Write the FIFO with the data
        for i in range(num_words):
            value = (word >>( 16*(num_words-i-1)  ))% 2**16
            self.__lvds_cmd(self.fifo_opcode, dds_address, value, wait=fifo_wait)
        # Set the register address and wait until finished
        self.__lvds_cmd(self.addr_opcode, dds_address, reg_address, wait=addr_wait)

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
            self.dds_to_serial(val, register[1], register[0], dds_instance.device_addr)

    def update_dds(self, dds_instance):
        "updates the DDS IO registers after a write"
        address = dds_instance.device_addr
        val = 0
        self.__lvds_cmd(self.dds_up_opcode, address, val, wait=10)

    def set_dds_profile(self, dds_instance, profile=0):
        "Sets the dds profile pin on the DDS"
        dds_address = dds_instance.device_addr
        self.__lvds_cmd(self.dds_profile_opcode, dds_address, profile)

    def set_dds_freq(self, dds_instance, freq_value, profile=0):
        "Sets the dds frequency of a given profile register"
        self.reset_fifo(dds_instance)
        dds_instance.set_freq_register(profile, freq_value)
        freq_register = dds_instance.PROF_START   # (addr, length) of first profile register
        reg_addr = freq_register[0] + profile
        word_length =  freq_register[1]
        reg_value = dds_instance.reg_value_dict[(reg_addr, word_length)]
        self.dds_to_serial(reg_value, word_length, reg_addr, dds_instance.device_addr)

    def load_phase(self, dds_instance, profile=0):
        "Loads the phase register with the FTW of the given register"
        # UNTESTED
        device_address = dds_instance.device_addr
        fpga_tuning_word = dds_instance.get_fpga_ftw(profile)
        self.logger.debug("load phase fpga ftw: "+str(hex(fpga_tuning_word)))
        lower_val = fpga_tuning_word % (2**16)
        upper_val = (fpga_tuning_word >> 16) % (2**16)

        # The control is untested !!!
        self.__lvds_cmd(self.phase_load_opcode, device_address, upper_val,
                      phase_profile=profile, control=0x0, wait=0)
        # set control word to 1 for set current
        self.__lvds_cmd(self.phase_load_opcode, device_address, lower_val,
                      phase_profile=profile, control=0x1, wait=0)
        # set control word to 3 for wren
        self.__lvds_cmd(self.phase_load_opcode, device_address, lower_val,
                      phase_profile=profile, control=0x3, wait=0)

    def pulse_phase(self, dds_instance, profile, phase_offset=0):
        """switches to the given phase register with additional phase offset"""
        # UNTESTED
        device_address = dds_instance.device_addr

        val = (phase_offset / math.pi) * (2 ** 16)
        val = int(val) % (2**16)
        self.__lvds_cmd(self.phase_pulse_opcode, device_address, val,
                      phase_profile=profile, wait=10)

    def init_frequency(self, dds_instance, freq_value, profile=0):
        """Writes the frequency into the DDS and initializes a phase register in the FPGA
        If a frequency is already initialized it is simply overwritten"""
        # UNTESTED
        self.set_dds_freq(dds_instance, freq_value, profile)
        self.load_phase(dds_instance, profile)

    def switch_frequency(self, dds_instance, profile, phase_offset=0):
        """Sets the profile pins of the DDS and generates a pulse phase instruction\
        profile=the integer index of the transition that is used"""
        # UNTESTED
        self.set_dds_profile(dds_instance, profile)
        self.update_dds(dds_instance)
        self.pulse_phase(dds_instance, profile, phase_offset)



    # digital ramp generator
    def init_digital_ramp_generator(self, ramp_type, dds_instance, dt_pos, dt_neg, dfreq_pos, dfreq_neg, lower_limit, upper_limit):
        """Initializes the digital ramp generator registers"""

        dds_instance.set_ramp_configuration_registers(ramp_type, dt_pos, dt_neg, dfreq_pos, dfreq_neg, lower_limit, upper_limit) 

        DRLreg = dds_instance.DRL
        DRSreg = dds_instance.DRS
        DRRreg = dds_instance.DRR
        CFR2reg = dds_instance.CFR2

        reg_value = dds_instance.reg_value_dict[DRLreg]
        self.dds_to_serial(reg_value, DRLreg[1], DRLreg[0], dds_instance.device_addr)
        reg_value = dds_instance.reg_value_dict[DRSreg]
        self.dds_to_serial(reg_value, DRSreg[1], DRSreg[0], dds_instance.device_addr)
        reg_value = dds_instance.reg_value_dict[DRRreg]
        self.dds_to_serial(reg_value, DRRreg[1], DRRreg[0], dds_instance.device_addr)
        reg_value = dds_instance.reg_value_dict[CFR2reg]
        self.dds_to_serial(reg_value, CFR2reg[1], CFR2reg[0], dds_instance.device_addr)


    def configure_ramping(self, dds_instance, slope_direction):        
        """slope_direction, +1 = positive slope, 0 = hold generator, -1 = negative slope
        """
        ramp_conf   = 1

        if slope_direction==-1:
            drctl = 0
            drhold = 0
        if slope_direction==0:
            drctl = 0
            drhold = 1
        if slope_direction==1:
            drctl = 1
            drhold = 0

        # since the ramp_conf, drctl and drhold is bit 16:18 we use the phase_profile variable to send it over the lvds bus
        val = 0
        phase_profile = ramp_conf << self.DDSRAMPCONF_bit | drctl << self.DRCTL_bit | drhold << self.DRHOLD_bit
        phase_profile = phase_profile >> 16
        self.__lvds_cmd(self.dds_up_opcode, dds_instance.device_addr, val, phase_profile, wait=0)
 

    def start_digital_ramp_generator(self, dds_instance):
        """Starts the digital ramp generator"""

        dds_instance.switch_digital_ramp_enable_register(1)
        CFR2reg = dds_instance.CFR2
        reg_value = dds_instance.reg_value_dict[CFR2reg]
        self.dds_to_serial(reg_value, CFR2reg[1], CFR2reg[0], dds_instance.device_addr)

        self.update_dds(dds_instance)


    def stop_digital_ramp_generator(self, dds_instance):
        """Stops the digital ramp generator
        by switching off the ramp_enable_register bit
        and setting the ramping slope to negative
        and autoclearing the the register"""

        dds_instance.switch_digital_ramp_enable_register(0)
        CFR2reg = dds_instance.CFR2
        reg_value = dds_instance.reg_value_dict[CFR2reg]
        self.dds_to_serial(reg_value, CFR2reg[1], CFR2reg[0], dds_instance.device_addr)

        dds_instance.switch_autoclear_register(1)
        CFR1reg = dds_instance.CFR1
        reg_value = dds_instance.reg_value_dict[CFR1reg]
        self.dds_to_serial(reg_value, CFR1reg[1], CFR1reg[0], dds_instance.device_addr)

        self.configure_ramping(dds_instance, -1)

        self.update_dds(dds_instance)


    





    #################################################################
    # Functions for the TTL output system
    #################################################################
    def ttl_set_bit(self, key, value):
        """Sets a single bit of the TTL outputs
        @param key: string identifier of the TTL channel
        @param value: integer 0 or 1
        """

        output_state = self.sequencer.current_output
        (select, new_state) = self.ttl_sys.set_bit(key, value, output_state)
        self.sequencer.current_output[select] = new_state
        self.ttl_value(new_state, select)

    def ttl_set_multiple(self, value_dict):
        """Sets multiple pins of the TTL outputs simultanious
        The values are given in the dictionary value_dict
        @param value_dict: Dictionary with channels and values:
                           {"channel" : value, ...}
        """
        # save select is missing !!
        # Generate the bit mask for the given channels
        # Every select mask (1bits) is set separately
        select_list=[]
        for  key in value_dict:
            value = value_dict[key]
            output_state = self.sequencer.current_output
            (select, new_state) = self.ttl_sys.set_bit(key, value, output_state)
            self.sequencer.current_output[select] = new_state
            if select_list.count(select) == 0:
                select_list.append(select)
        # Set the TTL output for all select banks
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
