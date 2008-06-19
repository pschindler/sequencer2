#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "14-Jun-2008 15:07:40 viellieb"

#  file       transitions.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net

"""The transition functions are defined here"""

from math import *

def calibrate(x):
    "Calibration to dB"
    if x <= 0 :
        return -100
    if x >= 1:
        return 0
    try:
        y = 10.0 * log(x)
    except OverflowError:
        raise RuntimeError("error while calculating pulse value")
    return y



class Transitions:
    def __init__(self):
        self.trans_dict = {}
        self.trans_dict["sine"] = self.sine_func
        self.trans_dict["blackman"] = self.blackman_func

    def sine_func(self, x, is_rising):
       if is_rising:
           f=sin(x*pi/2)
           return calibrate(f)
       else:
           f=sin(x*pi/2+pi/2)
           return calibrate(f)

    def blackman_func(self, x, is_rising):
        if is_rising:
            f=1.0/2.0*(0.84-cos(x*pi)+0.16*cos(2*x*pi))
            return calibrate(f)
        else:
            f=1.0/2.0*(0.84-cos((x+1)*pi)+0.16*cos(2*(x+1)*pi))
            return calibrate(f)

# transitions.py ends here
