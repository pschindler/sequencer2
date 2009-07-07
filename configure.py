#!/usr/bin/env python
# -*- mode: Python; coding: latin-1 -*-
# Time-stamp: "2009-02-12 13:42:50 c704271"

#  file       config.py
#  copyright  (c) Philipp Schindler 2008
#  url        http://pulse-sequencer.sf.net

# configure.py script for generating the local configuration of the
# sequencer2 server.

# Usage: execute script and answer questions:

import os

# configuration
CONFIG_FILENAME = "config/user_sequencer2.ini"

# question and answers:
print "Please answer the following questions \n\n"
print "What is the last byte of the box IP address?"
ip_addr_byte = raw_input("192.168.0.X :  ")
ip_addr_str = "192.168.0." + ip_addr_byte

dds_count = raw_input("How many DDS channels are available? ")

print "\n\n ********************************************************** \n"
print "Please remember to use the slash / instead of the backslash \\ for file names \n"


print "\nWhat is the file NAME of the Hardware Settings file?"
hardware_path = raw_input()

print "\nWhat is the file path to the Pulse sequence files?"
print "Press enter if your control program supplies the full path"
print "Yes QFP does this"
sequence_path = raw_input()

print "\nWhat is the file path to the Include files?"
include_path = raw_input()

print "\nWhat is your reference frequency?"
ref_freq = raw_input()

print "\n\n************************************************************"
print "Please note that not all possible configuration options are handled"
print "with this helper program. Look into the file "
print "config/sequencer2.ini for more information"

# Generate configuration string
config_str = "#Automatically generated file\n"
config_str += "#You can edit this - but it may be overwritten when executing"
config_str += " configure.py\n\n"
config_str += "[SERVER]\n"
config_str += "#We have got a working box so we set nonet to False\n"
config_str += "nonet = False\n\n"
config_str += "DIO_configuration_file = " + str(hardware_path) + "\n\n"
config_str += "sequence_dir = " + str(sequence_path) + "\n\n"
config_str += "include_dir = " + str(include_path) + "\n\n"
config_str += "DDS_count = " + str(dds_count) + "\n\n"
config_str += "[PTP]\n"
config_str += "box_ip_address   = " + str(ip_addr_str) + "\n\n"
print "\n\n*************************************\n\n\n\n"
print "The configuration file: \n"
print config_str
#Check if the file already exists !!
if os.path.isfile(CONFIG_FILENAME):
    print "Warning config file exists! Should I overwrite the file? (y/n)"
    decision = raw_input()
    if decision != "y":
        raise RuntimeError("Config file already exists")

# Write the file to disk:
fobj = open(CONFIG_FILENAME,"w")
fobj.write(config_str)
fobj.close()
