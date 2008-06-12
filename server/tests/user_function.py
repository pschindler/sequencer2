#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-06-12 15:16:17 c704271"

#  file       user_function.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net

import unittest
import time
import logging

from server import main_program
from server import handle_commands
from server import user_function


def generate_cmd_str(filename, nr_of_car=1):
    data="NAME,"+filename+";CYCLES,10;TRIGGER,YES;"
    for index in range(nr_of_car):
        data += "TRANSITION,carrier" + str(index + 1) + ";FREQ,150.0;RABI,1:23,2:45,3:12"
        data += ";SLOPE_TYPE,blackman;"
        data += "SLOPE_DUR,0;IONS,1:201,2:202,3:203"
        data += ";FREQ2,10;AMPL2,1;"
    return data


class TestUserFunction(unittest.TestCase):
    def test_execute_program(self):
        cmd_str = generate_cmd_str("PMTreadout.py", nr_of_car=2)
        my_main_program = main_program.MainProgram()
        my_main_program.execute_program(cmd_str)

    def test_sequence_files(self):
        "Simple test for error handling of an unknown sequence file"
        cmd_str = "NAME,PMTreadoutgibtsnit.py;CYCLES,1;TRIGGER,YES;"
        my_main_program = main_program.MainProgram()
        my_main_program.execute_program(cmd_str)

    def test_nr_carrier_nr(self):
        "Test how many transitions the server can handle"
        cmd_str = generate_cmd_str("PMTreadout.py", nr_of_car=9)
        my_main_program = main_program.MainProgram()
        my_main_program.execute_program(cmd_str)

#------------------------------------------------------------------------------
# Collect all test suites for running
all_suites = unittest.TestSuite((
  unittest.makeSuite(TestUserFunction)
  ))

def run():
  unittest.TextTestRunner(verbosity=2).run(all_suites)


# user_function.py ends here
