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
        self.variables = {}
        self.init_transitions()
        self.pulse_program_name = None
        self.cycles = 1
        self.last_transition = None
        self.transition = None
        self.default_transition = None

    def get_variables(self, var_string):
        "Splits up the string and invokes variable extraction mehtods "
        self.variables = {}
        splitted_list = []

        frame = var_string.split(";")

        for frame_item in frame:
            splitted = frame_item.split(",")
            splitted_list.append(splitted)
            try:
                self.command_dict[splitted[0]](splitted)

            except KeyError:
                self.logger.warn("error: cannot identify command"+str(splitted))

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

        #return the dict to the handler !
        return command_dict

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

    def get_transition(self, splitted):
        "Generate a transition object"
        if splitted[0] == "TRANSITION":
            name = splitted[1]
            self.transitions[name] = transition(name, 0, 0)
            self.last_transition = splitted[1]
        if splitted[0] == "DEFAULT_TRANSITION":
            name = splitted[1]
            self.transitions[name] = transition(name, 0, 0)
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
        elif splitted[0] == "FREQ2":
            self.transition.frequency2 = float(splitted[1])
            self.transition.freq_is_init = False

        elif splitted[0] == "IONS":
            self.transition.ion_list = self.get_dictionary(splitted)

        self.transitions[self.last_transition] = self.transition



    def get_dictionary(self, splitted):
        "Extract a dictionary from the command string"

        dict_string = "this_dict={"
        for i in range(1, len(splitted)):
            dict_string += splitted[i]+" , "
        dict_string += "}"
        try:
            exec(dict_string)
        except:
            self.logger.warn("Error while getting dictionary"+str(splitted))
            this_dict = {}
        return this_dict

    def init_transitions(self):
        "Generates a transition with frequency 0 for switching off the DDS"
        trans_obj = transition("NULL", 0, 0)
        self.transitions["NULL"] = trans_obj
