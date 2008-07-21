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

#rf_pulse(1,0,1,"carrier1")
rf_pulse(1,0,1,"carrier2")
rf_pulse(1,0,1,"carrier3")
rf_pulse(1,0,1,"carrier4")
rf_pulse(1,0,1,"carrier5")
rf_pulse(1,0,1,"carrier6")
rf_pulse(1,0,1,"carrier7")
rf_pulse(1,0,1,"carrier8")
#rf_pulse(1,0,1,"carrier9")

# if switch729: rf_set729(freq729,power729)
# else: rf_set729(freq729,-100)
# if switchRaman: rf_setRaman(freqRaman,powerRaman)
# else: rf_setRaman(freqRaman,-100)

# incl.PMTDetection(det_time,gl_cam_time,no_lasers=True)
</SEQUENCE>

<AUTHORED BY LABVIEW>
1
</AUTHORED BY LABVIEW>
