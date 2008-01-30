#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "30-Jan-2008 23:10:36 viellieb"

#  file       api.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://wiki.havens.de

# Missing: subroutine handling

from exceptions import *
import instructions
import copy

class api():
    def __init__(self,sequencer):
        self.sequencer=sequencer
        self.is_subroutine=False

    def dac_value(self,dac_nr,val):
        """
        simple example for a DAC event
        """
        #insert the chainboard address event
        addr_insn=instructions.p(dac_nr << 12,3)
        self.sequencer.add_insn(addr_insn)
        #Set the data bus
        data_insn=instructions.p(val << 2,0)
        self.sequencer.add_insn(data_insn)
        #Set the WRB
        data2_insn=copy.copy(data_insn)
        data2_insn.output_state=val << 2 | 2
        self.sequencer.add_insn(data2_insn)

    def ttl_value(self,value):
        """
        simple example for a TTL event
        """
        ttl_insn=instructions.p(value,2)
        self.sequencer.add_insn(ttl_insn)

    def label(self,label_name):
        """
        inserts a label and a NOP
        """
        label_insn=instructions.label(label_name)
        self.sequencer.add_insn(label_insn)

    def jump(self,target_name):
        """
        jumps to label
        """
        jump_insn=instructions.j(target_name)
        nop_insn=instructions.nop()
        self.sequencer.add_insn(jump_insn)
        self.sequencer.add_insn(nop_insn)
        self.sequencer.add_insn(copy.copy(nop_insn))
        self.sequencer.add_insn(copy.copy(nop_insn))

    def jump_trigger(self,target_name,trigger):
        """
        branch on trigger
        Adds a conditional jump
        trigger : trigger state in hex
        """
        jump_insn=instructions.btr(target_name,)
        nop_insn=instructions.nop()
        self.sequencer.add_insn(jump_insn)
        self.sequencer.add_insn(nop_insn)
        self.sequencer.add_insn(copy.copy(nop_insn))
        self.sequencer.add_insn(copy.copy(nop_insn))

    def begin_subroutine(self,label_name):
        if self.is_subroutine:
            raise RuntimeError, "Previous subroutine not ended"
        if self.sequencer.current_sequence!=[]:
            raise RuntimeError, "Subroutine can only be started at beginnig of sequence"
        self.sequencer.add_insn(instructions.label(label_name))

    def end_subroutine(self):
        self.sequencer.add_insn(instructions.ret())
        self.sequencer.sub_list.append(copy.copy(self.sequencer.current_sequence))
        self.sequencer.current_sequence=[]

    def call_subroutine(self,label_name):
        call_insn=instructions.call(label_name)
        nop_insn=instructions.nop()
        self.sequencer.add_insn(call_insn)
        self.sequencer.add_insn(nop_insn)
        self.sequencer.add_insn(copy.copy(nop_insn))
        self.sequencer.add_insn(copy.copy(nop_insn))

##
## api.py
## Login : <viellieb@ohm>
## Started on  Tue Jan 29 17:15:37 2008 Philipp Schindler
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


# api.py ends here
