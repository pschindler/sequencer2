#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-02-07 10:53:52 c704271"

#  file       ad9910.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net
"""
Class for the registers of the AD9910 DDS
"""
import copy
from bitmask import Bitmask

class ProfileRegister():
    """Class for a profile register contains of:
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
    FTW = (0x07, 32)
    PHOW = (0x08, 16)
    PROF_START = (0x0E, 64)
    # Bitmasks for the configuration

    auto_clr = Bitmask(label="auto_clr", width=1, shift=13)
    pdclk_en = Bitmask(label="pdclk_en", width=1, shift=11)
    para_en = Bitmask(label="parallel_en", width=1, shift=4)

    def __init__(self, device_addr, ref_freq):
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
        self.reg_bitmask_dict[self.CFR2] = [self.pdclk_en, self.para_en]

        self.reg_value_dict = {}

        self.init_device()

    def init_device(self):
        """initialized the control registers
        """
        self.auto_clr.set_value(1)
        self.pdclk_en.set_value(0)
        self.para_en.set_value(1)
        self.set_conf_register(self.CFR1)
        self.set_conf_register(self.CFR2)

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
        phase_val = phase << 32
        asf_val = asf << 48
        addr_tuple = (self.PROF_START[0] + register_addr, self.PROF_START[1])
        self.reg_value_dict[addr_tuple] = freq_val | asf_val | phase_val
        val=hex(freq_val | asf_val | phase_val)


# ad9910.py ends here
