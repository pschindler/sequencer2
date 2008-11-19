# Module : bitmask
# Package: pcp.tests
# Unit tests for Bitmask class

import unittest
import time
import logging
#import psyco
from  sequencer2 import sequencer
from  sequencer2 import api
from  sequencer2 import instructions
from  sequencer2 import outputsystem

#------------------------------------------------------------------------------
class Test_Sequencer(unittest.TestCase):

  def test_ttl_system(self):
    "test the ttl subsystem"
    output_status=[0,0,0,0]
    ttl_sys = outputsystem.OutputSystem()

    new_state = ttl_sys.set_bit("5",1,output_status)
    output_status[new_state[0]] = new_state[1]
    self.assertEquals(output_status,[0,0,2**5,0])

    new_state = ttl_sys.set_bit("4",1,output_status)
    output_status[new_state[0]] = new_state[1]
    self.assertEquals(output_status,[0,0,2**4|2**5,0])

    new_state = ttl_sys.set_bit("5",0,output_status)
    output_status[new_state[0]] = new_state[1]
    self.assertEquals(output_status,[0,0,2**4,0])

  def test_ttl_set_bit(self):
    "test the set bit api function"
    my_sequencer=sequencer.sequencer()
    my_api = api.api(my_sequencer)
    my_api.ttl_set_bit("1",1)
    my_api.ttl_set_bit("6",1)
    my_api.ttl_set_bit("18",1)
    my_sequencer.compile_sequence()
    my_sequencer.debug_sequence()
    self.assertEquals(my_sequencer.current_output,[0,0,66,4])
    insn=my_sequencer.current_sequence[1]
    self.assertEquals(insn.output_state,0x42)
    insn=my_sequencer.current_sequence[2]
    self.assertEquals(insn.change_state,0x3)
    self.assertEquals(insn.output_state,0x4)

  def test_ttl_set_bit(self):
    "test the set bit api function"
    my_sequencer=sequencer.sequencer()
    my_api = api.api(my_sequencer)
    my_api.ttl_set_bit("1",1)
    my_api.ttl_set_bit("6",1)
    my_api.ttl_set_bit("18",1)
    my_sequencer.compile_sequence()
    my_sequencer.debug_sequence()
    self.assertEquals(my_sequencer.current_output,[0,0,66,4])
    insn=my_sequencer.current_sequence[1]
    self.assertEquals(insn.output_state,0x42)
    insn=my_sequencer.current_sequence[2]
    self.assertEquals(insn.change_state,0x3)
    self.assertEquals(insn.output_state,0x4)



  def test_ttl_multiple(self):
    "test the ttl_set_multiple api function"
    my_sequencer=sequencer.sequencer()
    my_api = api.api(my_sequencer)

    ttl_dict = {}
    ttl_dict["3"] = 1
    ttl_dict["20"] = 2
    my_api.ttl_set_multiple(ttl_dict)
    my_sequencer.compile_sequence()
    my_sequencer.debug_sequence()
    self.assertEquals(my_sequencer.current_output,[0,0,8,32])
    insn=my_sequencer.current_sequence[1]
    self.assertEquals(insn.output_state,32)


  def test_ttl_multiple_invert(self):
    "test the ttl_set_multiple api function with inverted channels"
    my_sequencer=sequencer.sequencer()
    my_api = api.api(my_sequencer)
    my_api.ttl_sys.ttl_dict["3"].is_inverted = True
    my_api.ttl_sys.ttl_dict["5"].is_inverted = True
    ttl_dict = {}
    ttl_dict["5"] = 1
    ttl_dict["3"] = 0
    ttl_dict["20"] = 2
    my_api.ttl_set_multiple(ttl_dict)
    my_sequencer.compile_sequence()
    my_sequencer.debug_sequence()
    self.assertEquals(my_sequencer.current_output,[0,0,8,32])
    insn=my_sequencer.current_sequence[0]
    self.assertEquals(insn.output_state,0x20)
    insn=my_sequencer.current_sequence[1]
    self.assertEquals(insn.output_state,0x8)


  def test_dac_sequence(self):
    """test if the dac instruction generates the right number of insns
    """
    my_sequencer=sequencer.sequencer()
    my_api = api.api(my_sequencer)
    my_api.dac_value(-12, 1)
    current_seq = my_sequencer.current_sequence
    self.assertEquals(len(current_seq),7)
    del(my_sequencer)

  def test_p_insn(self):
    """Tests the hex value of the p_insn
    """
    p_insn=instructions.p(12,3)
    value=0xc << 28 | 3 << 16 | 12
    test_value=p_insn.get_value()
    self.assertEquals(test_value,value)

  def test_wait_insn(self):
    """Tests the wait instruction
    """
    wait_cycles = 0xaf0
    value = 0x9 << 28 | wait_cycles
    wait_insn = instructions.wait(wait_cycles)
    test_value = wait_insn.get_value()
    self.assertEquals(test_value,value)
    my_sequencer=sequencer.sequencer()
    my_api = api.api(my_sequencer)
    my_api.wait((2**14+100)*0.01)
    current_seq = my_sequencer.current_sequence
    my_sequencer.debug_sequence(force=True)
    insn1 = current_seq[0]
    insn2 = current_seq[1]
    value = 0x9 << 28 | 2**14-1
    value1 = 0x9 << 28 | 100 +1 -4
    self.assertEquals(insn1.get_value(), value)
    self.assertEquals(insn2.get_value(), value1)

  def test_subroutine(self):
    """Test the subroutine calling
    """
    my_sequencer=sequencer.sequencer()
    my_api=api.api(my_sequencer)

    my_api.begin_subroutine("test")
    my_api.dac_value(-12,1)
    my_api.dac_value(-12,1)
    my_api.dac_value(-12,1)
    my_api.end_subroutine()

    my_api.begin_subroutine("test1")
    my_api.dac_value(-0xf,3)
    my_api.dac_value(-0xf,3)
    my_api.dac_value(-0xf,3)
    my_api.end_subroutine()

    my_api.dac_value(-12,1)
    my_api.dac_value(-12,1)
    my_api.call_subroutine("test")
    my_api.call_subroutine("test1")
    my_api.call_subroutine("test")
    my_api.dac_value(-12,1)
    my_sequencer.compile_sequence()
    my_sequencer.debug_sequence(force=False)
    target=my_sequencer.current_sequence[14].target_address
    label=my_sequencer.current_sequence[target].label

    self.assertEquals(target,39)
    self.assertEquals(label,"test")

    target=my_sequencer.current_sequence[18].target_address
    label=my_sequencer.current_sequence[target].label
    self.assertEquals(target,62)
    self.assertEquals(label,"test1")


  def test_subroutine_error_handler(self):
    """Test if the subroutine error handler works correctly
    """
    my_sequencer=sequencer.sequencer()
    my_api=api.api(my_sequencer)
    my_api.begin_subroutine("test")
    my_api.dac_value(-12,1)
    try:
      self.assertRaises(RuntimeError, my_api.begin_subroutine("test1"))
    except RuntimeError:
      None

  def test_j_seq(self):
    """test the jump address
    """
    my_sequencer=sequencer.sequencer()
    my_api=api.api(my_sequencer)
    my_api.dac_value(-12,1)
    my_api.label("test")
    my_api.dac_value(-12,1)
    my_api.jump("test")
    my_sequencer.compile_sequence()
    my_sequencer.current_sequence.pop()
    my_sequencer.current_sequence.pop()
    my_sequencer.current_sequence.pop()
    my_sequencer.current_sequence.pop()
    my_sequencer.debug_sequence(force=False)
    j_insn=my_sequencer.current_sequence[15]
    label_insn=my_sequencer.current_sequence[7]
    self.assertEquals(label_insn.address,7)
    self.assertEquals(label_insn.name,"label")
    self.assertEquals(j_insn.name,"j")
    self.assertEquals(j_insn.target_address,7)
    del(my_sequencer)

  def test_compile_speed(self):
    """Test if 10000 DAC events may be compiled in under 1s
    """
