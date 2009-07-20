#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2009-06-03 15:05:33 c704271"

#  file       analyze.py
#  copyright  (c) Philipp Schindler 2009
#  url        http://pulse-sequencer.sf.net


"""
analyze.py

Analyzes a binary machine code file for the pcp32 processor.
For more information visit http://pulse-programmer.org

TODO

- Search for the difference in two files (use difflib)
- Address offset / start address for comparison

"""

import struct
import Tkinter
import sys
import optparse
import difflib
import pprint


def Denary2Binary(n):
    '''convert denary integer n to binary string bin_str'''
    bin_str = ''
    if n < 0:
        raise ValueError, "must be a positive integer"
    if n == 0:
        return '0'
    while n > 0:
        bin_str = str(n % 2) + bin_str
        n = n >> 1
    bin_str2 = ""
    for n1 in range(len(bin_str)):
        if n1 % 4 == 0:
            bin_str2 += "|"
        bin_str2 += bin_str[len(bin_str) - n1 - 1]
    return bin_str2[::-1]

def generic_get_description(value):
    """Move on, nothing to see yet"""
    return str(hex(value))

def btr_get_description(value):
    """get description for a btr insn"""
    trig_state = value >> 19
    output_val = value - (trig_state << 19)
    return_var =  "trig: " + str(hex(trig_state)) + " - tar: " + str(hex(output_val))
    return return_var

def p_get_description(value, old_box=True):
    """get description for a pulse insn"""
    select_state = value >> 16
    output_val = value - (select_state << 16)
    sel_dict = {0: "DAC data",
                1: "DDS data/addr",
                2: "Digi out",
                3: "chainboard addr"}
    if old_box:
        val_str = sel_dict[select_state]
        if select_state == 2:
            out_str = Denary2Binary(output_val)
        else:
            out_str = str(hex(output_val))
        val_str = " - val: " + val_str + " - val " + out_str
    else:
        val_str = "sel: " + str(hex(select_state)) + " - val: " + str(hex(output_val))
    return_var = val_str
    return return_var

def lp_get_description(value):
    """get description for a load pulse insn"""
    myaddress = value >> 23
    value = value - (myaddress << 23)
    wren = value >> 22
    value = value -(wren << 22)
    addend = value >> 21
    value = value - (addend << 21)
    select = value >> 16
    value = value - (select << 16)
    output_val = value
    return_var = "addr:" +str(hex(myaddress)) + " - wren: "+str(wren)
    return_var += " - af: " +str(addend)
    return_var += " - sel: " + str(select) + " - val: " + str(hex(output_val))
    return return_var

class InsnInfo:
    """Class for storing information over an instruction
    the get_description method may be adapted to give beter information
    for each opcode"""

    def __init__(self, opcode, name, description_function=None):
        self.opcode = opcode
        self.name = name
        if description_function == None:
            self.get_description = generic_get_description
        else:
            self.get_description = description_function

INSTR_DICT = {
    0 : InsnInfo(0,"nop"),
    3 : InsnInfo(3,"btr",btr_get_description),
    4 : InsnInfo(4,"j"),
    5 : InsnInfo(5,"call"),
    6 : InsnInfo(6,"return"),
    8 : InsnInfo(8,"halt"),
    9 : InsnInfo(9,"wait"),
    10 : InsnInfo(10,"bdec"),
    11 : InsnInfo(11,"ldc"),
    12 : InsnInfo(12,"p",p_get_description),
    13 : InsnInfo(13,"pp"),
    14 : InsnInfo(14,"lp",lp_get_description)
    }


DIFF_COLOR_DICT = {
    " " : ['white', 'black'],
    "+" : ['red', 'blue'],
    "-" : ['yellow', 'black'],
    "?" : ['green' , 'black'],
    None : ['white', 'black']
    }



COLOR_DICT = {
    0 : ['white', 'grey'],
    3 : ['red', 'blue'],
    4 : ['red', 'black'],
    5 : ['yellow', 'black'],
    6 : ['yellow', 'blue'],
    8 : ['blue' , 'grey'],
    9 : ['green' , 'black'],
    10 : ['red' , 'green'],
    12 : ['lightgrey', 'black'],
    13 : ['lightgrey', 'red'],
    14 : ['lightgrey', 'blue'],
    None : ['white', 'black']
    }

def get_color(opcode):
    """Returns the color tuple corresponding to the opcode"""
    try:
        color = COLOR_DICT[opcode]
    except KeyError:
        color = COLOR_DICT[None]
    return color


