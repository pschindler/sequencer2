#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "26-Aug-2008 22:13:48 viellieb"

#  file       instruction_handler.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net


"""Defines the high level instructions which are used by
functions in user_fucntion.py"""

from transitions import ShapeForms
from  sequencer2 import config

import logging
import copy

GLOBAL_CONFIG = config.Config()
GLOBAL_REFERENCE = GLOBAL_CONFIG.get_float("SERVER","reference_frequency")
GLOBAL_CLK_DIVIDER = GLOBAL_CONFIG.get_float("SERVER","clk_divider")

GLOBAL_CONFIG.get_all_dict("Durations")
GLOBAL_GET_DURATION = GLOBAL_CONFIG.get_float_dict_val

class SeqInstruction:
    "Base class used for all intructions"
    duration = 0.0
    start_time = 0.0
    cycle_time = 1 / GLOBAL_REFERENCE * GLOBAL_CLK_DIVIDER
    get_hardware_duration = GLOBAL_GET_DURATION
    is_last = False
    is_added = False
    sequence_var = []
    name = "generic Instruction"
    max_name_length = 20

    def add_insn(self, sequence_var):
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
        return str(self.name) + (self.max_name_length-len(self.name))*" " + " | start: " + str(self.start_time) \
            + " | dur: " + str(self.duration) + " | last: " + str(self.is_last)

    def resolve_conflict(self, other_item):
        "By default no conflict is resolved"
        return False




class DDSSweep(SeqInstruction):
    """Programs the DDS Digital Ramp Generator Registers
    ramp_type = 'freq', 'ampl', 'phase'
    the non-ramped parameters will be taken from the current profile settings
    """
    def __init__(self, ramp_type, time_array, slope_array, dds_address, transitions, phi, dfreq_pos, dfreq_neg, lower_limit, upper_limit, dt_pos, dt_neg, loop_counts, is_last):

        self.sequence_var = []

        dac_switch_time = self.get_hardware_duration("dac_duration")
        dds_switch_time = self.get_hardware_duration("dds_duration")
        # Init the logger
        self.logger = logging.getLogger("server")
