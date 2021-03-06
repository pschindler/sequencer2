Sequencer2  main documentation
================================

Overview - About the sequencer2
-------------------------------
The sequencer2 is a compiler for the FPGA experiment control system known as the
Programmable pulse generator (PPG).

The home page of the PPG is at:

http://pulse-programmer.org

The sequencer2 can be downloaded from the mercurial (hg) repository on
the source-forge page.  With a command line hg tool just type::

  hg clone http://pulse-sequencer.hg.sourceforge.net:8000/hgroot/pulse-sequencer/sequencer2

With a GUI tool (Tortoise HG) just select clone and add the following URL

http://pulse-sequencer.hg.sourceforge.net:8000/hgroot/pulse-sequencer/sequencer2

This high level documentation is written in the restructured text
format and can be converted in a HTML or PDF document.


Structural overview
-------------------
The sequencer2 source code consists of two different modules:


+-----------------+---------------------------------------------+
|sequencer2       |  The Bytecode assembler                     |
+-----------------+---------------------------------------------+
|server           |  A TCP server for interfacing with LabView  |
+-----------------+---------------------------------------------+

Where the sequencer2 module generates the binary code for the PPG and transmits
it via an ethernet connection.

The sequencer2 module can be used without the server module

The server package is a high level interface for the sequencer module and handles
the communication with the experiment control software. 

Installing the software
-----------------------

For installing the server the Python programming language in
version 2.4 to 2.6 is required.

The  sequencer2 does not work with python 3.0 or higher

The python programming language can be downloaded at:

http://python.org

The sequencer2 itself does not need an installation. 
Just copy to files to a directory and run the server from a command line.

Configuring the server 
-----------------------

The default configration is stored in the file config/sequencer2.ini. Do not edit his file.

The site configuration is stored in the file user_sequencer2.ini.

To generate this file run the interactive script configure.py::

     python configure.py

This script will generate the file config/user_sequencer2.ini

For a new setup make sure that at least following settings are correct:


+--------------------------+------------------------------------------+
|Setting                   |     Value                                |
+==========================+==========================================+
|box_ip_address            |     The network address of the sequencer.|
+--------------------------+------------------------------------------+
|DIO_configuration_file    |     Your hardware configuration file     |
+--------------------------+------------------------------------------+
|sequence_dir              |     The directory of your sequence files |
+--------------------------+------------------------------------------+
|include_dir               |     The directory of your include files  |
+--------------------------+------------------------------------------+
|nonet                     |     False                                |
+--------------------------+------------------------------------------+
|reference_frequency       |     Your DDS reference frequency         |
+--------------------------+------------------------------------------+


The network address of the sequencer is set by the DIP switches on the sequencer PCB board

How to set up the ip address
----------------------------

To set the ip address on the PPG main board use the red dip switches.

The pin usage on the board is:

+-----+---+---+---+---+----+
|reset|ip1|ip2|ip3|ip4|dhcp|
+-----+---+---+---+---+----+

set dhcp to OFF

The ip address is 192.168.0.X where::

   X = 220 + ip1 + 2 * ip2 + 4 * ip3 + 8 * ip4


Testing the PBox Hardware
-------------------------

An interactive testing program that uses the webbrowser to give
directions for troubleshooting is available::

    python test_pbox_hardware.py

It is able to investigate

* The network configuration of the PBox and the sequencer
* The TTL output modules
* The DDS board and its connection

Starting up the server
----------------------

After that the server may be started with::

 python test_sequencer2_server.py


Configuring the logging module
------------------------------

Generally the logging module is set in the startup file.
For a default installation this file is test_sequencer2_server.py

The logging is enabled by the line::

     logger=ptplog.ptplog()


The log level is determined by the configuration file user_sequencer2.ini.

Following options are allowed::

     log_filename = None
     console_log_level = WARNING
     combined_log_level = DEBUG
     default_log_level = DEBUG


If log_filename is set to None, the sequencer logs only to the terminal
with default_log_level

Following log levels are allowed::

    DEBUG
    INFO	
    WARNING
    ERROR


Logging to files
----------------

The logging facilites are also able to log to a couple of files.
To log to files the logger should be configured as::

log_filename = log/sequencer2


