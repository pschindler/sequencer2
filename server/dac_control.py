#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-03-20 16:35:13 c704271"

#  file       dac_control.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net

#from Nidaq_dummy import nidaq as nidaq_test #Dummy for testing
#nidaq = nidaq_test()
import nidaq                   #real Nidaq-module


#pure Methods provided by NiDAQ Module


#Main Electrode Updateprogram

class DacControl:
    """Baseclass for dac_function to control the Nidaq-cards
    """

    def __init__(self, num_cards):
        "create an instance for all Cards and put them into card_dict"
        self.card_dict = {}
        for i in range(1,num_cards+1):
            self.card_dict[i] = nidaq.Nidaq(i)
        #und was halt sonst noch alles gemacht werden muss.....

    #Static update methods:
    def set_static(self, device, dac_array):
        """Load given array into card "device", use _start_static_task to update
        """
        self.card_dict[device].set_static(dac_array)

    def start_static_task(self, device):
        """Start static update task, in means of update voltages
        """
        self.card_dict[device].start_static_task()

    #Ramp methods:
    def append_from_file(self, device, file):
        """Load array from a file into the card "device" for preparing a triggered task
        """
        self.card_dict[device].append_from_file(file)

    def new_duration(self, device):
        """calculate new integer Duration
        """
        new_totaltime = self.card_dict[device].get_new_duration()
        return new_totaltime

    def start_timed_task(self, device):
        """Start a clock-timed task, with preloaded Voltage array
        """
        self.card_dict[device].start_timed_task()

    #Control methods:
    def clear_data(self, device):
        """clear the card device
        """
        self.card_dict[device].clear_data()

    def stop_card(self, device):
        """deletes all tasks written to device
        """
        self.card_dict[device].stop_card()

    def set_task_parameters(self, params, device):
        """Sets continous mode on/off and samples per second
        """
        self.card_dict[device].set_task_parameters(params)

    def clear_all(self):
        """Clears and deletes the task set on device
        """
        for i in self.card_dict:
            self.clear_data(i)
            self.stop_card(i)



    def calc_ramp(self, device):
        """deletes all tasks written to device
        """
        self.card_dict[device].calc_ramp(self.duration, self.interval, self.start, self.stop, self.shape)