#        self.logger.debug("Switching frequency to: "+str(transitions))
        # Extract the transition object and the pulse duration
        try:
            transition_obj = transitions[transitions.current_transition]
        except KeyError:
            raise RuntimeError("Transition name not found: " + \
                                   str(transitions.current_transition))
            
        self.logger.debug("Switching frequency to: "+str(transition_obj))
            
        # Set the real phase
        phi = transition_obj.get_phase(phi)
        transition_name = transition_obj.name
        # Set the Amplitudes
        amplitude = transition_obj.amplitude
        amplitude_off = -100.0
        # Set the slope duration
        slope_duration = 0
        # Set the start and stop times
        # Switch the DDS on before the DAC
        drg_prg_time = time_array[0]
        drg_start_time = drg_prg_time + 3*self.cycle_time
        dds_start_time = drg_start_time + 3*self.cycle_time
        dac_start_time = dds_start_time + dds_switch_time
        drg_conf_time = [dac_start_time + dac_switch_time]
        for k in range(1, len(time_array)-1):
            drg_conf_time.append(drg_conf_time[0] + time_array[k])
       # Switch the DAC of berfore the DDS
        dac_stop_time = drg_conf_time[len(drg_conf_time)-1] + time_array[len(time_array)-1] + 3*self.cycle_time
        dds_stop_time = dac_stop_time + dac_switch_time

        drg_stop_time = dds_stop_time + dds_switch_time

        # if dt_pos/neg=0. then take the lowest value possible
        if dt_pos==0:
            dt_pos = 4.0/GLOBAL_CONFIG.get_float("SERVER","reference_frequency")
        if dt_neg==0:
            dt_neg = 4.0/GLOBAL_CONFIG.get_float("SERVER","reference_frequency")




        program_ramp_gen_event = ProgramRampGeneratorEvent(ramp_type, drg_prg_time, dds_address, dfreq_pos, dfreq_neg, lower_limit, upper_limit, dt_pos, dt_neg, is_last=False)
        
        start_dds_ramp_event = StartRampGeneratorEvent(drg_start_time, dds_address, loop_counts, is_last=False)        

        conf_ramp_event = []
        for k in range(len(drg_conf_time)):
            conf_ramp_event.append(ConfigureRampEvent(drg_conf_time[k], dds_address, slope_array[k], is_last=False))

        stop_dds_ramp_event = StopRampGeneratorEvent(drg_stop_time, dds_address, loop_counts, is_last)

        # initializing rest parameters
        dac_start_event = DACEvent(dac_start_time, amplitude, dds_address, is_last=False)
        dac_stop_event  = DACEvent(dac_stop_time, amplitude_off, dds_address, is_last=False)
        dds_start_event = DDSSwitchEvent(dds_start_time, dds_address, transition_name, phi,  is_last=False)
        dds_stop_event  = DDSSwitchEvent(dds_stop_time, dds_address, "NULL", phi, is_last=is_last)
 




        self.sequence_var = program_ramp_gen_event.add_insn(self.sequence_var)
        
        self.sequence_var = start_dds_ramp_event.add_insn(self.sequence_var)
        
        self.sequence_var = dds_start_event.add_insn(self.sequence_var)
        self.sequence_var = dac_start_event.add_insn(self.sequence_var)

        for k in range(len(time_array)-1):
            self.sequence_var = conf_ramp_event[k].add_insn(self.sequence_var)


        self.sequence_var = dac_stop_event.add_insn(self.sequence_var)
        self.sequence_var = dds_stop_event.add_insn(self.sequence_var)

        self.sequence_var = stop_dds_ramp_event.add_insn(self.sequence_var)
 
 
class Start_Finite(SeqInstruction):
    """at the beginning of a finite loop
    adds a ldc instruction and a label intruction
    @param target_name:  String identifier of the label to jump to
    @param loop_count: Desired number of loops
    """
    def __init__(self, target_name, loop_counts=1, automatic_label=False):
        self.target_name = target_name
        self.loop_counts = loop_counts
        self.automatic_label = automatic_label
        self.start_time = 0.0
        self.duration = self.cycle_time
        self.is_last = True        
        self.name = "StartLoopEvent"
        self.sequence_var = []
        self.sequence_var = self.add_insn(self.sequence_var)

    def handle_instruction(self, api):
        api.start_finite(self.target_name, self.loop_counts, self.automatic_label)

    def __str__(self):
        return str(self.name) + (self.max_name_length-len(self.name))*" " + " | start: " + str(self.start_time) \
            + " | cnt: " + str(self.loop_counts) + " | last: " + str(self.is_last)

class End_Finite(SeqInstruction):
    """At the ending of a finite loop
    Adds a bdec instruction and fills the branch delay slots
    @param target_name:  String identifier of the label to jump to
    """
    def __init__(self, target_name, automatic_label=False):
        self.target_name = target_name
        self.automatic_label = automatic_label
        self.start_time = 0.0
        self.duration = self.cycle_time
        self.is_last = True
        self.name = "EndLoopEvent"
        self.sequence_var = []
        self.sequence_var = self.add_insn(self.sequence_var)

    def handle_instruction(self, api):
        api.end_finite(self.target_name, self.automatic_label)

    def __str__(self):
        return str(self.name) + (self.max_name_length-len(self.name))*" " + " | start: " + str(self.start_time) \
            + " | last: " + str(self.is_last)

