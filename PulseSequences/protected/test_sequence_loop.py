# TEst sequence for unittests for the server

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

<SEQUENCE>
if det_time == 100000.0:
    raise RuntimeError("Variable not set")
insert_label('infinite_target')
ttl_pulse(["3", "5"],500)
jump_trigger('trigger_label',0x2)
jump_label('infinite_target')
insert_label('trigger_label')
ttl_pulse(["1", "5"],500)

</SEQUENCE>

<AUTHORED BY LABVIEW>
1
</AUTHORED BY LABVIEW>
