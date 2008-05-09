#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-05-09 09:41:26 c704271"

#  file       instructions.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://wiki.havens.de
"""The instruction set for the PCP
"""
# Missing insns:
# lp
# pp
# bdec
# ldc


class insn_class():
    """Base class for an instruction
    """
    label = None
    address = None
    is_branch = False
    is_pulse = False

    def __init__(self):
        self.name = "None"
#        self.change_state = None
        self.opcode = 0x0
#        self.output_state = [0, 0, 0, 0]


    def get_value(self):
        """returns the hex value"""
        return self.opcode << 28
    def __str__(self):
        return " add: "+str(self.address) + \
               " -- op:  "+str(hex(self.opcode)) + \
               " -- nam: "+str(self.name)


class nop(insn_class):
    """No operation
    """
    def __init__(self):
        self.name = "nop"
        self.opcode = 0x0

class halt(insn_class):
    """stop the processor
    """
    def __init__(self):
        self.name = "halt"
        self.opcode = 0x8

class label(insn_class):
    """inserts a NOP and a label
    """
    name = "label"
    opcode = 0x0
    def __init__(self, label_name):
        self.label = label_name

class p(insn_class):
    """The p instruction:
    p.output_state : hex value of the (16bit)
    p.change state : output select bits (2bit)
    """

    def __init__(self, output_state, change_state):
        self.name = "p"
        self.opcode = 0xc
        self.output_state = output_state
        self.change_state = change_state
        self.is_pulse = True

    def get_value(self):
        """returns the hex value"""
        if self.change_state != None:
            return self.opcode << 28 | self.change_state << 16 | self.output_state

    def __str__(self):
        return " add: "+str(self.address) + \
               " -- op:  "+str(hex(self.opcode)) + \
               " -- nam: "+str(self.name) +\
               " -- sel: "+str(hex(self.change_state)) +\
               " -- val: "+str(hex(self.output_state))

class j(insn_class):
    """Jumps to a defined label
    """
    is_branch = True
    opcode = 0x4
    name = "j"
    def __init__(self, label_name):
        self.target_name = label_name

    def get_value(self):
        """returns the hex value"""
        return None

    def get_jump_value(self, target_address):
        """returns the hex value for j insns"""
        self.target_address = target_address
        return self.opcode << 28 | target_address
    def __str__(self):
        return " add: "+str(self.address) + \
               " -- op:  "+str(hex(self.opcode)) + \
               " -- nam: "+str(self.name) + \
               " -- tar: "+str(self.target_address)

class btr(j):
    """Jumps to a defined label if the trigger is satisfied
    trigge is the trigger state in HEX
    """

    name = "btr"
    opcode = 0x3
    def __init__(self, label_name, trigger):
        self.target_name = label_name
        self.trigger = trigger

    def get_jump_value(self, target_address):
        """returns the hex value for j insns"""
        return self.opcode << 28 | self.trigger << 19 | target_address

class call(j):
    """ Calls a subroutine
    """
    name = "call"
    opcode = 0x5

class ret(insn_class):
    """returns from the last subroutine
    """
    name = "ret"
    opcode = 0x6

class wait(insn_class):
    """inserts a wait insn
    """
    name = "wait"
    opcode = 0x9
    def __init__(self, wait_cycles):
        self.wait_cycles = wait_cycles

    def get_value(self):
        return self.opcode << 28 | self.wait_cycles

    def __str__(self):
        return " add: "+str(self.address) + \
               " -- op:  "+str(hex(self.opcode)) + \
               " -- nam: "+str(self.name) + \
               " -- val: "+str(hex(self.wait_cycles))

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
