#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-08-22 12:22:57 c704271"

#  file       test_lvds_bus.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net

import logging
from sequencer2 import sequencer
from sequencer2 import api
from sequencer2 import comm
from sequencer2 import ad9910
from sequencer2 import ptplog

import random

class HardwareTests:
    """Hardware tests for the DDS board"""
    def __init__(self, nonet=False):
        self.nonet = nonet
        self.logger = ptplog.ptplog(level=logging.DEBUG)

    def test_lvds_bus_single(self):
        "Test the LVDS bus. Use this with the corresponding signal tap file"
        my_sequencer = sequencer.sequencer()
        my_api = api.api(my_sequencer)
        my_api.ttl_value(0xffff, 0)
        my_api.ttl_value(0xffff, 1)
        my_api.ttl_value(0xaaaa, 0)
        my_api.ttl_value(0xaaaa, 1)
        my_api.wait(100)
        self.compile(my_sequencer)

    def test_ttl_set(self, value=0xffff, show_debug=0):
        "Test ttl pulses of box"
        my_sequencer = sequencer.sequencer()
        my_api = api.api(my_sequencer)
        my_api.ttl_value(value, 2)
        self.compile(my_sequencer, show_debug)

    def test_trigger(self):
        "Test the trigger functionality of box"
        my_sequencer = sequencer.sequencer()
        my_api = api.api(my_sequencer)

        my_api.ttl_value(0x0, 2)
        my_api.label("start_loop")
        my_api.jump_trigger("trig_label",0x2)
        my_api.jump("start_loop")
        my_api.label("trig_label")
        my_api.ttl_value(0xffff, 2)
        self.compile(my_sequencer)

    def test_lvds_bus_infinite(self):
        "Test the LVDS bus. Use this with the corresponding signal tap file"
        my_sequencer = sequencer.sequencer()
        my_api = api.api(my_sequencer)

#        dds_device = ad9910.AD9910(0, 800)
        my_api.label("start_loop")


#        my_api.init_dds(dds_device)
#        my_api.set_dds_freq(dds_device, 10.0, 0)
#        my_api.update_dds(dds_device)
#        my_api.dac_value(0, 0)
 
        my_api.ttl_value(0x1,1) # trigger on bus[0]
        my_api.ttl_value(0x0,1)

        my_api.ttl_value(0xffff, 0)
        my_api.wait(1, use_cycles=True)
        my_api.ttl_value(0xfffe, 1)
        my_api.wait(10, use_cycles=True)
        my_api.ttl_value(0x0, 0)
        my_api.ttl_value(0x0, 1)
#        my_api.ttl_value(0xf, 1)
#        my_api.wait(2)
#        my_api.ttl_value(0xffff, 0)
#        my_api.ttl_value(0xffff, 1)
#        my_api.wait(3)
#        my_api.ttl_value(0x0, 0)
#        my_api.ttl_value(0x0, 1)
#        dds_device = ad9910.AD9910(0, 800)
#        my_api.init_dds(dds_device)
#        my_api.set_dds_freq(dds_device, 10, 1)
#        my_api.update_dds(dds_device)
#        my_api.dac_value(-20, 0)
#        my_api.set_dds_profile(dds_device,1)

        my_api.jump("start_loop")
        self.compile(my_sequencer)

    def test_dds_simple(self, frequency=10, amplitude=0, my_device=0):
        "Just sets a single profile of the dds and activates it"
        my_sequencer = sequencer.sequencer()
        my_api = api.api(my_sequencer)
        dds_device = ad9910.AD9910(my_device, 800)
#        my_api.init_dds(dds_device)
#        my_api.set_dds_freq(dds_device, frequency, 0)
#        my_api.set_dds_profile(dds_device, 0)
        my_api.ttl_value(0xf, 1)
        my_api.update_dds(0, dds_device)        
