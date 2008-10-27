#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-07-21 16:16:35 c704271"

#  file       rf_setup.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net

"""
We define two dictionaries for settings related to the RF setup

  offset: Frequency offset

  multiplier: Frequency multiplier

"""



offset = {}
multiplier = {}

#This is for Ca43 right now:
offset["729"] = 0
multiplier["729"] = 1

offset["Raman"] = 0
multiplier["Raman"] = 1

offset["RF"] = 285.0
multiplier["RF"] = 1



# rf_setup.py ends here