#    psyco.full()
    time1=time.time()
    my_sequencer=sequencer.sequencer()
    my_api=api.api(my_sequencer)
    N0=10000
    my_api.dac_value(-3,1)
    my_api.jump("test")
    for i in range(N0):
        my_api.dac_value(-3,1)
    my_api.label("test")
    my_sequencer.compile_sequence()
    if N0 < 100:
        my_sequencer.debug_sequence()
    #    print my_my_sequencer.word_list
    time2=time.time()
    print str(time2-time1)
    if time2-time1 > 1:
      self.fail("Failed speed test: "+str(time2-time1))


  def test_sequence_length(self):
    """Test maximum sequence length. This test may take some time !!!!
    """
    return None
#    psyco.full()
    time1=time.time()
    my_sequencer=sequencer.sequencer()
    my_api=api.api(my_sequencer)
    N0=1000000
    my_api.dac_value(-3,1)
    my_api.jump("test")
    for i in range(N0):
        my_api.dac_value(-3,1)
    my_api.label("test")
    my_sequencer.compile_sequence()
    print len(my_sequencer.current_sequence)
    if N0 < 100:
        my_sequencer.debug_sequence()
    #    print my_my_sequencer.word_list
    time2=time.time()
    print str(time2-time1)


  def test_finite_loop(self):
    "Testing the finite loop construct"
    my_sequencer=sequencer.sequencer()
    my_api=api.api(my_sequencer)
    my_api.start_finite("finite1", 100)
    my_api.ttl_set_bit("1",1)
    my_api.ttl_set_bit("6",1)
    my_api.start_finite("finite2", 10)
    my_api.ttl_set_bit("18",1)
    my_api.end_finite("finite2")
    my_api.end_finite("finite1")
    my_sequencer.compile_sequence()
    my_sequencer.debug_sequence(force=False)
    ldc_insn1 = my_sequencer.current_sequence[0]
    bdec_insn1 = my_sequencer.current_sequence[15]
    self.assertEquals(ldc_insn1.name,"load const")
    self.assertEquals(ldc_insn1.value,100)
    self.assertEquals(bdec_insn1.name,"bdec")
    self.assertEquals(bdec_insn1.target_address,1)
    self.assertEquals(bdec_insn1.register_address,ldc_insn1.register_address)

#  def tearDown(self):

#------------------------------------------------------------------------------
# Collect all test suites for running
all_suites = unittest.TestSuite((
  unittest.makeSuite(Test_Sequencer)
  ))

def run():
  unittest.TextTestRunner(verbosity=2).run(all_suites)
