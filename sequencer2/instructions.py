#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "11-J�n-2010 22:48:47 viellieb"

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


class InsnClass:
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


class nop(InsnClass):
    """No operation
    """
    def __init__(self, val=0x0):
        self.name = "nop"
        self.opcode = 0x0
        self.val = val

    def get_value(self):
        """returns the hex value"""
        return self.opcode << 28 | self.val

    def __str__(self):
        return " add: "+str(self.address) + \
               " -- op:  "+str(hex(self.opcode)) + \
               " -- nam: "+str(self.name) + "  " + \
               " -- val: "+str(hex(self.val))

class halt(InsnClass):
    """stop the processor
    """
    def __init__(self):
        self.name = "halt"
        self.opcode = 0x8

class label(InsnClass):
    """inserts a NOP and a label
    """
    name = "label"
    opcode = 0x0
    def __init__(self, label_name):
        self.label = label_name

    def __str__(self):
        return " add: "+str(self.address) + \
               " -- op:  "+str(hex(self.opcode)) + \
               " -- nam: "+str(self.name) + \
               " -- id: " +str(self.label)

class p(InsnClass):
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
               " -- nam: "+str(self.name) + "    " + \
               " -- sel: "+str(hex(self.change_state)) + \
               " -- val: "+str(hex(self.output_state))

class j(InsnClass):
    """Jumps to a defined label
    """
    is_branch = True
    opcode = 0x4
    name = "j"
    def __init__(self, label_name):
        self.target_name = label_name
        self.target_address = None

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
               " -- nam: "+str(self.name) + "    " + \
               " -- tn: "+str(self.target_name) + "    " + \
               " -- tar: "+str(self.target_address)

class btr(j):
    """Jumps to a defined label if the trigger is satisfied
    trigger is the trigger state in HEX
    """

    name = "btr"
    opcode = 0x3
    def __init__(self, label_name, trigger, invert=False):
        self.target_name = label_name
        self.trigger = trigger
        self.target_address = None
        self.invert = invert

    def get_jump_value(self, target_address):
        self.target_address = target_address
        """returns the hex value for j insns"""
        invert_flag = 0;
        if (self.invert):
          invert_flag = 1 << 18
        return self.opcode << 28 | self.trigger << 19 | target_address | invert_flag

class bdec(j):
    """Decrements the loop register and branches to label"""
    name = "bdec"
    opcode = 0xa
    def __init__(self, label_name, register_address):
        if register_address > 15:
            raise RuntimeError("Register address cannot be greater then 15")
        self.target_name = label_name
        self.register_address = register_address
        self.target_address = None

    def get_jump_value(self, target_address):
        "returns the hex value for bdec insns"
        self.target_address = target_address
        return self.opcode << 28 | self.register_address << 23  | target_address

    def __str__(self):
        return " add: "+str(self.address) + \
               " -- op:  "+str(hex(self.opcode)) + \
               " -- nam: "+str(self.name) + " " + \
               " -- tar: "+str(self.target_address) + \
               " -- reg addr: "+str(self.register_address)

class call(j):
    """ Calls a subroutine
    """
    name = "call"
    opcode = 0x5

    def __str__(self):
        return " add: "+str(self.address) + \
               " -- op:  "+str(hex(self.opcode)) + \
               " -- nam: "+str(self.name) + \
               " -- tar: "+str(self.target_address)

class ret(InsnClass):
    """returns from the last subroutine
    """
    name = "ret"
    opcode = 0x6

    def __str__(self):
        return " add: "+str(self.address) + \
               " -- op:  "+str(hex(self.opcode)) + \
               " -- nam: "+str(self.name)

class wait(InsnClass):
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
               " -- nam: "+str(self.name) + " " + \
               " -- val: "+str(hex(self.wait_cycles))


class ldc(InsnClass):
    "Loads constant into register for bdec"
    name = "load const"
    opcode = 0xb
    def __init__(self, register_addr, value):
        if value > 255:
            raise RuntimeError("Cannot generate a bdec with more than 255 cycles")
        self.register_address = register_addr
        self.value = value

    def get_value(self):
        return self.opcode << 28 | self.register_address << 23 | self.value

    def __str__(self):
        return " add: "+str(self.address) + \
               " -- op:  "+str(hex(self.opcode)) + \
               " -- nam: "+str(self.name) + \
               " -- reg addr: "+str(self.register_address) + \
               " -- val: "+str(hex(self.value))

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
