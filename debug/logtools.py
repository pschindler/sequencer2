#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2009-07-20 13:17:51 c704271"

#  file       logtools.py
#  copyright  (c) Philipp Schindler 2009
#  url        http://pulse-sequencer.sf.net

import logging
import Tkinter, tkFileDialog

LEVEL_DICT = {"ERROR": logging.ERROR,
              "DEBUG": logging.DEBUG,
              "INFO": logging.INFO,
              "WARNING": logging.WARNING}

COLOR_DICT = {
    "ERROR" : ['red', 'blue'],
    "WARNING" : ['yellow', 'red'],
    "INFO" : ['grey', 'red'],
    "DEBUG" : ['white', 'black'],
    None : ['white', 'grey']
    }



def get_color(opcode):
    """Returns the color tuple corresponding to the opcode"""
    try:
        color = COLOR_DICT[opcode]
    except KeyError:
        color = COLOR_DICT[None]
    return color


class AnalyzeLog:
    def __init__(self, filename, level=logging.INFO):
        self.logger_list = ["sequencer2", "api", "server", "DACcontrol"]
        self.level = level
        self.filename = filename


    def load_sequence(self, module=None):
        myfile = self.filename #+  "_all.log.1"
        self.analyze_file(myfile, module)

    def analyze_file(self, myfile, module=None):
        fh = myfile #open(myfile, "r")
        file_str = fh.read()
        line_array = file_str.split("!#")
        log_list = self.analyze_list(line_array, module)
        self.disp = DisplayList(log_list)

    def analyze_list(self, mylist, module=None):
        log_list = []
        for item in mylist:
            item_array = item.split("||")
            try:
                if LEVEL_DICT[item_array[0].strip()] >= self.level:
                    if module != None:
                        if item_array[1].strip() in module:
                            log_list.append(item_array)
                    else:
                        log_list.append(item_array)
            except KeyError:
                pass
        return log_list

    def destroy(self):
        self.disp.destroy()


class DisplayList:
    def __init__(self, myinsn_list):
        self.insn_list = myinsn_list
        self.master = Tkinter.Tk()
        self.scroll = Tkinter.Scrollbar(self.master)
        self.listbox = Tkinter.Listbox(self.master, width=80, height=80) #len(insn_list))
        self.scroll.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
        self.listbox.pack(side=Tkinter.LEFT, fill=Tkinter.Y)
        self.scroll.config(command=self.listbox.yview)
        self.listbox.config(yscrollcommand=self.scroll.set)
        self.listbox.bind("<Double-Button-1>", self.display_insn)
        index = 0

        for item in myinsn_list:
            self.listbox.insert(Tkinter.END, getstring(item))
            color = get_color(item[0].strip())
            self.listbox.itemconfig(index, bg=color[0], fg=color[1])
            index += 1

        Tkinter.mainloop()

    def display_insn(self, info_str):
        """Method is run if an item is double clicked"""
        items = self.listbox.curselection()
        print getstring(self.insn_list[int(items[0])])

    def destroy(self):
        self.master.destroy()

def getstring(list):
    return str(list[0]) + " | " + \
           str(list[1]) + " | " + \
           str(list[2])

class MainGui:
    def __init__(self):
        self.comp_list= ["sequencer2", "api", "server", "DACcontrol"]
        self.level_list = LEVEL_DICT.keys()
        self.master = Tkinter.Tk()
        self.listbox = Tkinter.Listbox(self.master, selectmode=Tkinter.MULTIPLE,
                                       exportselection=0)
        self.listbox.pack()
        for item in self.comp_list:
            self.listbox.insert(Tkinter.END, item)
        self.listbox.select_set(0,3)

        self.level_lb = Tkinter.Listbox(self.master, exportselection=0)
        self.level_lb.pack()
        for item in self.level_list:
            self.level_lb.insert(Tkinter.END, item)
        self.level_lb.select_set(0)
        b1 = Tkinter.Button(self.master, text="select file", command=self.get_file)
        b1.pack()
        b2 = Tkinter.Button(self.master, text="open last log", command=self.open_last)
        b2.pack()
        Tkinter.mainloop()

    def get_file(self, filename=None):
        comp_index = self.listbox.curselection()
        components = []
        for index in comp_index:
            components.append(self.comp_list[int(index)])
        log_index = self.level_lb.curselection()
        log_name = self.level_list[int(log_index[0])]
        log_level = LEVEL_DICT[log_name]

        if filename == None:
            root1 = Tkinter.Tk()
            file1 = tkFileDialog.askopenfile(parent=root1,mode='rb',title='Choose a file')
            self.file = file1
            root1.destroy()
        else:
            self.file = open(filename)
        self.disp_window = AnalyzeLog(self.file, log_level)
        self.disp_window.load_sequence(components)

    def open_last(self):
        filename = "log/sequencer2_all.log.1"
        self.get_file(filename)


if __name__ == "__main__":
    gui = MainGui()




# logtools.py ends here
