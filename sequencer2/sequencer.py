#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-12-29 11:39:52 c704271"

#  file       sequencer.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://wiki.havens.de
"""Sequencer module with compiling functions
The sequencer conatins a list with the current sequence
The sequencer object handles the compiling of the sequence
"""
import logging
import instructions
import copy
import config

class sequencer:
    """sequener class
    Stores the current sequence in a list:
    Handles the creation of the binary instructions from the
    instructions as defined in L{sequencer2.instructions}
    """
    def __init__(self):
        self.current_sequence = []
        self.jump_list = []
        self.word_list = []
        self.label_dict = {}
        self.sub_list = []
        self.is_subroutine = False
        self.logger = logging.getLogger("sequencer2")
        self.current_output = [0,0,0,0]
        self.bdec_register = []
        # global list for automatically labeling finite loops and stuff like that
        # last element contains the next label which will be used
        self.automatic_label_list = ['aut_label_1']
        self.open_automatic_labels = []

        self.config = config.Config()
        self.branch_delay_slots = self.config.get_int("PCP", "branch_delay_slots")
        self.max_sequence_length = self.config.get_int("PCP", "max_sequence_length")
# This would collide with the subroutine handling :-(
# So we remove it and hope for the best
#        nop_insn = instructions.nop()
#        self.add_insn(nop_insn)
        self.initial_sequence = copy.copy(self.current_sequence)

    def clear(self):
        "just execute the init function"
        self.__init__()

    def get_binary_charlist(self, hex_num, byte_width):
        """hex_char_list(hex_num, byte_width)
        @param hex_num: number to convert into a list of bytes
        @param byte_width: number of bytes to divide hex_num into
        @return: A string representing the lower bytes of hex_num
        """
        i = 0
        datastring = ''
        while i < byte_width:
            datastring = chr(hex_num & 0xff) + datastring
#            datastring = hex(hex_num & 0xff) + datastring
            # Prepend b/c we return in MSB
            hex_num >>= 8
            i += 1
        return datastring


    def add_insn(self, instruction):
        """adds instruction to the current_sequence
        @param instruction: sequencer2.instruction object to add
        """
        self.current_sequence.append(instruction)
        # If insn is a label add it to the label list
        if instruction.label != None:
            self.label_dict[instruction.label] = len(self.current_sequence)-1
        # Set current output for the TTL output system
        if instruction.is_pulse:
            self.current_output[instruction.change_state]=instruction.output_state

    def begin_subroutine(self):
        # checl if the previous subroutine was ended
        if self.is_subroutine:
            self.logger.exception("Previous subroutine not ended")
            raise RuntimeError("Previous subroutine not ended")
        #check if current sequence is empty
        if self.current_sequence != self.initial_sequence:
            self.logger.exception("tried to insert subroutine with a non empty sequence")
            raise RuntimeError("Subroutine can only be started at beginnig of sequence")
        self.is_subroutine = True

    def end_subroutine(self):
        """ends the current subroutine
        appends current_sequence to sub_list
        flushes current_sequence"""
        self.sub_list.append(copy.copy(self.current_sequence))
        self.current_sequence = []
        self.is_subroutine = False

    def compile_sequence(self):
        """generates the binary list
        """
        # Addresses are broken when using subroutines


        # Add a halt instruction to the current sequence !
        halt_insn = instructions.halt()
        self.add_insn(halt_insn)
        nop_insn = instructions.nop()
        for i in range(self.branch_delay_slots):
            self.add_insn(copy.copy(nop_insn))


        sequence_list = self.current_sequence
        word_index = len(self.current_sequence)

        # Add the subroutines to current_sequence
        for insn_list in self.sub_list:
            self.label_dict[insn_list[0].label] = word_index
            sequence_list += insn_list
            word_index += len(insn_list)
        self.word_list = []
        # reset the address counter
        address = 0
        # Append the binary charlist to the word_list
        # If the calue of the insn is None we are dealing
        # with a jump insn and adding it to the jump_list

        for insn in sequence_list:
            # calculate the instruction's machine code as an int
            value = insn.get_value()
            if insn.is_branch == True:
                self.word_list.append(insn)
                self.jump_list.append(len(self.word_list)-1)
            else:
                # Generate a 32bit binary word from value
                self.word_list.append(self.get_binary_charlist(value, 4))
            # set the insn address and increase the address counter
            insn.address = address
            address += 1

        # calculate the addresses for the branch insns in jump_list
        for word_num in self.jump_list:
            jump_insn = self.word_list[word_num]
            try:
                target_num = self.label_dict[jump_insn.target_name]
                target_insn = self.current_sequence[target_num]
                target_address = target_insn.address
                value = jump_insn.get_jump_value(target_address)
                self.word_list[word_num] = self.get_binary_charlist(value, 4)
            except:
                self.logger.exception("error while handling jump: " \
                                          + str(jump_insn.target_name))
        # update current_sequence to make debugging possible
        if len(sequence_list) > self.max_sequence_length - 1:
            raise RuntimeError("Maximum sequence length exceeded: " + \
                                   str(hex(len(sequence_list))))
        self.current_sequence = sequence_list

#        print self.word_list

    def debug_sequence(self, force=False, show_word_list=False):
        """Prints out the current instruction list including the word that is sent to the box
        @param force: Boolean; If set to True, the sequence_list is printed to
                      stdout without taking care of the debug level
        @param show_word_list: Boolean; If True, shows the word that is sent to the box for each instruction
        """
#        logging.basicConfig(level=logging.DEBUG,
#                            format="%(levelname)-10s %(asctime)s %(message)s")
        insn_str = "\n\n"
        for insn in self.current_sequence:
            if show_word_list==False:
                insn_str += str(insn) + "\n"
            else:
                if insn.is_branch==True:
                    insn_str += str(insn) + (71 - len(str(insn)))*' ' + "word: " + hex(insn.get_jump_value(insn.target_address)) + "\n"
                else:
                    insn_str += str(insn) + (71 - len(str(insn)))*' ' + "word: " + hex(insn.get_value()) + "\n"

        self.logger.debug(insn_str)
        if force:
            print(insn_str)


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
