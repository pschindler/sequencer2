#from sequencer.constants import *
import logging

from sequence_handler import transition, TransitionListObject

class CommandHandler:
    """The new command handler for the sequencer2
    The transitions routines are hopeless broken :-("""
    def __init__(self):
        self.command_dict = self.get_command_dict()
        self.logger = logging.getLogger("sequencer2")
        self.transitions = TransitionListObject()
        self.transitions.clear()
        self.variables = {}
        self.init_transitions()
        self.pulse_program_name = None
        self.cycles = 1
        self.last_transition = None
        self.transition = None
        self.default_transition = None
        self.is_triggered = False
        self.ttl_word = 0
        self.ttl_mask = 0 # this is not used
        self.dac_sampling_rate = None
        self.dac_nr_of_samples = None

    def get_variables(self, var_string):
        self.dac_ramps = {}
        self.dac_voltarrays = {}
        self.variables = {}
        splitted_list = []
        self.logger.debug("command_string: + \n" + var_string)
        frame = var_string.split(";")

        for frame_item in frame:
            splitted = frame_item.split(",")
            splitted_list.append(splitted)
            try:
                self.command_dict[splitted[0]](splitted)

            except KeyError:
                if len(str(splitted)) > 4 :
                    self.logger.info("cannot identify command"+str(splitted))

            except SyntaxError:
                self.logger.warn("error while executing command"+str(splitted))

        return self.variables

    def get_command_dict(self):
        "defines the command dictionary"
        command_dict = {}

        # The commands understood by the server
        command_dict["NAME"] = self.get_name
        command_dict["CYCLES"] = self.get_cycles
        command_dict["TRIGGER"] = self.get_trigger
        command_dict["TTLWORD"] = self.get_ttlword
        command_dict["TTLMASK"] = self.get_ttlmask

        #Some boring ordinary variables
        command_dict["FLOAT"] = self.get_vars
        command_dict["INT"] = self.get_vars
        command_dict["BOOL"] = self.get_vars
        command_dict["STRING"] = self.get_vars

        # The transition variables:
        command_dict["TRANSITION"] = self.get_transition
        command_dict["DEFAULT_TRANSITION"] = self.get_transition
        command_dict["RABI"] = self.get_transition
        command_dict["SLOPE_TYPE"] = self.get_transition
        command_dict["SLOPE_DUR"] = self.get_transition
        command_dict["FREQ"] = self.get_transition
        command_dict["AMPL"] = self.get_transition
        command_dict["IONS"] = self.get_transition
        command_dict["FREQ2"] = self.get_transition
        command_dict["AMPL2"] = self.get_transition
        command_dict["SWEEP"] = self.get_transition

        # The DAC commands:
        command_dict["DAC"] = self.get_dac
        command_dict["RAMP"] = self.get_dac

        #return the dict to the handler !
        return command_dict

    def get_ttlmask(self, splitted):
        "Get the TTL mask - not used though"
        self.ttl_mask = int(splitted[1])

    def get_ttlword(self, splitted):
        "Get the TTL output"
        self.ttl_word = int(splitted[1])

    def get_name(self, splitted):
        "Get name of the pulse program"
        self.pulse_program_name = splitted[1]


    def get_cycles(self, splitted):
        "Get cycle count"
        self.cycles = int(splitted[1])


    def get_vars(self, splitted):
        "Get variable values and store it in a dictionary"
        if (splitted[0]=="FLOAT"):
            self.variables[splitted[1]] = float(splitted[2])
        elif (splitted[0]=="INT"):
            self.variables[splitted[1]] = int(splitted[2])
        elif (splitted[0]=="STRING"):
            self.variables[splitted[1]] = str(splitted[2])
        elif (splitted[0]=="BOOL"):
            self.variables[splitted[1]] = bool(int(splitted[2]))


    def get_trigger(self, splitted):
        "Get trigger mode"
        trig_string = splitted[1]
        if (trig_string!="NONE"):
            self.start_trigger = 0x1 # Trigger configuration ??
            self.is_triggered = True
        else:
            self.is_triggered = False

    def get_dac(self, splitted):
        if (splitted[0]=="DAC"):
            num_array = self.get_array(splitted, start_split = 2)
            self.dac_voltarrays[splitted[1]] = num_array
        elif (splitted[0]=="RAMP"):
            ramp_dict = self.get_dictionary(splitted)
            self.dac_ramps[ramp_dict["ramp"]] = ramp_dict


    def get_transition(self, splitted):
        "Generate a transition object"
        if splitted[0] == "TRANSITION":
            name = splitted[1]
            self.transitions[name] = transition(name, {0:0}, 0)
            self.last_transition = splitted[1]
        if splitted[0] == "DEFAULT_TRANSITION":
            name = splitted[1]
            self.transitions[name] = transition(name, {0:0}, 0)
            self.last_transition = splitted[1]
            self.default_transition = self.transitions[self.last_transition]

        self.transition = self.transitions[self.last_transition]
        if splitted[0] == "RABI":
            self.transition.t_rabi = self.get_dictionary(splitted)
        elif splitted[0] == "SLOPE_TYPE":
            self.transition.slope_type = splitted[1]
        elif splitted[0] == "SLOPE_DUR":
            self.transition.slope_duration = float(splitted[1])
        elif splitted[0] == "AMPL":
            self.transition.amplitude = float(splitted[1])
        elif splitted[0] == "FREQ":
            self.transition.frequency = float(splitted[1])
            self.transition.freq_is_init = False
        elif splitted[0] == "AMPL2":
            self.transition.amplitude2 = float(splitted[1])
        elif splitted[0] == "SWEEP":
            self.transition.sweeprange = float(splitted[1])

        elif splitted[0] == "FREQ2":
            self.transition.frequency2 = float(splitted[1])
            self.transition.freq_is_init = False

        elif splitted[0] == "IONS":
            self.transition.ion_list = self.get_dictionary(splitted)

        self.transitions[self.last_transition] = self.transition



    def get_dictionary(self, splitted):
        "Extract a dictionary from the command string"
        this_dict ={}
        item_array = splitted[1:]
        # Get the items out of the dict_array
        for item in item_array:
            key, value = item.split(':')
            this_dict[int(key)] = float(value)
            
        return this_dict


    def get_array(self, splitted, start_split=1):
        this_array = []
        for item in splitted[start_split:]:
            this_array.append(float(item))
        return this_array

    def init_transitions(self):
        "Generates a transition with frequency 0 for switching off the DDS"
        trans_obj = transition("NULL", {1 : 0}, 0)
        self.transitions["NULL"] = trans_obj


