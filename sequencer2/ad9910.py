#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-06-24 12:45:37 c704271"

#  file       ad9910.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net
"""
AD9910
======

Class for the registers of the AD9910 DDS
-----------------------------------------

  Furhter information on the DDS functionality may be
  found in the AD9910 datasheet:

  http://www,analog.com/dds


Important DDS registers:
------------------------

  0x00  Control Register 1
    - Autoclr Phase

  0x01  Control Register 2
    - PDCLK enable
    - Parallel data port enable
    - Parallel data port gain

  0x02  Control Register 3
    - REFCLK divider bypass
    - REFCLK divider reset

  0x07 Frequency Tuning Word

  0x08 Phase Offset Word

  0x0E Single Tone Profile 0
  ...
  ...
  0x15 Single Tone Profile 7

  0x16 RAM

Initializing the DDS registers:
-------------------------------

  The DDS registers are initialized with the method init_device()

  Standard values are:
  >>>#CFR1
self.auto_clr.set_value(1)
#CFR2
self.para_en.set_value(1)
self.para_hold_last.set_value(1)
self.para_gain.set_value(0x0)
#CFR3
self.divider_bypass.set_value(1)
self.divider_reset.set_value(1)

"""
import copy
from sequencer2.bitmask import Bitmask

class ProfileRegister:
    """Class for a profile register containing of:
        ftw : frequency tuning word
        phow : phase offset word
        asf : amplitude scale factor
        transition_name: name of transition for this register
    """
    def __init__(self, ftw=0, phow=0, asf=0):
        self.ftw = ftw
        self.phow = phow
        self.asf = asf
        self.transition_name = None

class AD9910:
    """base class dor AD9910
    """

    # Adrresses for the registers
    # format: (address, length in Bits)
    CFR1 = (0x00, 32)
    CFR2 = (0x01, 32)
    CFR3 = (0x02, 32)
    FTW = (0x07, 32)
    PHOW = (0x08, 16)
    PROF_START = (0x0E, 64)

    DRL = (0x0B, 64) # Digital Ramp Limit Register
    DRS = (0x0C, 64) # Digital Ramp Step Register
    DRR = (0x0D, 32) # Digital Ramp Rate Register    

    Ifs = 0xff # full-scale output current of the DDS DAC

    # Bitmasks for the configuration
    auto_clr = Bitmask(label="auto_clr", width=1, shift=13)
    pdclk_en = Bitmask(label="pdclk_en", width=1, shift=11)
    para_en = Bitmask(label="parallel_enable", width=1, shift=4)
    para_gain = Bitmask(label="parallel_gain", width=4, shift=0)
    para_hold_last = Bitmask(label="data assembler hold last", width=1, shift=6)
    divider_bypass = Bitmask(label="divider_bypass", width=1, shift=15)
    divider_reset = Bitmask(label="divider_reset", width=1, shift=14)
#    digital_ramp_enable = Bitmask(label="digital_ramp_enable", width=1, shift=19)


    def __init__(self, device_addr, ref_freq, clk_divider=8):
        """generates the register variables
        """
        self.device_addr = device_addr
        self.ref_freq = float(ref_freq)
        self.prof_reg = []
        prof_reg_inst = ProfileRegister()
        for i in range(8):
            self.prof_reg.append(copy.copy(prof_reg_inst))

        # Set the bitmasks for the register
        self.reg_bitmask_dict = {}
        self.reg_bitmask_dict[self.CFR1] = [self.auto_clr]
        self.reg_bitmask_dict[self.CFR2] = [self.pdclk_en, self.para_en,
                                            self.para_gain, self.para_hold_last]
        self.reg_bitmask_dict[self.CFR3] = [self.divider_bypass, self.divider_reset]
        self.reg_value_dict = {}
        #set the clk divider for DDS/FPGA Clock
        self.clk_divider = clk_divider
        #Generate the init register values
        self.init_device()

    def init_device(self):
        """initialized the control registers
        """
        #CFR1
        self.auto_clr.set_value(1)
        #CFR2
        self.para_en.set_value(1)
        self.para_hold_last.set_value(1)
        self.para_gain.set_value(0x0)
        #CFR3
        self.divider_bypass.set_value(1)
        self.divider_reset.set_value(1)

        self.set_conf_register(self.CFR1)
        self.set_conf_register(self.CFR2)
        self.set_conf_register(self.CFR3)

    def set_conf_register(self, register):
        """sets the binary value of the configuration register
        """
        value = 0x0
        try:
            for bitmask in self.reg_bitmask_dict[register]:
                value = value | bitmask.get_value()
        except KeyError:
            print "Cannot get bitmasks for address: "+str(register)
            return
        self.reg_value_dict[register] = value

    def set_freq_register(self, register_addr, frequency, phase=0, asf=0x8B5):
        """sets the hex value of a profile register
        """
        freq_val = int(2**(32) * frequency / self.ref_freq) + 1
        freq_val = freq_val - freq_val % 8
        phase_val = phase << 32
        asf_val = asf << 48      # amplitude scaling factor
        addr_tuple = (self.PROF_START[0] + register_addr, self.PROF_START[1])
        self.reg_value_dict[addr_tuple] = freq_val | asf_val | phase_val

    def get_fpga_ftw(self, register_addr):
        """Returns the tuning word for the FPGA phase register
        used for phase coherent switching"""
        addr_tuple = (self.PROF_START[0] + register_addr, self.PROF_START[1])
        dds_ftw = self.reg_value_dict[addr_tuple] % 2**32
        fpga_ftw = int(dds_ftw *  self.clk_divider) % 2**32
        return fpga_ftw


