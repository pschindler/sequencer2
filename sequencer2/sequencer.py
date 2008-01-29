#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-01-29 14:21:20 c704271"

#  file       sequencer.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://wiki.havens.de
import sequencer2.instructions
import copy
class sequencer():

    def __init__(self):
        self.current_sequence=[]
        self.jump_list=[]
        self.word_list=[]
        self.label_dict={}

    def get_binary_charlist(self,hex_num,byte_width):
        """
        hex_char_list(hex_num, byte_width)
        hex_num    = number to convert into a list of bytes
        byte_width = number of bytes to divide hex_num into
        Returns a string representing the lower bytes of hex_num
        """
        i = 0
        datastring = ''
        while i < byte_width:
            datastring = chr(hex_num & 0xff) + datastring # Prepend b/c we return in MSB
            hex_num >>= 8
            i += 1
        return datastring


    def add_insn(self,instruction):
        """
        adds instruction to the current_sequence
        """
        self.current_sequence.append(instruction)
        if instruction.label != None:
            self.label_dict[instruction.label]=len(self.current_sequence)-1

    def compile_sequence(self):
        """
        generates the binary list
        """
        self.word_list=[]
        address=0
        for insn in self.current_sequence:
            value=insn.get_value()
            if value==None:
                self.word_list.append(insn)
                self.jump_list.append(len(self.word_list)-1)
            else:
                self.word_list.append(self.get_binary_charlist(value,4))
            insn.address=address
            address+= 1
        for word_num in self.jump_list:
            jump_insn=self.word_list[word_num]
            try:
                target_num=self.label_dict[jump_insn.target_name]
                target_insn=self.current_sequence[target_num]
                target_address=target_insn.address
                value=jump_insn.get_jump_value(target_address)
                self.word_list[word_num]=self.get_binary_charlist(value,4)
            except SyntaxError:
                print "error while handling jump"

    def debug_sequence(self):
        for insn in self.current_sequence:
            print insn

    def dac_value(self,dac_nr,val):
        """
        simple example for a DAC event
        """
        addr_insn=sequencer2.instructions.p()
        addr_insn.change_state=3
        addr_insn.output_state=dac_nr << 12
        self.add_insn(addr_insn)
        data_insn=sequencer2.instructions.p()
        data_insn.change_state=0
        data_insn.opcode=0x7
        data_insn.output_state=val << 2
        self.add_insn(data_insn)
        data2_insn=copy.copy(data_insn)
        data2_insn.output_state=val << 2 | 2
        self.add_insn(data2_insn)

    def ttl_value(self,value):
        """
        simple example for a TTL event
        """
        ttl_insn=sequencer2.instructions.p()
        ttl_insn.change_state=2
        ttl_insn.output_state=value
        self.add_insn(ttl_insn)

    def label(self,label_name):
        """
        inserts a label and a NOP
        """
        label_insn=sequencer2.instructions.label(label_name)
        self.add_insn(label_insn)

    def jump(self,target_name):
        """
        jumps to label
        """
        jump_insn=sequencer2.instructions.j(target_name)
        nop_insn=sequencer2.instructions.nop()
        self.add_insn(jump_insn)
        self.add_insn(nop_insn)
        self.add_insn(nop_insn)
        self.add_insn(nop_insn)
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