class SeqWait(SeqInstruction):
    "generates a waiting time from a certain (optional) start time"
    def __init__(self, wait_time, start_time=0.0, is_last=True):
        self.duration = float(wait_time)
        self.start_time = float(start_time)
        self.is_last = is_last
        self.name = "WaitEvent"
        self.sequence_var = []
        self.sequence_var = self.add_insn(self.sequence_var)

    def handle_instruction(self, api):
        "does nothing"
        api.wait(self.duration)

    def __str__(self):
        return str(self.name) + (self.max_name_length-len(self.name))*" " + " | start: " + str(self.start_time) \
            + " | dur: " + str(self.duration) + " | last: " + str(self.is_last)

class RFOn(SeqInstruction):
    "Switches on a given DDS"
    def __init__(self, start_time, frequency, amplitude, address, is_last=True):
        self.start_time = float(start_time)
        self.duration = self.cycle_time
        self.frequency = float(frequency)
        self.amplitude = float(amplitude)
        self.dds_address = address
        self.is_last = is_last
        self.name = "RFOnEvent"

        self.sequence_var = []
        self.sequence_var = self.add_insn(self.sequence_var)

    def handle_instruction(self, api):
        """Creates following events:
         - dac
         - set_dds_freq
         - set_dds_profile
         - update_dds
         """
        try:
            dds_instance = api.dds_list[self.dds_address]
        except IndexError:
            raise RuntimeError("DDS not found: "+str(self.dds_address))
        api.dac_value(self.amplitude, self.dds_address)
        api.set_dds_freq(dds_instance, self.frequency, profile=0)
        api.set_dds_profile(dds_instance, profile=0)
        api.update_dds(dds_instance)

    def __str__(self):
        return str(self.name) + (self.max_name_length-len(self.name))*" " \
               + " | start: " + str(self.start_time) \
               + " | freq: "  + str(self.frequency) \
               + " | amp: "   + str(self.amplitude) \
               + " | add: "   + str(self.dds_address) \
               + " | last: "  + str(self.is_last)

class TTLOn(SeqInstruction):
    "generates a TTL pulse"
    def __init__(self, start_time, device_key, is_last=True):
        start_time = float(start_time)
        duration = self.cycle_time

        if str(device_key) == device_key:
            device_key = [device_key]

        self.start_time = float(start_time)
        self.duration = self.cycle_time
        self.name = "TTL_On"
        self.is_last = is_last
        self.sequence_var = []

        start_event = TTLEvent(start_time, device_key, [1], is_last=False)

        self.sequence_var = []
        self.sequence_var = start_event.add_insn(self.sequence_var)

class TTLOff(SeqInstruction):
    "generates a TTL pulse"
    def __init__(self, start_time, device_key, is_last=True):
        start_time = float(start_time)
        duration = self.cycle_time

        if str(device_key) == device_key:
            device_key = [device_key]

        self.start_time = float(start_time)
        self.duration = self.cycle_time
        self.name = "TTL_Off"
        self.is_last = is_last
        self.sequence_var = []

        start_event = TTLEvent(start_time, device_key, [0], is_last=False)

        self.sequence_var = []
        self.sequence_var = start_event.add_insn(self.sequence_var)



class TTLPulse(SeqInstruction):
    "generates a TTL pulse"
    def __init__(self, start_time, duration, device_key, is_last=True):
        start_time = float(start_time)
        duration = float(duration)
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

        start_event = TTLEvent(start_time, device_key, value_on, is_last=False)
        stop_event = TTLEvent(stop_time, device_key, value_off, is_last=is_last)

        self.sequence_var = []
        self.sequence_var = start_event.add_insn(self.sequence_var)
        self.sequence_var = stop_event.add_insn(self.sequence_var)

class RFPulse(SeqInstruction):
    "Generates an RF pulse"
    def __init__(self, start_time, theta, phi, ion, transitions, \
                     is_last=False, address=0):

        cycle_time = self.cycle_time
        dac_switch_time = self.get_hardware_duration("dac_duration")
        dds_switch_time = self.get_hardware_duration("dds_duration")
        # Init the logger
        self.logger = logging.getLogger("server")