Now the logger will log to following files::

    sequencer2_sequencer2.log
    sequencer2_api.log
    sequencer2_server.log
    sequencer2_DACcontrol.log
    sequencer2_all.log


The file sequencer_all.log will contain messages from all different logging parts with the log level set by
combined_log_level

Viewing log files
-----------------

The log files which are describd may be viewed with the help of the logtools
The logtools are included in any sequencer2 distribution and may be invoked typing::

 python debug/logtools.py


Writing pulse sequences
------------------------

There are 2 possibilities of generating pulse sequences:

- Generate a pulse sequence directly from sequencer2
- Use the server and high level script files to generate pulse sequences

Writing pulse sequences directly in the sequencer2
---------------------------------------------------

A typical pulse sequence::

     import sequencer
     import api
     import ptplog
     my_sequencer=sequencer.sequencer()
     my_api=api.api(my_sequencer)
     my_api.dac_value(1, 12)
     my_api.jump("test")
     my_sequencer.compile_sequence()

This script is then directly executed in the sequencer2 root directory by typing:

An example is::

 python [script_name]


List of API commands
--------------------
Below is a table of commands which are available through the API interface


+------------------------------------+----------------------------------------------------+
| Command                            |    Function                                        |
+====================================+====================================================+
| wait(time, use_cycles=False)	     |	wait for a given time in Microseconds             |
+------------------------------------+----------------------------------------------------+
| label(label_name)		     |	Insert a label                                    |
+------------------------------------+----------------------------------------------------+
| jump(target_name)		     |	Jump to label with given name                     |
+------------------------------------+----------------------------------------------------+
| jump_trigger(target_name,trigger)  |	Jump to label if trigger inputs match the Bitmask |
+------------------------------------+----------------------------------------------------+
| start_finite(label_name,loop_count)|	Begin a finite loop with given loop count         |
+------------------------------------+----------------------------------------------------+
| end_finite(target_name)	     | 		End a finite loop                         |
+------------------------------------+----------------------------------------------------+
| begin_subroutine(sub_name)	     |	Start a subroutine                                |
+------------------------------------+----------------------------------------------------+
| end_subroutine(sub_name)	     |	End a subroutine                                  |
+------------------------------------+----------------------------------------------------+
| call_subroutine(sub_name)	     |	Calls a subroutine                                |
+------------------------------------+----------------------------------------------------+
| ttl_value(value, select)	     |	Sets the status of a 16Bit part of the digital IO |
+------------------------------------+----------------------------------------------------+
| dac_value(value, address)	     |Sets the DAC on the DDS board with the given address|
+------------------------------------+----------------------------------------------------+
| init_dds(dds_instance)             |	Control the AD9910 DDS                            |
+------------------------------------+----------------------------------------------------+
| update_dds(dds_instance)           |                                                    |
+------------------------------------+----------------------------------------------------+
| set_dds_profile(dds_inst,profile)  |                                                    |
+------------------------------------+----------------------------------------------------+
| set_dds_freq(dds_inst,freq,profile)|                                                    |
+------------------------------------+----------------------------------------------------+
| load_phase			     |	Control the phase registers                       |
+------------------------------------+----------------------------------------------------+
| pulse_phase                        |                                                    |
+------------------------------------+----------------------------------------------------+
| init_frequency                     |                                                    |
+------------------------------------+----------------------------------------------------+


Using the DDS from the API interface
------------------------------------

A simple example for testing the functionality of the DDS board::


    my_sequencer = sequencer.sequencer()
    my_api = api.api(my_sequencer)
    dds_device = ad9910.AD9910(my_device, 800)
    my_api.init_dds(dds_device)
    my_api.set_dds_freq(dds_device, frequency, 0)
    my_api.set_dds_profile(dds_device, 0)
    my_api.update_dds(0, dds_device)        
    my_sequencer.compile_sequence()


For more examples on testing the DDS see the file::

tests/test_hardware.py



Writing pulse sequences with server component
---------------------------------------------

The server component acts as an interface between the API component and an advanced experiment control program.

A sequence is executed as follows:

- Experiment control software sends script filename and sequence data to the server
- Server interprets this "command string" and loads the sequence file
- The sequence file is executed
- The server sends data back to the experiment control software.

