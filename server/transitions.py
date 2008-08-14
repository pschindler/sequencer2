#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-08-13 09:59:11 c704271"

#  file       transitions.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net
#pylint: disable-msg = W0614
"""The transition functions are defined here"""

from math import *

def calibrate(value):
    "Calibration to dB"
    if value <= 0 :
        return -100
    if value >= 1:
        return 0
    try:
        result = 10.0 * log(value)
    except OverflowError:
        raise RuntimeError("error while calculating pulse value")
    return result



class ShapeForms:
    """Class containing all avaliable pulse shapes
    The shapes are stored in the dictionary trans_dict
    The dictionary items are methods which accept the value between  0 and 1
    and a boolean determining wheter a rising or falling slope is performed
    """
    def __init__(self):
        self.trans_dict = {}
        self.trans_dict["sine"] = self.sine_func
        self.trans_dict["blackman"] = self.blackman_func

    def sine_func(self, value, is_rising):
        "A sinusoidal shape"
        if is_rising:
            lin_result = sin(value*pi/2)
            return calibrate(lin_result)
        else:
            lin_result = sin(value*pi/2+pi/2)
            return calibrate(lin_result)

    def blackman_func(self, value, is_rising):
        "The standard Blackman shape"
        if is_rising:
            lin_result = 1.0/2.0*(0.84-cos(value*pi)+0.16*cos(2*value*pi))
            return calibrate(lin_result)
        else:
            lin_result = 1.0/2.0*(0.84-cos((value+1)*pi)+0.16*cos(2*(value+1)*pi))
            return calibrate(lin_result)

# transitions.py ends here