#        self.logger.debug("Switching frequency to: "+str(transitions))
        # Extract the transition object and the pulse duration
        try:
            transition_obj = transitions[transitions.current_transition]
        except KeyError:
            raise RuntimeError("Transition name not found: " + \
                                   str(transitions.current_transition))

            
        self.logger.debug("Switching frequency to: "+str(transition_obj))
            
        # Set the real phase
        phi = transition_obj.get_phase(phi)
        try:
            pulse_duration = transition_obj.t_rabi[ion] * theta
        except KeyError:
            raise RuntimeError("Error while getting Rabi frequency for ion "+str(ion))
        transition_name = transition_obj.name
        # Set the Amplitudes
        amplitude = transition_obj.amplitude
        amplitude_off = -100.0
        # Set the slope duration
        if transition_obj.slope_type != "None":
            slope_duration = transition_obj.slope_duration
        else:
            slope_duration = 0
        # Set the start and stop times
        # Switch the DDS on before the DAC
        dds_start_time = start_time
        dac_start_time = start_time + dds_switch_time
        # Switch the DAC of berfore the DDS
        dac_stop_time = dds_start_time + pulse_duration - slope_duration
        dds_stop_time = dac_stop_time + dac_switch_time


        # Let's check if we're using a shaped pulse or not ....
        if slope_duration < cycle_time :
            # We're a rectangular pulse
            dac_start_event = DACEvent(dac_start_time, amplitude, \
                                            address, is_last=False)
            dac_stop_event = DACEvent(dac_stop_time, amplitude_off, \
                                           address, is_last=False)
        else:
            # We're a shaped pulse
            dac_start_event = DACShapeEvent(dac_start_time, transition_obj, \
                                                  address, rising=True, is_last=False)
            dac_stop_event = DACShapeEvent(dac_stop_time, transition_obj, \
                                                 address, rising=False, is_last=False)
        # The DDS start event
        dds_start_event = DDSSwitchEvent(dds_start_time, address, transition_name, \
                                                   phi,  is_last=False)
        #The DDS stop event switches to a zero frequency
        dds_stop_event = DDSSwitchEvent(dds_stop_time, address, "NULL", \
                                                   phi, is_last=is_last)
        # Add the events to the sequence
        self.sequence_var = []
        self.sequence_var = dac_start_event.add_insn(self.sequence_var)
        self.sequence_var = dac_stop_event.add_insn(self.sequence_var)
        self.sequence_var = dds_start_event.add_insn(self.sequence_var)
        self.sequence_var = dds_stop_event.add_insn(self.sequence_var)