An example sequence file::

    # Define the sequence variables
    <VARIABLES>
    det_time=self.set_variable("float","det_time",100000.000000,0.01,2e7)
    </VARIABLES>
    # The save form specifies which data will be saved and how, when a scan is performed.
    # If this is omitted a standard form is used
    <SAVE FORM>
      .dat   ;   %1.2f
       PMTcounts;   1;sum; 		(1:N);		%1.0f
    </SAVE FORM>
    # Here the sequence can override program parameters. Syntax follows from "Write Token to Params.vi"
    <PARAMS OVERRIDE>
    AcquisitionMode fluorescence
    DOasTTLword 1
    Cycles 1
    </PARAMS OVERRIDE>
    # The sequence itself
    <SEQUENCE>
    ttl_pulse(["397_det", "866"],det_time)
    </SEQUENCE>
    # Some spooky LabView stuff
    <AUTHORED BY LABVIEW>
    1
    </AUTHORED BY LABVIEW>



This file contains chunk that is needed for the Innsbruck experiment control system also known as QFP ...

The format of the command string is described in the Innsbruck manual available on the sf.net download site.

Reporting Bugs
--------------
If you encounter any bugs in the software/hardware of your experiment write an email to:

philipp.schindler@uibk.ac.at

Testing the sequencer2 internals
---------------------------------

The python code of the sequencer2 may be tested with following
command::

  python sequencer2_unittest.py

Note that this does not test the Hardware, it is intended for testing
the source code of the seqeuencer2. It tests the generation of the
machine code from the API layer commands and (to a lesser extend) the
generation of the API commands from the end user layer.

More documentation
------------------

A general talk about the Box may be found on

http://pulse-sequencer.sourceforge.net/innsbruck/obergurgl-box.pdf

A sequence programming overview may be found on:

http://pulse-sequencer.sourceforge.net/innsbruck/box-cheat.pdf

The LabView interface documentation and a general overview may be found in
the old documentation:

http://sourceforge.net/project/showfiles.php?group_id=129764&package_id=220283

Please note that this manual refers to the "old" sequencer and is not generally
valid for the sequencer2. The LabView interface is identical in the two servers.

API documentation
-----------------

The server uses the epydoc markup language inside the source code.

To generate the API-level documentation the epydoc interpreter is needed.
It is available from: http://epydoc.sf.net

The documentation is generated with the command::

  epydoc -v --top=server server sequencer2


Debugging the sequencer
-----------------------

This simple debugging procedure is able to test the API commands on
the hardware itself.

Simple tests are collected in the file tests/test_hardware.py

For testing purposes an interactive python shell is needed.
For better testing experince it is recommended to use the
improved python shell http://ipython.scipy.org

If python is in your system path the shell may be invoked from the
root directory of the sequencer2 in a command window by simply
typing::

 python


Then the test_hardware file has to be imported::

    from tests.test_hardware import *


After that the HardwareTests class has to instantiated::

    ht = HardwareTests()


To test the TTL subsystem of the Box type then::


    ht.test_ttl_set()


It is advisable to play around with the commands defined in
tests.test_hardware.py to get a feeling of how the commands
work

Tips for trouble shooting can be found in the general box documentation:

http://sourceforge.net/project/showfiles.php?group_id=129764&package_id=220283

Debugging the server with ipython
---------------------------------

This debugging method is for low level debugging of the server. This
can be used to investigate unusual behavior of the hardware or to add
more functionality top the API.

For debugging the server the ipython python shell is recommended.
Ipython is available at:

http://ipython.scipy.org

Start the ipython shell in the root directory of the server.
Generate the necessary variables and includes by running following command::

   %run test_ipython.py


A simple sequence consisting of two ttl pulses is then generated with the commands::

  ttl_pulse("1",10)
  ttl_pulse("2",10)


The sequence list is generated with the command::

  user_api.final_array = user_api.get_sequence_array(sequence_var)[0]


Compiling the sequence is done with the command::

 user_api.compile_sequence()


The machine code of the sequence is displayed with the following
command::

  user_api.sequencer.debug_sequence(force=True)


COPYING
-------

Copyright (C) 2008 Philipp Schindler, Max Harlander, Lutz Peterson,
                   Boerge Hemmerling, Thomas Holleis

Free use of this software is granted under the terms of the
GNU General Public License (GPL).

