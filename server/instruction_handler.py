#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-06-02 13:03:08 c704271"

#  file       instruction_handler.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net


"""Defines the high level instructions which are used by functions in user_fucntion.py"""

from transitions import Transitions

class SeqInstruction:
    "Base class used for all intructions"
    duration = 0.0
    start_time = 0.0
    cycle_time = 10e-3
    dac_duration = 3 * cycle_time
    dds_duration = 3 * cycle_time
    is_last = False
    is_added = False
    sequence_var = []

    def add_insn(self, sequence_var, is_last=False):
        "Adds the instructions to the sequence dictionary"
        if self.is_added:
            raise RuntimeError("Instruction can not be added twice")
        sequence_var.append(self)
        self.is_added = True
        return sequence_var

    def get_duration(self):
        "returns the duration of the instruction"
        return self.duration

    def __str__(self):
        return str(self.name) + " | start: " + str(self.start_time) \
            + " | dur: " + str(self.duration) + " | last: " + str(self.is_last)

class TTL_Pulse(SeqInstruction):
    "generates a TTL pulse"
    def __init__(self, start_time, duration, device_key, is_last=True):
        stop_time = start_time + duration
        value_on = []
        value_off = []

        if str(device_key) == device_key:
            device_key = [device_key]

        for item in device_key:
            value_on.append(1)
            value_off.append(0)

        self.start_time = start_time
        self.duration = duration
        self.name = "TTL_Pulse"
        self.is_last = is_last
        self.sequence_var = []

        start_event = TTL_Event(start_time, device_key, value_on, is_last=False)
        stop_event = TTL_Event(stop_time, device_key, value_off, is_last=is_last)

        self.sequence_var = start_event.add_insn(self.sequence_var)
        self.sequence_var = stop_event.add_insn(self.sequence_var)

class RF_Pulse(SeqInstruction):
    "Generates an RF pulse"
    def __init__(self, start_time, theta, phi, ion, transition_obj, \
                     is_last=False, address=0):
        try:
            pulse_duration = transition_obj.t_rabi[ion] * theta
        except KeyError:
            raise RuntimeError("Error while getting Rabi frequency for ion "+str(ion))

        amplitude = transition_obj.amplitude
        if transition_obj.slope_type != "None":
            slope_duration = transition_obj.slope_duration
        else:
            slope_duration = 0
        transition_name = transition_obj.name
        # Missing: global configuration
        cycle_time = self.cycle_time
        dac_switch_time = self.dac_duration
        dds_switch_time = self.dds_duration
        #Switch the DDS on before the DAC
        dds_start_time = start_time
        dac_start_time = start_time + dds_switch_time
        #Switch the DAC of berfore the DDS
        dac_stop_time = dds_start_time + pulse_duration - slope_duration
        dds_stop_time = dac_stop_time + dac_switch_time

        amplitude_off = 0
        print "RF_Pulse not implemented yet :-("
        print "Slope duration: " + str(slope_duration)

        #Let's check if we're using a shaped pulse or not ....
        if slope_duration < cycle_time :
            dac_start_event = DAC_Event(dac_start_time, amplitude, address, is_last=False)
            dac_stop_event = DAC_Event(dac_start_time, amplitude_off, address, is_last=False)
        else:
            dac_start_event = DAC_Shape_Event(dac_start_time, transition_obj, address, \
                                                  rising=True, is_last=False)
            dac_stop_event = DAC_Shape_Event(dac_stop_time, transition_obj, address, \
                                                 rising=False, is_last=False)


        dds_start_event = DDS_Switch_Event(dds_start_time, address, transition_name,\
                                                   phi, is_last=False)
        #The DDS stop event is not working !!!!!
        ############################################################
        dds_stop_event = DDS_Switch_Event(dds_stop_time, address, transition_name,\
                                                   phi, is_last=is_last)
        # Add the events to the sequence
        self.sequence_var = dac_start_event.add_insn(self.sequence_var)
        self.sequence_var = dac_stop_event.add_insn(self.sequence_var)
        self.sequence_var = dds_start_event.add_insn(self.sequence_var)
        self.sequence_var = dds_stop_event.add_insn(self.sequence_var)

