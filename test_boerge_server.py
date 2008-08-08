#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-07-07 12:55:14 c704271"

#  file       test_ipython.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net test

from server import main_program
from sequencer2 import ptplog
import logging

logger=ptplog.ptplog(level=logging.DEBUG)



cmd_str = "NAME,C:/ExperimentControl_Current/new qfp config/PulseSequences/protected/PMTreadout.py;CYCLES,1;TRIGGER,NONE;INIT_FREQ,CYCLE;FLOAT,det_time,100000.000000;FLOAT,freq729,486.000000;FLOAT,power729,0.000000;FLOAT,gl_cam_time,2000.000000;BOOL,switch729,0;TRANSITION,PumpBoost;RABI,1:1.000000,2:0.000000;SLOPE_TYPE,blackman;SLOPE_DUR,0.000000;AMPL,0.000000;FREQ,480.000000;IONS,1:0.000000,2:0.000000,3:0.000000;SWEEP,0.000000;PORT,1;TRANSITION,transfer1;RABI,1:14.800000,2:0.000000;SLOPE_TYPE,blackman;SLOPE_DUR,0.000000;AMPL,-40.000000;FREQ,489.056710;IONS,1:0.000000,2:0.000000,3:0.000000;SWEEP,0.000000;PORT,2;TRANSITION,transfer2;RABI,1:100.000000,2:0.000000;SLOPE_TYPE,blackman;SLOPE_DUR,5.000000;AMPL,-17.500000;FREQ,489.051710;IONS,1:0.000000,2:0.000000,3:0.000000;SWEEP,0.000000;PORT,3;TRANSITION,sb_cooling;RABI,1:1.000000;SLOPE_TYPE,blackman;SLOPE_DUR,0.000000;AMPL,0.000000;FREQ,493.675390;IONS,1:0.000000,2:0.000000,3:0.000000;SWEEP,0.000000;PORT,1;TRANSITION,sb_cooling_2;RABI,1:1.000000,2:0.000000;SLOPE_TYPE,blackman;SLOPE_DUR,0.000000;AMPL,-9.000000;FREQ,494.570390;IONS,1:0.000000,2:0.000000,3:0.000000;SWEEP,0.000000;PORT,1;TRANSITION,shelve1;RABI,1:8.600000;SLOPE_TYPE,blackman;SLOPE_DUR,0.000000;AMPL,-35.000000;FREQ,489.057910;IONS,1:0.000000,2:0.000000,3:0.000000;SWEEP,0.000000;PORT,2;TRANSITION,shelve2;RABI,1:7.900000;SLOPE_TYPE,blackman;SLOPE_DUR,0.000000;AMPL,-35.000000;FREQ,489.057910;IONS,1:0.000000,2:0.000000,3:0.000000;SWEEP,0.000000;PORT,2;TRANSITION,red_sb;RABI,1:400.000000;SLOPE_TYPE,blackman;SLOPE_DUR,0.000000;AMPL,-30.000000;FREQ,494.562390;IONS,1:0.000000,2:0.000000,3:0.000000;SWEEP,0.000000;PORT,1;TRANSITION,blue_sb;RABI,1:125.000000;SLOPE_TYPE,blackman;SLOPE_DUR,40.000000;AMPL,-35.000000;FREQ,497.023835;IONS,1:0.000000,2:0.000000,3:0.000000;SWEEP,0.000000;PORT,2;TRANSITION,sb_cooling_3;RABI,1:1.000000;SLOPE_TYPE,blackman;SLOPE_DUR,0.000000;AMPL,-90.000000;FREQ,494.560390;IONS,1:0.000000,2:0.000000,3:0.000000;SWEEP,0.000000;PORT,1;TRANSITION,carrier;RABI,1:42.200000;SLOPE_TYPE,blackman;SLOPE_DUR,0.000000;AMPL,-50.000000;FREQ,489.056710;IONS,1:0.000000,2:0.000000,3:0.000000;SWEEP,0.000000;PORT,2;TRANSITION,clock1;RABI,1:9.000000,2:9.000000;SLOPE_TYPE,blackman;SLOPE_DUR,0.000000;AMPL,0.000000;FREQ,489.056710;IONS,1:0.000000,2:0.000000,3:0.000000;SWEEP,0.000000;PORT,1;TRANSITION,clock2;RABI,1:6.500000,2:6.500000;SLOPE_TYPE,blackman;SLOPE_DUR,0.000000;AMPL,-10.000000;FREQ,495.792690;IONS,1:0.000000,2:0.000000,3:0.000000;SWEEP,0.000000;PORT,1;TTLWORD,16402;TTLMASK,32767"





# cmd_str = generate_cmd_str("test_bichro_sequence.py", nr_of_car=5)
 
my_main_program = main_program.MainProgram()
 
return_var = my_main_program.execute_program(cmd_str)
 
#if return_var.is_error:
#    self.fail(return_var.return_string)