# what we need: upper. lower limit, time and value step size set
# activate ramp (save old parameters)
# autoclear to switch off
# choose between phase, amplitude, frequency
# check wether current_frequency in (lower, upper) limits
# check input parameters for max and min


    def set_ramp_configuration_registers(self, ramp_type, dt_pos, dt_neg, dstep_pos, dstep_neg, lower_limit, upper_limit):
        """sets the registers for the digital ramp controller
        ramp = (dfreq/dt_(pos,neg)) * t + current_frequency
        min(ramp) = lower_limit
        max(ramp) = upper_limit
        min(dt_(pos,neg)) = 5ns @ 800 MHz clock
        """
        if (lower_limit>upper_limit):
            raise("Can't programm ramp generator because lower limit > upper limit")

       
        reg_ramp_rate_pos = int(dt_pos/4.0 * self.ref_freq) + 1
        reg_ramp_rate_neg = int(dt_neg/4.0 * self.ref_freq) + 1
        reg_ramp_rate_neg = reg_ramp_rate_neg << 16
        
        if ramp_type=='freq': 
            reg_lower_limit   = int(2**(32) * lower_limit / self.ref_freq) + 1
            reg_upper_limit   = int(2**(32) * upper_limit / self.ref_freq) + 1
            reg_upper_limit   = reg_upper_limit << 32

            reg_ramp_step_pos     = int(2**(32) * dstep_pos / self.ref_freq) + 1
            reg_ramp_step_neg     = int(2**(32) * dstep_neg / self.ref_freq) + 1
            reg_ramp_step_neg     = reg_ramp_step_neg << 32        
            # change the bits for the frequency sweep, bit 20:21 in cfr2 while keeping the rest the same
            self.reg_value_dict[self.CFR2] = self.set_bit_state(self.reg_value_dict[self.CFR2], 0, 20, 2)

        if ramp_type=='phase':
            reg_lower_limit   = int(2**(13) * lower_limit / 45.0) + 1
            reg_upper_limit   = int(2**(13) * upper_limit / 45.0) + 1
            reg_upper_limit   = reg_upper_limit << 32

            reg_ramp_step_pos     = int(2**(13) * dstep_pos / 45.0) + 1   
            reg_ramp_step_neg     = int(2**(13) * dstep_neg / 45.0) + 1   
            reg_ramp_step_neg     = reg_ramp_step_neg << 32        
            # change the bits for the phase sweep, bit 20:21 in cfr2 while keeping the rest the same
            self.reg_value_dict[self.CFR2] = self.set_bit_state(self.reg_value_dict[self.CFR2], 1, 20, 2)

        if ramp_type=='ampl':
            reg_lower_limit   = int(1.8*2**(18) * lower_limit / self.Ifs) << 20
            reg_upper_limit   = int(1.8*2**(18) * upper_limit / self.Ifs) << 20

            print hex(reg_upper_limit)
            reg_upper_limit   = reg_upper_limit << 32

            reg_ramp_step_pos     = int(1.8*2**(18) * dstep_pos / self.Ifs) << 20
            reg_ramp_step_neg     = int(1.8*2**(18) * dstep_neg / self.Ifs) << 20
            reg_ramp_step_neg     = reg_ramp_step_neg << 32
            # change the bits for the ampl sweep, bit 20:21 in cfr2 while keeping the rest the same
            self.reg_value_dict[self.CFR2] = self.set_bit_state(self.reg_value_dict[self.CFR2], 2, 20, 2)

        self.reg_value_dict[self.DRL] = reg_lower_limit | reg_upper_limit
        self.reg_value_dict[self.DRS] = reg_ramp_step_pos | reg_ramp_step_neg
        self.reg_value_dict[self.DRR] = reg_ramp_rate_pos | reg_ramp_rate_neg

        print hex(self.reg_value_dict[self.DRL])
        print hex(self.reg_value_dict[self.DRS])
        print hex(self.reg_value_dict[self.DRR])






    def switch_digital_ramp_enable_register(self, val):
        """Switches the Digital Ramp Enable bit in register CFR2
        Digital Ramp Enable bit 19 in CFR2
        """
        self.reg_value_dict[self.CFR2] = self.set_bit_state(self.reg_value_dict[self.CFR2], val, 19, 1)  # parallel pin activated at the same time?!?!?
       


    def switch_autoclear_register(self, val):
        """Switches the Digital Ramp Autoclear bit in register CFR1
        Digital Ramp Enable bit 14 in CFR1
        """
        self.reg_value_dict[self.CFR1] = self.set_bit_state(self.reg_value_dict[self.CFR1], val, 14, 1) 
       


    def set_bit_state(self, n, val, pos, bit_size):
        """This function sets certain bits to the value given while keeping the rest the same
        watch out: pos starts to count at zero
        e.g. n = 1001010101, val = 2, pos = 4, bit_size = 3
        -> ret = 1000100101"""

        return ( (n - (n & ((2**bit_size - 1)<<pos))) ^ (val<<pos) )


# ad9910.py ends here
