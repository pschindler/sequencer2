#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-06-02 11:26:55 c704271"

#  file       transitions.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net

"""The transition functions are defined here"""

from math import *

class Transitions:
    def __init__(self):
        self.trans_dict = {}
        self.trans_dict["sine"] = self.sine_func
        self.trans_dict["blackman"] = self.blackman_func

    def sine_func(self, x, is_rising):
       if is_rising:
           f=sin(x*pi/2)
           return f
       else:
           f=sin(x*pi/2+pi/2)
           return f

    def blackman_func(self, x, is_rising):
        if is_rising:
            f=1.0/2.0*(0.84-cos(x*pi)+0.16*cos(2*x*pi))
            return f
        else:
            f=1.0/2.0*(0.84-cos((x+1)*pi)+0.16*cos(2*(x+1)*pi))
            return f

# transitions.py ends here
