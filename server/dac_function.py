#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-07-10 15:03:40 c704271"

#  file       dac_function.py
#  copyright  (c) Max Harlander 2008
#  url        http://pulse-sequencer.sf.net
from dac_control import DacControl
import logging
import sequence_handler

class dac_API(DacControl):

    def __init__(self, num_cards):
        self.logger = logging.getLogger("DACcontrol")
        DacControl.__init__(self, num_cards)
        Update_only = False

    def set_dac(self, chandler):
        """get params sent by QFP and set DACs accordingly
        """
        Update_only = False
        self.chandler = chandler
        if self.chandler.dac_voltarrays:
            #Just a static update
            self.dac_voltarrays = self.chandler.dac_voltarrays
            for volts in self.dac_voltarrays.items()
                self.update(volts[0],volts[1])
            Update_only = True
        elif self.chandler.dac_ramps:
#Put everything into an own class, the rampclass... 
            self.rhandler = self.RampHandler(self.chandler)
        
        return Update_only


    def update(self, dac_device, dac_array):
        """Update the static voltageoutput on all channels of the given dac_card
        """
        self.clear_data(dac_device)
        self.stop_card(dac_device)
        self.set_static(dac_device, dac_array)
        self.start_static_task(dac_device)



class RampHandler(DacControl):
    "class for all the ramping stuff."

    def __init__(self, chandler):
        "inits Ramphandling by getting ramps from handler and sequencefile"
#        self.devices = {}
        self.ramp_array = []
        self.all_ramps = []
        self.pulse_program_name = self.chandler.pulse_program_name
        filename = self.seq_directory + self.pulse_program_name
        try:
            fobj = open(filename)
            sequence_string = fobj.read()
            fobj.close()
        except:
            raise RuntimeError("Error while loading sequence:" +str(filename))
        #Parse sequence
        ramp_str = sequence_handler.parse_sequence(sequence_string, is_ramp=True)
        self.logger.debug(ramp_str)
        exec(ramp_str)

        
#Needed to get the Rampvariables like ON/OFF or so? Mazbe I can implement it a bit different!?
    def set_variable(self, var_type, var_name, default_val, \
                         min_val=None, max_val=None):
        "sets a variable from a command string"
        try:
            var_val = self.chandler.variables[var_name]
            cmd_str = "var_obj = " + str(var_val)
            exec cmd_str
        except:
            # We return the default_val if an unknown variable was asked for.
            self.logger.warn("Variable not found in comand string: " \
                             +str(var_name))
            var_obj = default_val
        return var_obj


    def set_ramp(self, rampdict):
        """sets the ramp_dict as a instance of RampDict class from a command string or returns the default 
        """
        try:
            rampdict_val = self.chandler.dac_ramps[rampdict["ramp"]]
            cmd_str = "ramp" + "= RampDict(" + str(rampdict_val) + ")"
            exec cmd_str

        except KeyError:
            # We return the default_val if an unknown variable was asked for.
            self.logger.warn("Ramp not found in comand string: " \
                             +str(rampdict["ramp"]))
            cmd_str = "ramp" + " = RampDict(" + str(rampdict) + ")"
            exec cmd_str
#        self.devices[ramp["dev"]] = True
        self.ramp_array.append(ramp)
        return ramp

    def setup_ramps(self, ramps = self.ramp_array, rampto = {}, offset = False, is_last = True):
        """sets up the ramps, in that order as its given in the array, or if
        no array is given, then it'll use order as set_ramp was called in sequencefile
        """
        if rampto and is_last:
            "Do some ramptostuff"
            for i in range(1,len(self.card_dict)+1):
                first_device_ramp_index = ramps.index(i)
                self.card_dict[i].start_rampto(rampto["T"], rampto["dt"], rampto["shape"])
#find start values /first rampindex found... now get C to give it to us
#create the rampto
#start it for all cards
#wait till all are done
#clear all tasks
            self.clear_data(i)
            self.stop_card(i)



        if offset:
            "or maybe use an offset?"
#find start values
#calc offset values

        for ramp in ramps:
            self.all_ramps.append(ramp)
        if is_last:
            min_dt = min(self.all_ramps)["dt"]
            for ramp in self.all_ramps:
                self.card_dict[ramp["dev"]].append_ramp(ramp["T"], min_dt)
            for ramp in self.all_ramps:
                self.card_dict[ramp["dev"]].append_ramparray(ramp["file"], ramp["T"], ramp["start"], ramp["stop"], ramp["shape"])
            self.start_ramp_tasks()

    def start_ramp_tasks(self):
        """Starts the prepared ramptasks
        """


class RampDict(dict):
    """dictclass with rampextensions so, allowing changes to min()-, index()-function 
    and create an inverse to run the ramp backwards"""
    def __init__(self, params):
        self.update(params)
        self.inv = self.get_inv()

    def __cmp__(self, y):
        "will change the min() function for a array of RampDicts"
        if self["dt"] > y["dt"]:
            i = 1
        if self["dt"] < y["dt"]:
            i = -1
        else:
            i = 0
        return i

    def __eq__(self, y):
        "will change the .index() function aor an array of Rampdicts"
        if self["dev"] == y:
            return True
        else:
            return False

    def get_inv(self):
        "create a copy of the ramp with inversed start and stop, to use it with ramp.inv to go backwards"
        newdic = self.copy()
        newdic["stop"] = self["start"]
        newdic["start"] = self["stop"]
        return newdic


#Der alte Muell, den man nochma brauchen koennt>






#RAMPstuff:
"""
    def setup_ramps(self, ramps, rampto):
        "setup ramps, the sampling rate will be defined by the LAST appended ramp for each device!!!"
        self.clear_all()
        dac_device = {}
        if (rampto):
            if (rampto == 1):
                for i in range(1,len(self.card_dict)+1):
                    if (i in rampdict["dev"]):
                        firstramp = rampdict["file"][rampdict["dev"].index(i)]
                        self.card_dict[i].set_offset(firstramp)
            else:
                for i in range(1,len(self.card_dict)+1):
                    if (i in rampdict["dev"]):
                        firstramp = rampdict["file"][rampdict["dev"].index(i)]
                        self.card_dict[i].rampto(firstramp, rampto["T"], rampto["dt"], rampto["shape"])
                        self.clear_data(i)
                        self.stop_card(i)
        for j in range(1,len(self.card_dict)+1):
            dac_device[j] = False
            for i in range(len(rampdict["dev"])):
                if (rampdict["dev"][i] == j):
                    self.card_dict[j].append_ramp(rampdict["T"][i],min(rampdict["dt"]))
                    dac_device[j] = True
        for i in range(len(rampdict["dev"])):
            self.card_dict[j].append_ramparray(rampdict["file"][i], rampdict["T"][i], rampdict["start"][i], rampdict["stop"][i], rampdict["shape"][i])
        return dac_device



    def start_ramp_tasks(self, dac_device, timing, continous):
        "Create and start the ramps Task"
        ramptimes = {}
        for i in range(1, len(dac_device)+1):
            ramptimes[i] = 0
            if (dac_device[i]):
                self.card_dict[i].start_timed_task(timing, continous)
                ramptimes[i] = self.new_duration(i)
        return ramptimes"""


# dac_control.py ends here
