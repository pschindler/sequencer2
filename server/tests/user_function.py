#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "07-Jul-2008 23:49:56 viellieb"

#  file       user_function.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net

import unittest
import time
import logging


from sequencer2 import sequencer
from sequencer2 import api

from server import main_program
from server import instruction_handler
from server import sequence_handler
from server import handle_commands
from server import user_function


def generate_cmd_str(filename, nr_of_car=1):
    data = "NAME,"+filename+";CYCLES,10;TRIGGER,YES;"
    data += "FLOAT,det_time,25000.0;"
    for index in range(nr_of_car):
        data += "TRANSITION,carrier" + str(index + 1) + ";FREQ,150.0;RABI,1:23,2:45,3:12"
        data += ";SLOPE_TYPE,blackman;"
        data += "SLOPE_DUR,0;IONS,1:201,2:202,3:203"
        data += ";FREQ2,10;AMPL2,1;"
    return data


class TestUserFunction(unittest.TestCase):
    def test_execute_program(self):
        cmd_str = generate_cmd_str("test_sequence.py", nr_of_car=2)
        my_main_program = main_program.MainProgram()
        return_var = my_main_program.execute_program(cmd_str)
        if return_var.is_error:
            self.fail(return_var.return_string)

    def test_sequence_files(self):
        "Simple test for error handling of an unknown sequence file"
        cmd_str = "NAME,PMTreadoutgibtsnit.py;CYCLES,1;TRIGGER,YES;"
        my_main_program = main_program.MainProgram()
        my_main_program.execute_program(cmd_str)

    def test_nr_carrier_nr(self):
        "Test how many transitions the server can handle"
        cmd_str = generate_cmd_str("test_sequence.py", nr_of_car=9)
        my_main_program = main_program.MainProgram()
        return_var = my_main_program.execute_program(cmd_str)
        if return_var.is_error:
            self.fail(return_var.return_string)

    def test_pulse_shaping(self):
        "Test if the shaping works at all"
        trans_obj = sequence_handler.transition("1", 0, 2, amplitude=-3, \
                                                slope_duration=10.0, slope_type="sine")
        my_sequencer=sequencer.sequencer()
        my_api = api.api(my_sequencer)
        ihandler = instruction_handler.DACShapeEvent(0,trans_obj,1, step_nr=10)
        ihandler.handle_instruction(my_api)
        my_sequencer.debug_sequence()

    def test_bichro_pulse(self):
        "Test the bichromatic pulse"
        cmd_str = generate_cmd_str("test_bichro_sequence.py", nr_of_car=5)
        my_main_program = main_program.MainProgram()
        return_var = my_main_program.execute_program(cmd_str)
        if return_var.is_error:
            self.fail(return_var.return_string)

    def test_conflict_handler(self):
        "Test the conflict handler"
        from server.user_function import *
        from server.instruction_handler import *
        fobj = open("server/user_function.py")
        sequence_string = fobj.read()
        fobj.close()
        seq_list = sequence_string.split("#--1")

#        exec(seq_list[1])

        command_string = generate_cmd_str("test_sequence.py", 4)
        chandler = handle_commands.CommandHandler()
        variable_dict = chandler.get_variables(command_string)
        user_api = user_function.userAPI(chandler, dds_count=3)

        incl_list = user_api.include_handler.generate_include_list()
        for file_name, cmd_str in incl_list:
            exec(cmd_str)
        transitions = chandler.transitions
        sequence_var = []
        pulse1 = TTLPulse(0, 10, "1", is_last=False)
        pulse2 = TTLPulse(0, 10, "2", is_last=False)
        pulse3 = TTLPulse(0, 30, "3")
        sequence_var.append(pulse1.sequence_var)
        sequence_var.append(pulse2.sequence_var)
        sequence_var.append(pulse3.sequence_var)
        user_api.final_array = user_api.get_sequence_array(sequence_var)
        ttl_ev1 = user_api.final_array[0]
        for item in user_api.final_array:
            print item
        print ttl_ev1.device_key
        assert ttl_ev1.device_key == ["3","2","1"]
        ttl_ev2 = user_api.final_array[1]
        print ttl_ev2


#------------------------------------------------------------------------------
# Collect all test suites for running
all_suites = unittest.TestSuite((
  unittest.makeSuite(TestUserFunction)
  ))

def run():
  unittest.TextTestRunner(verbosity=2).run(all_suites)


# user_function.py ends here
