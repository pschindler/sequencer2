#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-06-17 11:06:07 c704271"

#  file       dac_function.py
#  copyright  (c) Max Harlander 2008
#  url        http://pulse-sequencer.sf.net
from dac_control import DacControl

class dac_API(DacControl):

    def __init__(self, num_cards):
        self.init_dac(num_cards)
        #und was halt sonst noch alles gemacht werden muss.....

    def set_dac(self, chandler):
        """get params sent by QFP and set DACs accordingly
        """
        self.chandler = chandler

        self.pulse_program_name = self.chandler.pulse_program_name
        filename = self.seq_directory + self.pulse_program_name
        try:
            fobj = open(filename)
            sequence_string = fobj.read()
            fobj.close()
        except:
            raise RuntimeError("Error while loading sequence:" +str(filename))
        #Parse sequence
        ramp_str = ramp_parser.parse_sequence(sequence_string)
        self.logger.debug(ramp_str)
        exec(ramp_str)

#und nu entweder nur n update oder solln wa doch rampen machen!
        self.dac_voltarrays = self.chandler.dac_voltarrays
        self.dac_ramps = self.chandler.dac_ramps
        if self.dac_voltarrays:
            Update_only = True
#nu mach mer Einfach n Update
        else:
            if self.dac_ramps:
#Rampen
                Update_only = False
        return Update_only
        

    def update(self, dac_device, dac_array):
        """Main controlprogram for Electrodes
        """
        for i in self.card_dict:
            if (dac_device[i] == True):
                #                self.timing=dac_timing[i]
#               print "dac filename: "+str(dac_filename)
#                if (dac_filename[i] == False ):
                self.array=dac_array[i]
#                   print "self.array gesetzt"
#                else:
#                    self.filename=dac_filename[i]

#                if (self.timing == 0):
                    #make and start simple static update task(i)
                self.clear_data(i)
                self.stop_card(i)
                self.set_static(i)
                self.start_static_task(i)
#                elif (self.timing == 1):
                    #make and start triggered task(i)
#                    self.clear_data(i)
#                    params=(1,1000000)
#                    self.set_task_parameters(params, i)
#                    self.append_from_file(i)
#                    self.start_triggered_task(i)
#                elif (self.timing > 1):
                    #make and start retriggerable clock task(i) with samplerate self.timing
#                    self.clear_data(i)
#                    params=(1,self.timing)
#                    self.set_task_parameters(params, i)
#                    self.append_from_file(i)
#                    self.start_timed_task(i)



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
