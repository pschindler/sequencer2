#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-07-07 12:55:14 c704271"

#  file       test_ipython.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net test

from server.user_function import *
from server import handle_commands
from sequencer2 import ptplog



def generate_cmd_str(filename, nr_of_car=1):
    data = "NAME,"+filename+";CYCLES,10;TRIGGER,YES;"
    data += "FLOAT,det_time,25000.0;"
    for index in range(nr_of_car):
        data += "TRANSITION,carrier" + str(index + 1) + ";FREQ,150.0;RABI,1:23,2:45,3:12"
        data += ";SLOPE_TYPE,blackman;"
        data += "SLOPE_DUR,0;IONS,1:201,2:202,3:203"
        data += ";FREQ2,10;AMPL2,1;"
    return data

logger=ptplog.ptplog(level=logging.DEBUG)

fobj = open("server/user_function.py")
sequence_string = fobj.read()
fobj.close()
seq_list = sequence_string.split("#--1")
exec(seq_list[1])

command_string = generate_cmd_str("test_sequence.py", 4)
chandler = handle_commands.CommandHandler()
variable_dict = chandler.get_variables(command_string)
user_api = userAPI(chandler, dds_count=3)

incl_list = user_api.include_handler.generate_include_list()
for file_name, cmd_str in incl_list:
    exec(cmd_str)

global transitions
transitions = chandler.transitions
global sequence_var
sequence_var = []
#user_api.init_sequence()



# test_ipython.py ends here