class RFBichroPulse(SeqInstruction):
    "Generates an RF pulse"
    def __init__(self, start_time, theta, phi, ion, transitions, \
                 is_last=False, address=0, address2=1):

        self.logger = logging.getLogger("server")
        self.logger.debug("Switching frequency to: "+str(transitions))

        try:
            transition_obj = transitions[transitions.current_transition]
            transition_obj2 = transitions[transitions.transition2_name]
        except KeyError:
            raise RuntimeError("Bichro Pulse Transition name not found: " + \
                                   str(transitions.current_transition))
        # Set the real phase
        phi = transition_obj.get_phase(phi)
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
        transition2_name = transition_obj2.name
        # Missing: global configuration
        cycle_time = self.cycle_time
        dac_switch_time = self.get_hardware_duration("dac_duration")
        dds_switch_time = self.get_hardware_duration("dds_duration")
        #Switch the DDS on before the DAC
        dds_start_time = start_time
        dds_start_time2 = start_time + dds_switch_time
        dac_start_time = start_time + 2 * dds_switch_time
        #Switch the DAC of berfore the DDS
        dac_stop_time = dds_start_time + pulse_duration - slope_duration
        dds_stop_time = dac_stop_time + dac_switch_time
        dds_stop_time2 = dac_stop_time + dac_switch_time + dds_switch_time
        amplitude_off = 0

        #Let's check if we're using a shaped pulse or not ....
        if slope_duration < cycle_time :
            dac_start_event = DACEvent(dac_start_time, amplitude, \
                                            address, is_last=False)
            dac_stop_event = DACEvent(dac_stop_time, amplitude_off, \
                                           address, is_last=False)
        else:
            dac_start_event = DACShapeEvent(dac_start_time, transition_obj, \
                                                  address, rising=True, is_last=False)
            dac_stop_event = DACShapeEvent(dac_stop_time, transition_obj, \
                                                 address, rising=False, is_last=False)

        dds_start_event = DDSSwitchEvent(dds_start_time, address, transition_name, \
                                                   phi,  is_last=False)
        dds_start_event2 = DDSSwitchEvent(dds_start_time2, address2, transition2_name, \
                                                   phi,  is_last=False)
        #The DDS stop event switches to a zero frequency
        dds_stop_event = DDSSwitchEvent(dds_stop_time, address, "NULL", \
                                        phi, is_last=False)
        dds_stop_event2 = DDSSwitchEvent(dds_stop_time2, address2, "NULL", \
                                         phi, is_last=is_last)
        # Add the events to the sequence
        self.sequence_var = []
        self.sequence_var = dac_start_event.add_insn(self.sequence_var)
        self.sequence_var = dac_stop_event.add_insn(self.sequence_var)
        self.sequence_var = dds_start_event.add_insn(self.sequence_var)
        self.sequence_var = dds_stop_event.add_insn(self.sequence_var)
        self.sequence_var = dds_start_event2.add_insn(self.sequence_var)
        self.sequence_var = dds_stop_event2.add_insn(self.sequence_var)




       


  



# Actual Events Follow Here


class TTLEvent(SeqInstruction):
    "Generates a ttl high or low event"
    def __init__(self, start_time, device_key, value, is_last=True):
        self.val_dict = {}

        for index in range(len(device_key)):
            self.val_dict[device_key[index]] = value[index]
        self.start_time = start_time
        self.device_key = copy.copy(device_key)
        self.name = "TTLEvent"
        self.duration = self.cycle_time
        self.is_last = is_last
        self.value = value

    def handle_instruction(self, api):
        "generate an API event"
        api.ttl_set_multiple(self.val_dict)

    def resolve_conflict(self, other_item):
        "We can combine two TTL Events"
        if other_item.name != "TTLEvent":
            return None
        for test_key in self.device_key:
            if other_item.device_key.count(test_key) > 0:
                raise RuntimeError ("Cannot switch same TTL channel simultaniously: "\
                                    +str(test_key))
        self.val_dict.update(other_item.val_dict)
        self.device_key += other_item.device_key
        return True

    def __str__(self):
        return str(self.name) + (self.max_name_length-len(self.name))*" " + " | start: " + str(self.start_time) \
            + " | dur: " + str(self.duration) + " | last: " + str(self.is_last) \
            + " | key: " +str(self.val_dict)


class DACEvent(SeqInstruction):
    "Generates a DAC event"
    def __init__(self, start_time, value, address, is_last=True):
        self.start_time = start_time
        self.name = "DACEvent"
        self.duration = self.cycle_time * 3.0
        self.is_last = is_last
        self.value = value
        self.address = address

    def handle_instruction(self, api):
        "generate an API event"
        api.dac_value(self.value, self.address)

    def __str__(self):
        return str(self.name) + (self.max_name_length-len(self.name))*" " + " | start: " + str(self.start_time) \
            + " | dur: " + str(self.duration) + " | last: " + str(self.is_last) \
            + " | addr: "+str(self.address) + " | val: "+str(self.value)



