# (c) by Lutz Petersen, Philipp Schindler
"""class for communicating over the ethernet"""
import struct
import socket
import logging
import config

START_PORT = 8736
STOP_PORT = 8736 + 16

class PTPComm:
    """class for communication with the box over the PTP protocol
    For sending a program to the box the method send_code may be used.
    """

    #constants
#    MY_PORT  = 0x221e

    MY_PORT  = 0x221f
    HIS_PORT = 8745  #8743  #0x2229
    HIS_IP   = '192.168.0.229'
    RETRY_COUNT = 5
    MAX_FRAME_LENGTH = 984

    PCP_DISCOVER_REQUEST = "\x09\x00\x00\x0b\x00\x00\x02"
    PCP_START_REQUEST   = "\x04\x00\x00\x0b\x00\x00\x01"
    PCP_STOP_REQUEST    = "\x04\x00\x00\x0b\x00\x00\x02"
    DDS_RESET_REQUEST   = "\x07\x00\x00\x0f\x00\x00\x61\x00\x00\x44\x00"
    DDS_UNRESET_REQUEST = "\x07\x00\x00\x0f\x00\x00\x61\x00\x00\x44\xff"


    #globals
    client_socket = None

    def __init__(self, nonet=False):
        """Initialize the PTP communication
        @param nonet: Boolean; If true no communication with the box is performed
        """
        self.nonet = nonet
        self.logger = logging.getLogger("sequencer2")
        if self.logger.level >= 30:
            self.debug = True
        else:
            self.debug = False
        if self.nonet:
          self.logger.warn("Running in nonet mode")

        try:
            self.config = config.Config()
            self.HIS_IP = self.config.get_str("PTP","box_ip_address")
            self.save_file = self.config.is_savebin()
        except:
            self.logger.warn("COMM: cannot read configuration file")

    #functions
    def print_binary(self, code):
        """Prints a readeable version of the UDP packets
        @param code: BInary PTP code """
        if self.debug == False:
            return
        length = len(code) / 4
        code_list = struct.unpack("!"+str(length)+"L", code[:length*4])
        for i in range(length):
            if i % 8 == 0:
                print
                print "%04x" % i, "|",
            print "%08x" % code_list[i],
        for i in range(len(code)%4, 0, -1):
            print "%02x" % ord(code[-i]),
        print


    def send_frame(self, data, port=None):
        """Sends an already generated frame to the PCP
        @param data: Binary PTP packet
        @param port=None: Send data frame on port if given
        """
        if port:
            actual_port = port
        else:
            actual_port = self.HIS_PORT
        # create a client_socket
        if self.nonet:
            return
        if self.client_socket == None:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
            self.client_socket.bind(('', self.MY_PORT))
            self.client_socket.settimeout(0.1)  # seconds

        # frame header
        datastring = '\x00\x02'
        # version
        datastring += '\x00\x15'
        # Data has the following format:
        #   opcode
        #   0x00
        #   total length (two bytes)
        #   0x00 0x00
        #   payload
        datastring += data

        self.print_binary(datastring)

        # send the frame
        retry_count = 0
        while retry_count < self.RETRY_COUNT:
            result = self.client_socket.sendto(datastring, (self.HIS_IP, actual_port))
            if result != len(datastring):
                raise RuntimeError, "Socket operation did not send all bytes."
            reply_data = self.recv_frame()
            if len(reply_data) > 0:
                break
            retry_count += 1
        if len(reply_data) > 0:
            self.print_binary(reply_data)
            return reply_data
        raise RuntimeError, "No Pulse Transfer Protocol reply received."


    def recv_frame(self):
        "Receive frame from PTP"
        if self.nonet:
            return
        try:
            data = self.client_socket.recvfrom(1024)
            # data is a tuple (string, (ip_address, port))
            data = data[0]
            total_length = ord(data[6]) << 8 | ord(data[7])
            return data[4:total_length]
        except socket.timeout:
            return ""


    def pack_write_frame(self, offset, payload):
        """Generate PTP frame
        @param offset: offset in the memory to write to
        @param payload: Binary instruction words for the PCP"""
        total_length = len(payload) + 14
        # opcode
        data = "\x02\x00"
        # length
        data += chr(total_length>>8 & 0xff) + chr(total_length & 0xff)
        # unused
        data += "\x00\x00"
        # subopcode
        data += "\x01" + chr((offset>>16) & 0xff) + chr((offset>>8) & 0xff) + chr(offset & 0xff)
        # payload
        data += payload
        return data


    def reset_dds(self):
        """Sends I2C reset events to the PCP
        Not needed for the AD9910
        """
        self.send_frame(self.DDS_RESET_REQUEST)
        self.send_frame(self.DDS_UNRESET_REQUEST)

    def send_code(self, code_list):
        """Sends a bytecode to the PCP
        @param code_list: Binary instruction word list
        """
        
        if self.save_file:
            self.savebin(code_list)
        code = ""
        for code_item in code_list:
            code += code_item
        # stop the processor
        self.send_frame(self.PCP_DISCOVER_REQUEST)
        self.send_frame(self.PCP_STOP_REQUEST)

        # write the pulse program in chunks
        byte_pos = 0
        while byte_pos < len(code):
            payload = code[byte_pos:byte_pos+self.MAX_FRAME_LENGTH]
            self.send_frame(self.pack_write_frame(byte_pos, payload))
            byte_pos += self.MAX_FRAME_LENGTH

        # start the processor
        self.send_frame(self.PCP_START_REQUEST)

    def send_discover(self):
        "Tries to find the box and sets the port"
        try:
            self.send_frame(self.PCP_DISCOVER_REQUEST)
        except RuntimeError:
            for port in xrange(START_PORT, STOP_PORT):
                try:
                    self.send_frame(self.PCP_DISCOVER_REQUEST, port)
                    self.logger.info("Using port: " + str(port))
                    PTPComm.HIS_PORT = port
                    self.HIS_PORT = port
                    return
                except RuntimeError:
                    self.logger.debug("Failed to use port: " + str(port))
            raise RuntimeError("Cannot find box at: " + str(self.HIS_IP))

    def savebin(self, code_list):
        """Saves a binary list to the file sequencer2.bin
        @param code_list: a list of binary characters resembling the binary code"""
        filename = "sequencer2.bin"
        filehandle = open(filename, "wb")
        for char in code_list:
            filehandle.write(char)
        filehandle.close()
