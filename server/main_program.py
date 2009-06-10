#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2009-06-10 16:09:43 c704271"

#  file       main_program.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net
# pylint: disable-msg = W0702
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

import server
import handle_commands
import user_function
#import dac_function #DAC

class ReturnClass:
    """Class for returning strings to LabView
    return_string : Return string without error
    error_string: Return string when an error occurred
    is_error: Bollean which indicates that an error occurred """
    def __init__(self):
        self.error_string = ""
        self.return_string = ""
        self.is_error = False

    def error(self, error_string="Undefined Error"):
        "Method which sets the attributes if an error occurred"
        self.is_error = True
        self.error_string = error_string
        self.return_string = error_string

class MainProgram:
    """The MainProgram class
        """

    def __init__(self):
        "sets up the configuration and the logger"
        self.logger = logging.getLogger("server")
        self.config = config.Config()
        self.config.parse_cmd_line()
        self.server = None
        self.setup_server()
        self.chandler = handle_commands.CommandHandler()
        self.variable_dict = {}
        ttl_conf_file = self.config.get_str("SERVER","DIO_configuration_file")
        self.dds_count = self.config.get_int("SERVER","DDS_count")
        # Extracts the channel names and numbers from the configuration file written by QFP
        self.ttl_dict = self.config.get_digital_channels(ttl_conf_file)
        self.setup_dac() # DAC
        self.segfalle = None

    def setup_server(self):
        "Reads the configurations and configures the server"
        server_port = self.config.get_int("SERVER","server_port")
        answer = self.config.get_bool("SERVER","server_answer")
        pre_return = self.config.get_bool("SERVER","server_pre_return")
        self.server = server.TcpServer(port=server_port, answer=answer, \
                                           pre_return=pre_return)

    def start_server(self):
        "executes the main loop of the server"
        try:
            self.server.main_loop(self.execute_program)
        except:
            self.logger.exception("Error in server main loop")

#DAC_Control for segtrappers
    def setup_dac(self):
        "inits and configures the dac_controls"
        self.segfalle = self.config.get_bool("DACCONTROL","segfalle")
        dac_numcards = self.config.get_int("DACCONTROL","num_cards")
   #     self.dac_api = dac_funtion.dac_API(dac_numcards)
#End of DAC_Control


    def execute_program(self, command_string):
        """This method is called by the main loop of the server
        The argument passed to this method is the command string sent from LabView
        """
        return_var = ReturnClass()
        try:
            self.variable_dict = self.chandler.get_variables(command_string)   # command string is parsed by handle_commands.py and variables are saved to a dictionary
        except ValueError:
            self.logger.exception("Error while interpreting command string")
            return_var.error("Error while interpreting command string")
            return return_var


#Here DACs will be handled, have to create my own "API"-file.... :-(:
    #    if self.segfalle:
    #        self.dac_api.set_dac(self.chandler) #DAC, if only static, then dac_update=True
     #       if self.dac_update:
      #          generate_str = "OK, DACs updated"
       #         return_var.return_string = generate_str
        #        return return_var

        # initialize API
        user_api = user_function.userAPI(self.chandler, ttl_dict=self.ttl_dict, \
                                         dds_count = self.dds_count)
        user_api.clear()


        # The init sequence is now executed in compile_sequence.
        # This is due to the transition management system

        # Generate sequence

        try:
            generate_str = user_api.generate_sequence()
        except:
            self.logger.exception("Error while generating sequence")
            return_var.error("Error while generating sequence")
            return return_var
        # end loops and generate IOs for LabView
        user_api.end_sequence()

        # Compile sequence

        try:
            user_api.compile_sequence()
            sequence_length = len(user_api.sequencer.current_sequence)

#           user_api.sequencer.debug_sequence(show_word_list=True)

            self.logger.info("sequence length: "+str(hex(sequence_length))+" ("+str(1/100.0*int(10000.0*sequence_length/self.config.get_int("PCP", "max_sequence_length")))+"% of maximum sequence length)")
        except:
            self.logger.exception("Error while compiling sequence")
            return_var.error("Error while compiling sequence")
            return return_var


        # Send sequence to Box

        try:
            user_api.send_sequence()
        except:
            self.logger.exception("Error while sending sequence")
            return_var.error("Error while sending sequence")
        user_api.clear()
        del(user_api)
        return_var.return_string = generate_str

        # Let's save the last logs to a single file
        # TODO: better check if we are using the right handler
        try:
            log1 = logging.getLogger()
            handler = log1.handlers[1]
            handler.target.doRollover()
            handler.flush()
        except IndexError:
            self.logger.error("Error while trying to log actual sequence")
            return return_var


# main_program.py ends here
