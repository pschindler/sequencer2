#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-07-01 13:28:51 c704271"

#  file       test_lvds_bus.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net

import logging
from sequencer2 import sequencer
from sequencer2 import api
from sequencer2 import comm
from sequencer2 import ad9910
from sequencer2 import ptplog

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
        "Test ttl pulses of box"
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
        my_api.label("start_loop")
        my_api.ttl_value(0xffff, 0)
        my_api.ttl_value(0xffff, 1)
        my_api.wait(5000)
        my_api.ttl_value(0x0, 0)
        my_api.ttl_value(0x0, 1)
#        my_api.ttl_value(0xf, 1)
        my_api.wait(5000)
#        my_api.ttl_value(0xaaaa, 0)
#        my_api.ttl_value(0xaaaa, 1)
#        my_api.wait(100)
        my_api.jump("start_loop")
        self.compile(my_sequencer)

    def test_dds_simple(self, frequency=10):
        "Just sets a single profile of the dds and activates it"
        my_sequencer = sequencer.sequencer()
        my_api = api.api(my_sequencer)
        dds_device = ad9910.AD9910(0, 800)
        my_api.init_dds(dds_device)
        my_api.set_dds_freq(dds_device, frequency, 0)
        my_api.update_dds(dds_device)
#        my_api.dac_value(0, 2**14-100)
        my_api.dac_value(0, 0)
        self.compile(my_sequencer)

    def test_dds_loop(self, frequency=10):
        "Just sets a loop profile of the dds and activates it"
        my_sequencer = sequencer.sequencer()
        my_api = api.api(my_sequencer)        
        dds_device = ad9910.AD9910(0, 800)        

        my_api.label("beginseq")
        my_api.init_dds(dds_device)        
        my_api.set_dds_freq(dds_device, frequency, 0)
        my_api.update_dds(dds_device)
        my_api.dac_value(0, 0)
        my_api.jump("beginseq")        

        self.compile(my_sequencer)


    def compile(self, my_sequencer, show_debug=0):
        "compile and send the sequence"
        my_sequencer.compile_sequence()
        ptp1 = comm.PTPComm(self.nonet)
        ptp1.send_code(my_sequencer.word_list)
        if show_debug:
            my_sequencer.debug_sequence()

# test_lvds_bus.py ends here
