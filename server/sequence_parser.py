#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-08-14 09:42:25 c704271"

#  file      : sequence_parser.py
#  email     : philipp DOT schindler AT frog DOT uibk DOT ac DOT at
#            : remove the "green animal"
#  copyright : (c) 2006 Philipp Schindler
#  rcs       : $Id: sequence_parser.py,v 1.2 2006/04/06 11:54:09 viellieb Exp $

"""The sequence parser
Contains a function which extracts the python code from the pseudo XML code.
"""

#_* Code

import logging

def parse_sequence(sequence_string, is_ramp=False):
    "Parses the pseudo XML string and returns the python code as a string"
    logger = logging.getLogger("server")
    current_tag = ""
    sequence_dict = {}
    for line in sequence_string.splitlines():
        try:
            if line[0] == "<":
                current_tag = line
                got_new_tag = True
            if line[0:2] == "</":
                current_tag = ""
                got_new_tag = True
        except IndexError:
            continue
        if current_tag != "" and not got_new_tag:
            try:
                sequence_dict[current_tag] += line+"\n"
            except KeyError:
                sequence_dict[current_tag] = line+"\n"
        got_new_tag = False
    if is_ramp:
        name_list = ["<VARIABLES>", "<RAMP>"]
    else:
        name_list = ["<VARIABLES>", "<TRANSITIONS>", "<SEQUENCE>"]
    return_string = ""
    for item in name_list:
        try:
            return_string += sequence_dict[item]
        except KeyError:
            logger.info("error while getting tag: " + str(item))
    if is_ramp:
        return_string += "setup_ramps()\n"
    return return_string



#_* Local Variables

#  Local Variables:
#  allout-layout: (1 0 :)
#  End:

# sequence_parser.py ends here
