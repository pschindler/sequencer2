#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "12-Jan-2010 12:10:48 c704215"

#  file      : server.py
#  email     : philipp DOT emacs DOT schindler AT uibk DOT ac DOT at
#            : remove the "One And Only Editor"
#  copyright : (c) 2006 Philipp Schindler
# pylint: disable-msg=E1101
#_* Code

import socket
import time
import logging
#from innsbruck import *

class TcpServer:
    "The class for receiving data from LabView"
    def __init__(self, port=8880, answer=False, pre_return=False):
        "set all important parameters for the server"
        self.port = port
        self.logger = logging.getLogger("server")
        self.answer = answer
        self.pre_return = pre_return

    #The one and only TCP server
    #just calls get_variables and create_program with the received string
    # we need definitely some error checking here

    def main_loop(self, program_method):
        "Executes program method with the received string as the argument"
        while True:
            self.logger.info("server started")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('', self.port))
            sock.listen(5)
            try:
                while True:
                    newSocket, address = sock.accept()
                    self.logger.debug("ip address: "+str(address))
                    while True:
                        try:
                            self.logger.debug("ready to receive:")
                            receivedData = newSocket.recv(4*8192)
                            #maybe we should increase the max receive data
                        except:
                            self.logger.warn("Socket error while receiving data")
                        if not receivedData:
                            self.logger.info("No data received")
                            break
                        if receivedData == "alive?":
                            self.logger.debug("Sended alive response")
                            newSocket.sendall("alive!"+";\r\n") #added TK
                            break
                        if self.pre_return:
                            try:
                                newSocket.sendall("RECEIVED!"+";\r\n") #added TK
                            except:
                                self.logger.warn("Error while sending return string")

                        self.logger.debug("received data: " + str(receivedData))
                        start_time = time.time()
                        return_var = program_method(receivedData)
                        stop_time = time.time()
                        used_time = round((stop_time-start_time)*1000)
                        try:
                            if return_var.is_error:
                                time_str = "ERROR"
                            else:
                                time_str = "OK, sequence_duration, " + str(used_time) + ";\n"
                        except AttributeError:
                            self.logger.warn("The main loop returned a wrong object type")

                        return_string = return_var.return_string
                        error_string = return_var.error_string
                        if (error_string==""):
                            return_string = time_str + return_string
                            self.logger.debug("Return string: "+return_string)
                            if self.answer:
                                try:
                                    newSocket.sendall(return_string + "\r\n")
                                except:
                                    self.logger.warn("Error while returning value")

                        else:
                            self.logger.debug("trying to send error: "+error_string)
                            if self.answer:
                                newSocket.sendall(error_string+"\r\n")
                            error_string = ""
                        self.logger.debug("finish connected")
                    newSocket.close()

            finally:

                self.logger.info("Disconnected server")
                try:
                    socket.close()
                except AttributeError:
                    self.logger.warn("server crashed")


# server.py ends here
