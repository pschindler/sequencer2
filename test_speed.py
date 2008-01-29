#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "29-Jan-2008 00:24:53 viellieb"

#  file       test_speed.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://wiki.havens.de
#  license    GPL (see file COPYING)


import time
from  sequencer2 import sequencer

time1=time.time()
my_sequencer=sequencer.sequencer()
N0=10
my_sequencer.dac_value(12,1)
my_sequencer.jump("test")
for i in range(N0):
    my_sequencer.dac_value(N0,1)
my_sequencer.label("test")
my_sequencer.compile_sequence()
if N0 < 100:
    my_sequencer.debug_sequence()
#    print my_sequencer.word_list
time2=time.time()
print str(time2-time1)
print N0
##
## test_speed.py
## Login : <viellieb@ohm>
## Started on  Mon Jan 28 20:55:07 2008 Philipp Schindler
## $Id$
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
