#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-09-16 15:19:43 c704271"

#  file       test.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net


def test_include(test_string, local_chandler=None):
    """This is a test include function
    This funtion generates a 300us pulse on channel nr "15"

    @param test_string: This is a meaningless test string which is
      just printed to stdout
    """
#    global return_str
#    return_str += test_string
#    print test_string
#    print "---------- \n\n\n"
#    print local_chandler.dac_nr_of_samples
    ttl_pulse("15",300, is_last=True)

# test.py ends here