class DACShapeEvent(SeqInstruction):
    "A simple shaped DAC pulse"
    def __init__(self, start_time, transition, dac_address, rising=True, is_last=False , step_nr=100):
        self.start_time = start_time
        self.name = "DAC_Shape_Event"
        self.slope_duration = float(transition.slope_duration)
        self.amplitude = transition.amplitude
        self.is_rising = rising
        self.is_last = is_last
        self.dac_address = dac_address
        # Get the transtion function
        transitions = ShapeForms()
        try:
            self.shape_func = transitions.trans_dict[transition.slope_type]
        except KeyError:
            raise RuntimeError("Error while getting slope function: "+str(transition.slope_type))
        self.duration = self.slope_duration
        self.step_nr = step_nr
        #calculate the waiting time in between two steps
        self.wait_time = self.slope_duration / float(self.step_nr) \
                         - self.get_hardware_duration("dac_duration") * self.cycle_time
        # Check if we need to decrease the step count
        if self.wait_time < 0:
            self.wait_time = 0
            self.step_nr = int(self.slope_duration / self.get_hardware_duration("dac_duration"))

    def handle_instruction(self, api):
        "generate API events"
        for i in range(self.step_nr):
            x = float(i)/float(self.step_nr)
            dac_value = self.shape_func(x, self.is_rising) + self.amplitude
            api.dac_value(dac_value, self.dac_address)
            if self.wait_time > 0:
                api.wait(self.wait_time)

    def __str__(self):
        return str(self.name) + (self.max_name_length-len(self.name))*" " + " | start: " + str(self.start_time) \
            + " | dur: " + str(self.duration) + " | last: " + str(self.is_last) \
            + " | dac_addr: "+str(self.dac_address) + " | ampl: " + str(self.amplitude) \
            + " | slope_dur: "+str(self.slope_duration)


class DDSSwitchEvent(SeqInstruction):
    "Generates a DDS freq switching event"
    def __init__(self, start_time, dds_address, index, phase=0, is_last=False):
        self.start_time = start_time
        self.duration = self.cycle_time * 3.0
        self.index = index
        self.phase = phase
        self.is_last = is_last
        self.dds_address = dds_address
        self.name = "DDS_Switch_Event"

    def handle_instruction(self, api):
        "generate API events"
        # We have to check if the index is a string or an integer
        try:
            if int(self.index) == self.index:
                real_index = self.index
        except:
            try:
                real_index = api.dds_profile_list[self.index]
            except KeyError:
                raise RuntimeError("Transition name not found: "+str(self.index))
        # Get the right dds object
        try:
            dds_instance = api.dds_list[self.dds_address]
        except IndexError:
            raise RuntimeError("No DDS known with address: "+str(self.dds_address))
        api.switch_frequency(dds_instance, real_index, self.phase)

    def __str__(self):
        return str(self.name) + (self.max_name_length-len(self.name))*" " + " | start: " + str(self.start_time) \
            + " | dur: " + str(self.duration) + " | last: " + str(self.is_last) \
            + " | dds_addr: "+ str(self.dds_address) + " | index: "+ str(self.index) + " | phase: "+ str(self.phase)




class ProgramRampGeneratorEvent(SeqInstruction):
    "Programs the ramp generator"
    def __init__(self, ramp_type, start_time, dds_address, dfreq_pos, dfreq_neg, lower_limit, upper_limit, dt_pos, dt_neg, is_last=False):
        self.start_time = start_time
        self.duration = self.cycle_time
        self.dt_pos = dt_pos
        self.dt_neg = dt_neg
        self.dfreq_pos = dfreq_pos
        self.dfreq_neg = dfreq_neg
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.ramp_type = ramp_type
        self.is_last = is_last
        self.dds_address = dds_address
        self.name = "PrgRampGen_Event"

    def handle_instruction(self, api):
        "generate API events"
       # Get the right dds object
        try:
            dds_instance = api.dds_list[self.dds_address]
        except IndexError:
            raise RuntimeError("No DDS known with address: "+str(self.dds_address))
        api.init_digital_ramp_generator(self.ramp_type, dds_instance, self.dt_pos, self.dt_neg, self.dfreq_pos, self.dfreq_neg, self.lower_limit, self.upper_limit)


    def __str__(self):
        return str(self.name) + (self.max_name_length-len(self.name))*" " + " | start: " + str(self.start_time) \
            + " | dur: " + str(self.duration) + " | last: " + str(self.is_last) \
            + " | dds_addr: "+ str(self.dds_address) \
            + " | rmp_type: "+ self.ramp_type \
            + " | dt_pos: "+ str(self.dt_pos) \
            + " | dt_neg: "+ str(self.dt_neg) \
            + " | dfreq_pos: "+ str(self.dfreq_pos) \
            + " | dfreq_neg: "+ str(self.dfreq_neg) \
            + " | lwr_limit: "+ str(self.lower_limit) \
            + " | upr_limit: "+ str(self.upper_limit)


