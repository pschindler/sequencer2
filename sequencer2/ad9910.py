#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-04-04 14:52:18 c704271"

#  file       ad9910.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net
"""Class for the registers of the AD9910 DDS
"""
import copy
from sequencer2.bitmask import Bitmask

class ProfileRegister():
    """Class for a profile register containing of:
        ftw : frequency tuning word
        phow : phase offset word
        asf : amplitude scale factor
    """
    def __init__(self, ftw=0, phow=0, asf=0):
        self.ftw = ftw
        self.phow = phow
        self.asf = asf

class AD9910():
    """base class dor AD9910
    """

    # Adrresses for the registers
    # format: (address, length)
    CFR1 = (0x00, 32)
    CFR2 = (0x01, 32)
    CFR3 = (0x02, 32)
    FTW = (0x07, 32)
    PHOW = (0x08, 16)
    PROF_START = (0x0E, 64)
    # Bitmasks for the configuration
    auto_clr = Bitmask(label="auto_clr", width=1, shift=13)
    pdclk_en = Bitmask(label="pdclk_en", width=1, shift=11)
    para_en = Bitmask(label="parallel_enable", width=1, shift=4)
    para_gain = Bitmask(label="parallel_gain", width=4, shift=0)
    para_hold_last = Bitmask(label="data assembler hold last", width=1, shift=6)
    divider_bypass = Bitmask(label="divider_bypass", width=1, shift=15)
    divider_reset = Bitmask(label="divider_reset", width=1, shift=14)

    def __init__(self, device_addr, ref_freq, clk_divider=8):
        """generates the register variables
        """
        self.device_addr = device_addr
        self.ref_freq = float(ref_freq)
        self.prof_reg = []
        prof_reg = ProfileRegister()
        for i in range(8):
            self.prof_reg.append(copy.copy(prof_reg))
        # Set the bitmasks for the register
        self.reg_bitmask_dict = {}
        self.reg_bitmask_dict[self.CFR1] = [self.auto_clr]
        self.reg_bitmask_dict[self.CFR2] = [self.pdclk_en, self.para_en,
                                            self.para_gain, self.para_hold_last]
        self.reg_bitmask_dict[self.CFR3] = [self.divider_bypass,self.divider_reset]
        self.reg_value_dict = {}
        #set the clk divider for DDS/FPGA Clock
        self.clk_divider = 8
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
        #self.set_conf_register(self.CFR2)
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
        asf_val = asf << 48
        addr_tuple = (self.PROF_START[0] + register_addr, self.PROF_START[1])
        self.reg_value_dict[addr_tuple] = freq_val | asf_val | phase_val
        val=hex(freq_val | asf_val | phase_val)

    def get_fpga_ftw(self, register_addr):
        "Returns the tuning word for the DDS phase register"
        addr_tuple = (self.PROF_START[0] + register_addr, self.PROF_START[1])
        dds_ftw = self.reg_value_dict[addr_tuple] % 2**32
        print hex(dds_ftw)
        fpga_ftw = int(dds_ftw *  self.clk_divider) % 2**32
        return fpga_ftw

# ad9910.py ends here