class TTL_Event(SeqInstruction):
    "Generates a ttl high or low event"
    def __init__(self, start_time, device_key, value, is_last=True):
        self.val_dict = {}

        for index in range(len(device_key)):
            self.val_dict[device_key[index]] = value[index]
        self.start_time = start_time
        self.device_key = device_key
        self.name = "TTL_Event"
        self.duration = self.cycle_time
        self.is_last = is_last
        self.value = value

    def handle_instruction(self, api):
        api.ttl_set_multiple(self.val_dict)

    def __str__(self):
        return str(self.name) + " start: " + str(self.start_time) \
            + " | dur: " + str(self.duration) + " | last: " + str(self.is_last) \
            + " | key: " +str(self.val_dict)


class DAC_Event(SeqInstruction):
    "Generates a DAC event"
    def __init__(self, start_time, value, address, is_last=True):
        self.start_time = start_time
        self.name = "DAC_Event"
        self.duration = self.cycle_time * 3.0
        self.is_last = is_last
        self.value = value
        self.address = address

    def handle_instruction(self, api):
        api.dac_value(self.address, self.value)

    def __str__(self):
        return str(self.name) + " start: " + str(self.start_time) \
            + " | dur: " + str(self.duration) + " | last: " + str(self.is_last) \
            + " | addr: "+str(self.address) + " | val: "+str(self.value)



class DAC_Shape_Event(SeqInstruction):
    def __init__(self, start_time, transition, dac_address, rising=True, is_last=False , step_nr=200):
        self.start_time = start_time
        self.name = "DAC_Shape_Event"
        self.slope_duration = transition.slope_duration
        self.amplitude = transition.amplitude
        self.is_rising = rising
        self.is_last = is_last
        self.dac_address = dac_address
        # Get the transtion function
        transitions = Transitions()
        try:
            self.shape_func = transitions.trans_dict[transition.slope_type]
        except KeyError:
            raise RuntimeError("Error while getting slope function: "+str(transition.slope_type))
        self.duration = self.slope_duration

        self.step_nr = step_nr
        self.wait_time = (self.slope_duration / self.step_nr * self.cycle_time) - self.dac_duration

    def handle_instruction(self, api):
        for i in range(self.step_nr):
            x = float(i)/float(self.step_nr)
            dac_value = self.shape_func(x, self.is_rising)
            api.dac_value(self.dac_address, dac_value)

    def __str__(self):
        return str(self.name) + " start: " + str(self.start_time) \
            + " | dur: " + str(self.duration) + " | last: " + str(self.is_last) \
            + " | dac_addr: "+str(self.dac_address) + " | ampl: " + str(self.amplitude) \
            + " | slope_dur: "+str(self.slope_duration)


class DDS_Switch_Event(SeqInstruction):
    "Generates a DDS freq switching event"
    def __init__(self, start_time, dds_address, index, phase=0, is_last=False):
        self.start_time = start_time
        self.index = index
        self.phase = phase
        self.is_last = is_last
        self.dds_address = dds_address
        self.name = "DDS_Switch_Event"

    def handle_instruction(self, api):
        try:
            if int(self.index) == self.index:
                real_index = self.index
        except:
            try:
                real_index = api.dds_profile_list[self.index]
            except:
                raise RuntimeError("Transition name not found: "+str(index))
        dds_instance = api.dds_list[self.dds_address]
        api.switch_frequency(dds_instance, real_index, self.phase)

    def __str__(self):
        return str(self.name) + " start: " + str(self.start_time) \
            + " | dur: " + str(self.duration) + " | last: " + str(self.is_last) \
            + " | dds_addr: "+str(self.dds_address) + " | index: "+str(self.index)


# instruction_handler.py ends here
