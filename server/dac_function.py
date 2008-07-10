#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-07-10 15:03:40 c704271"

#  file       dac_function.py
#  copyright  (c) Max Harlander 2008
#  url        http://pulse-sequencer.sf.net
from dac_control import DacControl
import sequence_handler

class dac_API(DacControl):

    def __init__(self, num_cards):
#        DacControl.__init__(self)
        self.init_module(num_cards)

        #additional things, not being handled in baseclass
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

#und nu entweder nur n update oder solln wa doch rampen machen!
        self.dac_ramps = self.chandler.dac_ramps
#nu mach mer Einfach n Update
        else:
            if self.dac_ramps:
#Rampen
        return Update_only



    def update(self, dac_device, dac_array):
        """Update the static voltageoutput on all channels of the given dac_card
        """
        self.clear_data(dac_device)
        self.stop_card(dac_device)
        self.set_static(dac_device, dac_array)
        self.start_static_task(dac_device)


    def set_ramp(self, rampdict):
        """sets the ramp_dict from a command string and appends it
        """
        try:
         #   dac_rampdict = self.chandler.variables[var_name]
          #  cmd_str = str(var_name) + " = " + str(var_val)
           # exec cmd_str

        except KeyError:
            # We return the default_val if an unknown variable was asked for.
            self.logger.warn("Variable not found in comand string: " \
                             +str(var_name))
            cmd_str = str(var_name) + " = " +str(default_val)
            exec cmd_str

#Needed to get the Rampvariables like ON/OFF or so? Mazbe I can implement it a bit different!?
    def set_variable(self, var_type, var_name, default_val, \
                         min_val=None, max_val=None):
        "sets a variable from a command string"
        try:
            var_val = self.chandler.variables[var_name]
            cmd_str = str(var_name) + " = " + str(var_val)
            exec cmd_str

        except KeyError:
            # We return the default_val if an unknown variable was asked for.
            self.logger.warn("Variable not found in comand string: " \
                             +str(var_name))
            cmd_str = str(var_name) + " = " +str(default_val)
            exec cmd_str

#Der alte Muell, den man nochma brauchen koennt>






#RAMPstuff:

    def setup_ramps(self, rampdict, rampto):
        """Sort and setup ramps, the sampling rate will be defined by the LAST appended ramp for each device!!!
        """
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
        """Create and start the ramps Task
        """
        ramptimes = {}
        for i in range(1, len(dac_device)+1):
            ramptimes[i] = 0
            if (dac_device[i]):
                self.card_dict[i].start_timed_task(timing, continous)
                ramptimes[i] = self.new_duration(i)
        return ramptimes


# dac_control.py ends here