def get_int_list(myfilename):
    """Returns a list of integer corresponding to the machine code """
    filehandle = open(myfilename,'rb')
    bin_str = filehandle.read()
    filehandle.close()
    length = len(bin_str) / 4
    myint_list = struct.unpack("!"+str(length)+"L", bin_str[:length*4])
    return myint_list


def write_str_list(my_list, myfilename):
    """Writes the instruction list to a file"""
    int_str = ""
    for item in my_list:
        int_str += "\n" + str(item)
    filehandle = open(myfilename,'w')
    filehandle.write(int_str)
    filehandle.close()

class Instruction:
    """Instruction class"""
    def __init__(self, int_machinecode, myaddress=None):
        self.machinecode = int_machinecode
        self.opcode = None
        self.value = None
        self.description = None
        self.address = myaddress
        self.name = None
        self.analyze_instr()

    def analyze_instr(self):
        """extracts the opcode and the name"""
        self.opcode = self.machinecode >> 28
        try:
            self.name = INSTR_DICT[self.opcode].name
        except KeyError:
            self.name = "unknown "+str(self.opcode)
        self.value = self.machinecode - (self.opcode << 28)
        try:
            self.description = INSTR_DICT[self.opcode].get_description(self.value)
        except KeyError:
            self.description = "unknown"

    def __str__(self):
        return str(hex(self.address)) + " | " + self.name  \
               + " | " + self.description

class DisplayInsnList:
    """Make a nice graphical frontend with beautiful colors"""
    def __init__(self, myinsn_list, is_diff=False):
        """Displays the list in an Tkinter window """
        self.insn_list = myinsn_list
        self.master = Tkinter.Tk()
        self.scroll = Tkinter.Scrollbar(self.master)
        self.listbox = Tkinter.Listbox(self.master, width=50, height=80) #len(insn_list))
        self.scroll.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
        self.listbox.pack(side=Tkinter.LEFT, fill=Tkinter.Y)
        self.scroll.config(command=self.listbox.yview)
        self.listbox.config(yscrollcommand=self.scroll.set)
        self.listbox.bind("<Double-Button-1>", self.display_insn)
        index = 0
        if not is_diff:
            for item in myinsn_list:
                self.listbox.insert(Tkinter.END, str(item))
                color = get_color(item.opcode)
                self.listbox.itemconfig(index, bg=color[0], fg=color[1])
                index += 1
        else:
            for item in myinsn_list:
                if item[0] != "?":
                    self.listbox.insert(Tkinter.END, str(item))
                    color = DIFF_COLOR_DICT[item[0]]
                    self.listbox.itemconfig(index, bg=color[0], fg=color[1])
                    index += 1

        Tkinter.mainloop()

    def display_insn(self, info_str):
        """Method is run if an item is double clicked"""
        items = self.listbox.curselection()
        print self.insn_list[int(items[0])]

if __name__ == "__main__":

    usage_str = "usage: analyze.py [options] file1 [file2]"
    parser = optparse.OptionParser(usage_str)
    parser.add_option("-d", action = "store_true", default=False,
                      help = "calculate difference between two files")
    parser.add_option("-u", action = "store_true", default=False,
                      help = "show unified diff")
    parser.add_option("-H", action = "store_true", default=False,
                      help = "generate html file for diff")
    parser.add_option("-g", action = "store_true", default=False,
                      help = "Do not open graphical user interface")
    (options, args) = parser.parse_args()

    if len(args) == 0:
        parser.print_help()
        sys.exit(1)

    all_lists = []
    file_list = []
    for filename in args:
        print("analyzing " + filename)
        int_list = get_int_list(filename)
        insn_list = []
        address = 0

        insn_str=""

        for int_code in int_list:
            instr = None
            instr = Instruction(int_code, address)
            insn_list.append(instr)
            address += 1
        all_lists.append(insn_list)
        file_list.append(filename)
        write_str_list(insn_list,filename + ".txt")

    if options.d:
        print "difference between"
        str1 = []
        str2 = []
        for item in all_lists[0]:
            str1.append(str(item)+"\n")
        for item in all_lists[1]:
            str2.append(str(item)+"\n")
        if options.u and options.g:
            diff = difflib.unified_diff(str1, str2, file_list[0], file_list[1])
            sys.stdout.writelines(diff)
        elif options.H and options.g:
            diff = difflib.HtmlDiff().make_file(str1, str2, file_list[0], file_list[1])
            fh = open("diff.html",'w')
            fh.write(diff)
            fh.close()
        else:
            diff = difflib.Differ()
            result = list(diff.compare(str1, str2))
            pprint.pprint(result)
            insn_list = result
    if not options.g:
        DisplayInsnList(insn_list, options.d)

# analyze.py ends here
