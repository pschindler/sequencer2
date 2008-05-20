#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-05-20 14:12:31 c704271"

#  file       instruction_handler.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net



# class SequenceClass:
#     def __init__(self):
#         self.sequence_dict = {}
#         self.current_time = 0.0
#         self.is_last_max_time = 0.0

"""Defines the high level instructions"""
class SeqInstruction:
    "Base class used for all intructions"
    duration = 0.0
    start_time = 0.0
    cycle_time = 10.0
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

#         #Calculate the real start time
#         real_time = self.start_time
#         #Ad the insn to the dictionary
#         if not sequence_var.sequence_dict.has_key(real_time):
#             sequence_var.sequence_dict[real_time] = []
#         sequence_var.sequence_dict[real_time].append(self)
#         # Time managment
#         if self.start_time + self.get_duration() > sequence_var.is_last_max_time:
#             sequence_var.is_last_max_time = self.start_time + self.get_duration()
#         if is_last:
#             sequence_var.current_time += sequence_var.current_time \
#                 + sequence_var.is_last_max_time
#             sequence_var.is_last_max_time = 0.0
#         #Return the sequence variable
#         self.start_time = real_time
#         self.is_added = True
#         return sequence_var

    def get_duration(self):
        "returns the duration of the instruction"
        return self.duration

    def get_seq(self, sequence_var):
        return self.sequence_var

    def __str__(self):
        return str(self.name) + " start: " + str(self.start_time) \
            + " dur: " + str(self.duration) + " last: " + str(self.is_last)

class TTL_Pulse(SeqInstruction):
    "generates a TTL pulse"
    def __init__(self, start_time, duration, device_key, is_last=True):
        stop_time = start_time + duration
        self.start_time = start_time
        self.duration = duration
        self.name = "TTL_Pulse"
        self.is_last = is_last
        self.sequence_var = []

        start_event = TTL_Event(start_time, device_key, is_last=False)
        stop_event = TTL_Event(stop_time, device_key, is_last=is_last)
        self.sequence_var = start_event.add_insn(self.sequence_var)
        self.sequence_var = stop_event.add_insn(self.sequence_var)

class TTL_Event(SeqInstruction):
    "Generates a ttl high or low event"
    def __init__(self, start_time, device_key, is_last=True):
        self.start_time = start_time
        self.device_key = device_key
        self.name = "TTL_Event"
        self.duration = self.cycle_time
        self.is_last = is_last

# instruction_handler.py ends here
