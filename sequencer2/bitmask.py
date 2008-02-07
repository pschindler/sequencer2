#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-02-07 10:07:49 c704271"

#  file       bitmmask.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net

class Bitmask():
    """
    A bitmask class for setting single bits in registers
    """
    def __init__(self, label, width, shift):
        """
        generates the bitmask object
        """
        self.label = label
        self.width = width
        self.shift = shift
        self.value = 0

    def set_value(self, val):
        """
        Sets the value bit
        """
        self.value = val

    def get_value(self):
        """
        Retruns the shifted value
        """
        return self.value << self.shift

# bitmmask.py ends here
