#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-05-08 11:16:27 c704271"
#  copyright  (c) Philipp Schindler 2008
#  license    GPL (see file COPYING)


import time, logging
from sequencer2 import sequencer
from sequencer2 import api
from sequencer2 import comm
from sequencer2 import ad9910
from sequencer2 import ptplog

# Set to true for testing without actual hardware
nonet = False
# Set to true for enabling the infinite loop
loop_bool = False

time1=time.time()
#Init logger, sequencer, API and DDS
logger=ptplog.ptplog(level=logging.DEBUG)
my_sequencer=sequencer.sequencer()
my_api=api.api(my_sequencer)
dds_device = ad9910.AD9910(0, 800)
##########################################################
# Program start
##########################################################
#Insert label
if loop_bool:
    my_api.label("test")
#send reset opcode to LVDS bus
my_api.ttl_value(0x1f <<  11,0)
my_api.ttl_value(0x1f <<  11 | 1 << 10,0)
my_api.wait(10)
#initialize the DDS
my_api.init_dds(dds_device)
my_api.ttl_value(0x0,0)
#send reset opcode to LVDS bus
my_api.ttl_value(0x1f <<  11,0)
my_api.ttl_value(0x1f <<  11 | 1 << 10,0)

# my_api.wait(1)
# my_api.ttl_value(0x0,0)
# my_api.ttl_value(0x0,1)
# my_api.wait(1)

#set frequency registers
for i in range(8):
    my_api.set_dds_freq(dds_device, 1, i % 8)
#update dds
my_api.update_dds(dds_device)
#Set DAC value
my_api.dac_value(0,2**14-100)
#Reset digital out
my_api.ttl_value(0x0,0)
my_api.ttl_value(0x0,1)
#Wait for 10 000 cycles and jump to label before (aka infinite loop)
my_api.wait(10000)
if loop_bool:
    my_api.jump("test")

######################################################
# Program end
######################################################
#Compile sequence
my_sequencer.compile_sequence()
#Debug sequence
my_sequencer.debug_sequence()
time2=time.time()
logger.logger.info("compile time: "+str(time2-time1))
ptp1 = comm.PTPComm(nonet=nonet)
ptp1.send_code(my_sequencer.word_list)
time3=time.time()
logger.logger.info("ptp time: "+str(time3-time2))
##
## Started on  Mon Jan 28 20:55:07 2008 Philipp Schindler
##
## Copyright (C) 2008 Philipp Schindler
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##


# test_speed.py ends here
