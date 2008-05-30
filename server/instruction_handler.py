#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-05-30 13:09:38 c704271"

#  file       instruction_handler.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net


"""Defines the high level instructions which are used by functions in user_fucntion.py"""

class SeqInstruction:
    "Base class used for all intructions"
    duration = 0.0
    start_time = 0.0
    cycle_time = 10e-3
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

        amplitude = int(transition_obj.amplitude)
        transition_name = transition_obj.name

        cycle_time = 1e-2
        dac_switch_time = 3.0*cycle_time
        dds_switch_time = 3.0*cycle_time
        dac_start_time = start_time
        dds_start_time = start_time + dac_switch_time
        dds_stop_time = dds_start_time + pulse_duration
        dac_stop_time = dds_stop_time + dds_switch_time

        amplitude_off = 0
        print "RF_Pulse not implemented yet :-("

        dac_start_event = DAC_Event(dac_start_time, amplitude, address, is_last=False)
        dds_start_event = DDS_Switch_Event(start_time, address, transition_name,\
                                               phi, is_last=False)
        dac_stop_event = DAC_Event(dac_start_time, amplitude_off, address, is_last=is_last)
        self.sequence_var = dac_start_event.add_insn(self.sequence_var)
        self.sequence_var = dds_start_event.add_insn(self.sequence_var)
        self.sequence_var = dac_stop_event.add_insn(self.sequence_var)

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