class ConfigureRampEvent(SeqInstruction):
    "Configures the ramp"
    def __init__(self, start_time, dds_address, slope_direction, is_last=False):
        self.start_time = start_time
        self.duration = self.cycle_time
        self.is_last = is_last
        self.dds_address = dds_address
        self.name = "ConfRamp_Event"
        self.slope_direction = slope_direction

    def handle_instruction(self, api):
        "generate API events"
       # Get the right dds object
        try:
            dds_instance = api.dds_list[self.dds_address]
        except IndexError:
            raise RuntimeError("No DDS known with address: "+str(self.dds_address))
        api.configure_ramping(dds_instance, self.slope_direction)

    def __str__(self):
        return str(self.name) + (self.max_name_length-len(self.name))*" " + " | start: " + str(self.start_time) \
            + " | dur: " + str(self.duration) + " | last: " + str(self.is_last) \
            + " | dds_addr: "+ str(self.dds_address) \
            + " | slp: "+ str(self.slope_direction)



class StartRampGeneratorEvent(SeqInstruction):
    "Programs the ramp generator"
    def __init__(self, start_time, dds_address, loop_counts, is_last=False):
        self.start_time = start_time
        self.duration = self.cycle_time
        self.is_last = is_last
        self.dds_address = dds_address
        self.loop_counts = loop_counts
        self.name = "StartRampGen_Event"

    def handle_instruction(self, api):
        "generate API events"
       # Get the right dds object
        try:
            dds_instance = api.dds_list[self.dds_address]
        except IndexError:
            raise RuntimeError("No DDS known with address: "+str(self.dds_address))
        api.start_digital_ramp_generator(dds_instance)

        if self.loop_counts>0:
            api.start_finite('', self.loop_counts, automatic_label=True)

    def __str__(self):
        return str(self.name) + (self.max_name_length-len(self.name))*" " + " | start: " + str(self.start_time) \
            + " | dur: " + str(self.duration) + " | last: " + str(self.is_last) \
            + " | dds_addr: "+ str(self.dds_address) + " | loop_cnts: "+ str(self.loop_counts)


class StopRampGeneratorEvent(SeqInstruction):
    "Programs the ramp generator"
    def __init__(self, start_time, dds_address, loop_counts, is_last=False):
        self.start_time = start_time
        self.duration = self.cycle_time
        self.is_last = is_last
        self.dds_address = dds_address
        self.loop_counts = loop_counts
        self.name = "StopRampGen_Event"

    def handle_instruction(self, api):
        "generate API events"
       # Get the right dds object
        try:
            dds_instance = api.dds_list[self.dds_address]
        except IndexError:
            raise RuntimeError("No DDS known with address: "+str(self.dds_address))
        if self.loop_counts>0:
            api.end_finite('', automatic_label=True)
        api.stop_digital_ramp_generator(dds_instance)

    def __str__(self):
        return str(self.name) + (self.max_name_length-len(self.name))*" " + " | start: " + str(self.start_time) \
            + " | dur: " + str(self.duration) + " | last: " + str(self.is_last) \
            + " | dds_addr: "+ str(self.dds_address) \








# instruction_handler.py ends here