#        my_api.dac_value(2**14-100, 0)
#        my_api.dac_value(amplitude, my_device)
        self.compile(my_sequencer)

    def test_dds_loop(self, frequency=10, amplitude=0, my_device=0):
        "Just sets a loop profile of the dds and activates it"
        my_sequencer = sequencer.sequencer()
        my_api = api.api(my_sequencer)
        dds_device = ad9910.AD9910(my_device, 800)
        my_api.label("beginseq")

        my_api.init_dds(dds_device)
        my_api.set_dds_freq(dds_device, frequency, 0)
        my_api.set_dds_profile(dds_device, 0)

        my_api.update_dds(dds_device)
        my_api.dac_value(amplitude, my_device)
        my_api.jump("beginseq")

        self.compile(my_sequencer)


    def test_lvds(self, opcode=1, address=1, data=1, phase_profile=0, control=0, wait=0):
        "Just tests the lvds command"
        
        my_sequencer = sequencer.sequencer()
        my_api = api.api(my_sequencer)
        my_api.label("beginseq")
        my_api.ttl_value(0x2)

        #def __lvds_cmd(self, opcode, address, data, profile=0, control=0, wait=0):

        my_api._api__lvds_cmd(0, 0, 1, 0, 0, 0)
        my_api.wait(1, use_cycles=True)
        my_api._api__lvds_cmd(opcode, address, data, phase_profile, control, wait)
        my_api.wait(1, use_cycles=True)
        my_api._api__lvds_cmd(0, 0, 0)
        my_api.jump("beginseq")


        self.compile(my_sequencer)




    def test_dds_switching(self, frequency1, frequency2, ampl1=0, ampl2=0, my_device=0):
        "Just sets a single profile of the dds and activates it"
        my_sequencer = sequencer.sequencer()
        my_api = api.api(my_sequencer)
        dds_device = ad9910.AD9910(my_device, 800)

        my_api.label("beginseq")
        my_api.init_dds(dds_device)
        my_api.ttl_value(0x2)
        # set_dds_freq params: dds_device, frequency, profile
        my_api.set_dds_freq(dds_device, frequency1, 0)
        my_api.update_dds(dds_device)
        my_api.dac_value(ampl1, my_device)
        my_api.wait(1)
        my_api.set_dds_freq(dds_device, frequency2, 0)
        my_api.update_dds(dds_device)
        my_api.ttl_value(0x0)
        my_api.dac_value(ampl2, my_device)
        my_api.set_dds_freq(dds_device, 0.0, 0)
        my_api.update_dds(dds_device)
        my_api.jump("beginseq")


        self.compile(my_sequencer)

    def test_dds_profile_switching(self, profile1, profile2, my_device=0):
        "Just sets a single profile of the dds and activates it"
        my_sequencer = sequencer.sequencer()
        my_api = api.api(my_sequencer)
        dds_device = ad9910.AD9910(my_device, 800)

        my_api.label("beginseq")
        my_api.init_dds(dds_device)
        # saves frequencies in dds registers/profiles
        my_api.dac_value(0, 0)
        my_api.set_dds_freq(dds_device, 1.0, 0)
        my_api.set_dds_freq(dds_device, 5.0, 1)
        my_api.set_dds_freq(dds_device, 0, 2)

        my_api.update_dds(dds_device)
        my_api.wait(2)
 #       my_api.dac_value(-2, my_device)
        my_api.ttl_value(0x2)
        my_api.set_dds_profile(dds_device, profile1)
        my_api.update_dds(dds_device)
        my_api.wait(2)
        my_api.set_dds_profile(dds_device, profile2)
        my_api.update_dds(dds_device)
        my_api.wait(2)
        my_api.set_dds_profile(dds_device, 2)
        my_api.ttl_value(0x0)
        my_api.jump("beginseq")

        self.compile(my_sequencer)

    def test_kit(self):
        my_sequencer = sequencer.sequencer()
        my_api = api.api(my_sequencer)
        my_api.label("go")
        for k in range(30):
            val = 1 << k
            if k >= 15:
                val = val >> 2*(k-15)
            my_api.ttl_value(val, 2)
            print val
            my_api.wait(200000)
        my_api.jump("go")
        self.compile(my_sequencer, 0)

    def test_random(self):
        my_sequencer = sequencer.sequencer()
        my_api = api.api(my_sequencer)
        my_api.label("go")
        my_api.ttl_value(random.randint(0, 0xffff))
        my_api.wait(200000)
        my_api.jump("go")
        self.compile(my_sequencer, 0)



    def compile(self, my_sequencer, show_debug=0):
        "compile and send the sequence"
        my_sequencer.compile_sequence()
        ptp1 = comm.PTPComm(self.nonet)
        ptp1.send_code(my_sequencer.word_list)
        if show_debug:
            my_sequencer.debug_sequence()

# test_lvds_bus.py ends here
