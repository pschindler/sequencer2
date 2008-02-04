#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "03-Feb-2008 17:48:06 viellieb"

#  file       sequencer.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://wiki.havens.de
"""
Sequencer module with compiling functions
"""

import instructions
#import copy
class sequencer():

    def __init__(self):
        self.current_sequence = []
        self.jump_list = []
        self.word_list = []
        self.label_dict = {}
        self.sub_list = []

    def get_binary_charlist(self, hex_num, byte_width):
        """
        hex_char_list(hex_num, byte_width)
        hex_num    = number to convert into a list of bytes
        byte_width = number of bytes to divide hex_num into
        Returns a string representing the lower bytes of hex_num
        """
        i = 0
        datastring = ''
        while i < byte_width:
            datastring = chr(hex_num & 0xff) + datastring
            # Prepend b/c we return in MSB
            hex_num >>= 8
            i += 1
        return datastring


    def add_insn(self, instruction):
        """
        adds instruction to the current_sequence
        """
        self.current_sequence.append(instruction)
        if instruction.label != None:
            self.label_dict[instruction.label] = len(self.current_sequence)-1

    def compile_sequence(self):
        """
        generates the binary list
        """
        # Addresses are broken when using subroutines
        halt_insn = instructions.halt()
        self.add_insn(halt_insn)
        sequence_list = self.current_sequence
        word_index = len(self.current_sequence)
        for insn_list in self.sub_list:
            self.label_dict[insn_list[0].label] = word_index
            sequence_list += insn_list
            word_index += len(insn_list)
        self.word_list = []
        address = 0
        for insn in sequence_list:
            value = insn.get_value()
            if value == None:
                self.word_list.append(insn)
                self.jump_list.append(len(self.word_list)-1)
            else:
                self.word_list.append(self.get_binary_charlist(value, 4))
            insn.address = address
            address += 1
        for word_num in self.jump_list:
            jump_insn = self.word_list[word_num]
            try:
                target_num = self.label_dict[jump_insn.target_name]
                target_insn = self.current_sequence[target_num]
                target_address = target_insn.address
                value = jump_insn.get_jump_value(target_address)
                self.word_list[word_num] = self.get_binary_charlist(value, 4)
            except SyntaxError:
                print "error while handling jump"
        self.current_sequence = sequence_list

    def debug_sequence(self):
        """
        Prints out the current instruction list
        """
        for insn in self.current_sequence:
            print insn


## sequencer.py
## Login : <viellieb@ohm>
## Started on  Mon Jan 28 22:44:57 2008 Philipp Schindler
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


# sequencer.py ends here
