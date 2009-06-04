#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-07-07 12:55:14 c704271"

#  file       test_ipython.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net test

from server import main_program
from sequencer2 import ptplog
import logging

import socket
import time


logger=ptplog.ptplog(level=logging.DEBUG)

cmd_str = "NAME,c:/sequencer2/PulseSequences/protected/PMTreadout.py;CYCLES,1;TRIGGER,NONE;INIT_FREQ,CYCLE;FLOAT,det_time,30.000000;FLOAT,freq729,486.000000;FLOAT,power729,0.000000;FLOAT,gl_cam_time,2000.000000;BOOL,switch729,0;TRANSITION,carrier;RABI,1:1.000000;SLOPE_TYPE,blackman;SLOPE_DUR,0.000000;AMPL,-15.00000;FREQ,10.0;IONS,1:0.000000,2:0.000000,3:0.000000;SWEEP,0.000000;PORT,1;TRANSITION,clock1;RABI,1:1.000000;SLOPE_TYPE,blackman;SLOPE_DUR,0.000000;AMPL,-15.000000;FREQ,0.0;IONS,1:0.000000,2:0.000000,3:0.000000;SWEEP,0.000000;PORT,1;TRANSITION,clock2;RABI,1:6.500000,2:6.500000;SLOPE_TYPE,blackman;SLOPE_DUR,0.000000;AMPL,-15.000000;FREQ,1.0;IONS,1:0.000000,2:0.000000,3:0.000000;SWEEP,0.000000;PORT,1;TTLWORD,750;TTLMASK,32767"




s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
local_ip = socket.gethostbyname(socket.gethostname())
port_of_server = 8880
s.connect((local_ip, port_of_server))

s.sendall(cmd_str)
data = s.recv(4*8192)
print data
data = s.recv(4*8192)
print data
s.close()

