#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-05-30 13:43:18 c704271"

#  file       __init__.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://wiki.havens.de
"""
sequencer2
==========

  sqeuencer2 is the new PCP compiler package

  It is not intended to be used with the old ad9858 dds boards.
  It is designed to work with the ad9910 DDS boards designed in Innsbruck

  Main Classes
  ------------

    - api: The programming interfaces which provides user readeable commands
    - sequencer: Framework for sequence generation and compilation
    - instructions: The machione code commands defintions
    - ad9910: A hardware description class for the ad9910 synthesizer
    - comm: Handles the communication over UDP
    - ptplog: Congiuration of the python logging framework
    - config: general configuration


  Basic usage
  -----------

    >>> import time, logging
    >>> from sequencer2 import sequencer
    >>> from sequencer2 import api
    >>> from sequencer2 import comm
    >>> from sequencer2 import ad9910
    >>> from sequencer2 import ptplog
    >>>
    >>> logger=ptplog.ptplog(level=logging.DEBUG)
    >>> my_sequencer=sequencer.sequencer()
    >>> my_api=api.api(my_sequencer)
    >>> dds_device = ad9910.AD9910(0, 800)
    >>> ptp1 = comm.PTPComm()
    >>>
    >>> #(insert sequence code here)
    >>> # my_api.ttl_value(0xffff , 0)
    >>>
    >>> my_sequencer.compile_sequence()
    >>> ptp1.send_code(my_sequencer.word_list)

  Testing
  -------

    To ensure the functionality of this module a unittest suite is
    located under sequencer2/tests. This tests may be performed with
    the help of the script sequencer2_unittest.py


"""

##
## __init__.py
## Login : <viellieb@ohm>
## Started on  Mon Jan 28 22:58:41 2008 Philipp Schindler
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


# __init__.py ends here
