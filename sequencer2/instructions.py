#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "29-Jan-2008 17:33:18 viellieb"

#  file       instructions.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://wiki.havens.de

# Missing insns:
# lp
# pp
# bdec
# ldc

class insn_class():
    """
    Base class for an instruction
    """
    name="None"
    address=None
    label=None
    change_state=None
    opcode=0x0
    output_state=[0,0,0,0]
    def get_value(self):
        return self.opcode << 28
    def __str__(self):
        return " add: "+str(self.address) + \
               " -- op:  "+str(hex(self.opcode)) + \
               " -- nam: "+str(self.name)

class nop(insn_class):
    """
    No operation
    """
    name="nop"
    opcode=0x0

class label(insn_class):
    """
    inserts a NOP and a label
    """
    name="label"
    opcode=0x0
    def __init__(self,label_name):
        self.label=label_name

class p(insn_class):
    """
    The p instruction:
    p.output_state : hex value of the (16bit)
    p.change state : output select bits (2bit)
    """
    name="p"
    opcode=0xc
    def __init__(self,output_state,change_state):
        self.output_state=output_state
        self.change_state=change_state
    def get_value(self):
        if self.change_state!=None:
            return self.opcode << 28 | self.change_state << 16 | self.output_state

    def __str__(self):
        return " add: "+str(self.address) + \
               " -- op:  "+str(hex(self.opcode)) + \
               " -- nam: "+str(self.name) +\
               " -- sel: "+str(hex(self.change_state)) +\
               " -- val: "+str(hex(self.output_state))

class j(insn_class):
    """
    Jumps to a defined label
    """
    opcode=0x4
    name="j"
    def __init__(self,label_name):
        self.target_name=label_name

    def get_value(self):
        return None

    def get_jump_value(self,target_address):
        self.target_address=target_address
        return self.opcode << 28 | target_address
    def __str__(self):
        return " add: "+str(self.address) + \
               " -- op:  "+str(hex(self.opcode)) + \
               " -- nam: "+str(self.name) + \
               " -- tar: "+str(self.target_address)

class btr(j):
    """
    Jumps to a defined label if the trigger is satisfied
    trigge is the trigger state in HEX
    """
    name="btr"
    opcode=0x3
    def __init__(self,label_name,trigger):
        self.target_name=target_name
        self.trigger=trigger

    def get_jump_value(self,target_address):
        return self.opcode << 28 | self.trigger << 19 | target_address

class call(j):
    """
    Calls a subroutine
    """
    name="call"
    opcode=0x5

class ret(insn_class):
    """
    returns from the last subroutine
    """
    name="ret"
    opcode=0x6
##
## instructions.py
## Login : <viellieb@ohm>
## Started on  Mon Jan 28 22:45:26 2008 Philipp Schindler
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


# instructions.py ends here
