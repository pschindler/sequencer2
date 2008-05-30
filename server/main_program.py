#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2008-05-30 13:48:50 c704271"

#  file       main_program.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net
"""Main Program
============

  This module contains the main program lopp which starts the server and invokes
  the user_function methods for sequence parsing and generation

  MainProgram
  -----------
    The class should be invoked as follows:

    >>> var1 = MainProgram()

    This command reads the configuration file and initializes the needed variables

    The server is then started with the command:

    >>> var1.start_server()

    This commands invokes the main_loop method of the server class.

    The main_loop method invokes then the execute_program method of the MainProgram class
    with the command string given from QFP as an argument

    The execute_program method does following tasks with help of the userAPI class:

      - The string is analyzed with the handle_command class
      - The triggers for and from QFP are set in the init_sequence method
      - The sequence is generated with generate_sequence
      - The end sequence ttl channel is set with the end_sequence method
      - The sequence is compiled with the compile_sequence method
      - The sequence is sent to the Box
"""

import logging

from sequencer2 import config
from  sequencer2 import comm

import server
import handle_commands
import user_function
"""This file defines the main_program class for the sequencer2
"""

class ReturnClass:
    "a simple class consisting of two strings"
    def __init__(self):
        self.error_string = ""
        self.return_string = ""

class MainProgram:
    """The MainProgram class
        """

    def __init__(self):
        "sets up the configuration and the logger"
        self.logger = logging.getLogger("server")
        self.config=config.Config()
        self.setup_server()
        self.chandler = handle_commands.CommandHandler()

    def setup_server(self):
        "Reads the configurations and configures the server"
        server_port = self.config.get_int("SERVER","server_port")
        answer = self.config.get_bool("SERVER","server_answer")
        pre_return = self.config.get_bool("SERVER","server_pre_return")
        self.server = server.tcp_Server(port=server_port, answer=answer, pre_return=pre_return)

    def start_server(self):
        "executes the main loop of the server"
        try:
            self.server.main_loop(self.execute_program)
        except:
            self.logger.exception("Error in server main loop")

    def execute_program(self, command_string):
        """This method is called by the main loop of the server
        The argument passed to this method is the command string sent from LabView
        """
        return_var = ReturnClass()
        try:
            self.variable_dict = self.chandler.get_variables(command_string)
        except ValueError, KeyError:
            self.logger.exception("Error while interpreting command string")
            generate_str = "Error while interpreting command string"
            return_var.return_string = generate_str
            return return_var
        # initialize API
        user_api = user_function.userAPI(self.chandler)
        # generate sequence  before loop trigger
        # initialize frequencies
        # Start looping and triggers
        try:
            user_api.init_sequence()
        except:

            self.logger.exception("Error while initializing sequence")
            generate_str = "Error while initializing sequence"
            return_var.return_string = generate_str
            return return_var
        # Generate sequence
        try:
            generate_str = user_api.generate_sequence()
        except:
            self.logger.exception("Error while generating sequence")
            generate_str = "Error while generating sequence"
            return_var.return_string = generate_str
            return return_var
        # end loops and generate IOs for LabView
        user_api.end_sequence()
        # Compile sequence
        try:
            user_api.compile_sequence()
        except:
            self.logger.exception("Error while compiling sequence")
            generate_str = "Error while compiling sequence"
            return_var.return_string = generate_str
            return return_var

        #Send sequence to Box
        try:
            user_api.send_sequence()
        except:
            self.logger.exception("Error while sending sequence")
            generate_str = "Error while sending sequence"

        del(user_api)
        return_var.return_string = generate_str
        return return_var

# main_program.py ends here
