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
#    rf_pulse(8,0,1,"carrier", 0.0, is_last=False, address=1)
#    rf_pulse(3,0,1,"carrier", 0.0, is_last=False, address=0)
#    rf_pulse(10,0,1,"clock1", 0.0, is_last=False, address=2)
#    rf_pulse(15,0,1,"clock2", 0.0, is_last=False, address=5)
#    for k in range(6):
#        rf_pulse(15,0,1,"carrier", k+0.0, is_last=False, address=k)
#        seq_wait(1, k+20.0)

#    rf_pulse(15,0,1,"carrier", 0.0, is_last=False, address=1)
#    rf_pulse(15,0,1,"carrier", 1.0, is_last=False, address=5)
#    seq_wait(10)

#    rf_pulse(15,0,1,"sb_cooling_3", 100.0, is_last=False, address=1)


    PMT_trigger_length = 10
#    ttl_pulse("PMT trigger", PMT_trigger_length)
#    ttl_pulse("PMT trigger", PMT_trigger_length, start_time=pmt_detect_length)
#    ttl_pulse("PMT trigger", PMT_trigger_length, start_time=pmt_detect_length)



    for i in multiple_pulses(255**15+28394):
        ttl_pulse("PMT trigger", 10)
        seq_wait(10)


#    for i in multiple_pulses(255**2*3+256):
#        ttl_pulse("PMT trigger", 10)
#        seq_wait(10)



#    ttl_pulse("PMT trigger", PMT_trigger_length)
#    dds_freq_sweep(5, [0, 10, 30, 50], [1, 0, -1], 10, 20, 10, 60, loop_counts=0)

#    ttl_pulse("PMT trigger", PMT_trigger_length, is_last=False)

#    ttl_pulse("PMT trigger", PMT_trigger_length, start_time=5.0, is_last=False)

    #ttl_pulse("PMT trigger", PMT_trigger_length, is_last=False)
#    dds_freq_sweep(4, [0, 10, 30, 50], [1, 0, -1], 10, 20, 10, 60, 1, 1, is_last=True)


#    dds_ampl_sweep(5, [0, 10, 20, 30], [1, 0, -1], 0.1, 0.1, 10, 10, 10, 100, is_last=False)

#    ttl_pulse("PMT trigger", PMT_trigger_length, start_time=70, is_last=True)



#    for i in multiple_pulses(3):
#        seq_wait(10)
#    for i in multiple_pulses(255**3*5 + 255):
#        ttl_pulse("PMT trigger", 5)
#        seq_wait(5)

    



#    for i in multiple_pulses(256+1):
#        ttl_pulse("866sw", 5)
#        seq_wait(5)


#    for i in multiple_pulses(10):
#        ttl_pulse("PMT trigger", 10)
#        for k in multiple_pulses(2):
#            seq_wait(2)


#    seq_wait(50)

#    for i in multiple_pulses(2):
#        ttl_pulse("PMT trigger", 10)
#        seq_wait(20)
#        for k in multiple_pulses(3):
#            ttl_pulse("PMT trigger", 10)
#            seq_wait(10)

#    for i in multiple_pulses(2, 5):
#        ttl_pulse("PB dummy", 5)
#        for k in multiple_pulses(3, 7):
#            ttl_pulse("PMT trigger", 25)
#    ttl_pulse("PMT trigger", PMT_trigger_length, start_time=pmt_detect_length+200)


#    rf_pulse(10,0,1,"clock1", 0, is_last=True)


