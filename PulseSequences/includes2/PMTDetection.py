#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-08-26 13:22:19 c704271"
#  file       PMTDetection
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net

def PMTDetection(pmt_detect_length):
    """Generate a PMT detection event
    @param pmt_detect_length: Length of PMT gate time
    """
    add_to_return_list("PM Count",2)

    # ttl_pulse(name, duration, starttime=0.0)
    PMT_trigger_length = 1
#    ttl_pulse("PMT trigger", PMT_trigger_length)
#    ttl_pulse("PMT trigger", PMT_trigger_length, start_time=pmt_detect_length)
