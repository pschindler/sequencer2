# Module : bitmask
# Package: pcp.tests
# Unit tests for Bitmask class

import unittest
import time
import logging
from  sequencer2 import sequencer
from  sequencer2 import api
from  sequencer2 import instructions
#------------------------------------------------------------------------------
class Test_Sequencer(unittest.TestCase):




  def test_dac_sequence(self):
    """test if the dac instruction generates the right number of insns
    """
    my_sequencer=sequencer.sequencer()
    my_api = api.api(my_sequencer)
    my_api.dac_value(12, 1)
    current_seq = my_sequencer.current_sequence
    self.assertEquals(len(current_seq),4)
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


  def test_subroutine(self):
    """Test the subroutine calling
    """
    my_sequencer=sequencer.sequencer()
    my_api=api.api(my_sequencer)
    my_api.begin_subroutine("test")
    my_api.dac_value(12,1)
    my_api.dac_value(12,1)
    my_api.dac_value(12,1)
    my_api.end_subroutine()

    my_api.begin_subroutine("test1")
    my_api.dac_value(0xf,3)
    my_api.dac_value(0xf,3)
    my_api.dac_value(0xf,3)
    my_api.end_subroutine()

    my_api.dac_value(12,1)
    my_api.dac_value(12,1)
    my_api.call_subroutine("test")
    my_api.call_subroutine("test1")
    my_api.call_subroutine("test")
    my_api.dac_value(12,1)
    my_sequencer.compile_sequence()
    my_sequencer.debug_sequence()
#    print "\n\n"
    target=my_sequencer.current_sequence[8].target_address
    label=my_sequencer.current_sequence[target].label

    self.assertEquals(target,30)
    self.assertEquals(label,"test")

    target=my_sequencer.current_sequence[12].target_address
    label=my_sequencer.current_sequence[target].label
    self.assertEquals(target,44)
    self.assertEquals(label,"test1")


  def test_subroutine_error_handler(self):
    """Test if the subroutine error handler works correctly
    """
    my_sequencer=sequencer.sequencer()
    my_api=api.api(my_sequencer)
    my_api.begin_subroutine("test")
    my_api.dac_value(12,1)
    try:
      self.assertRaises(RuntimeError, my_api.begin_subroutine("test1"))
    except RuntimeError:
      None

  def test_j_seq(self):
    """test the jump address
    """
    my_sequencer=sequencer.sequencer()
    my_api=api.api(my_sequencer)
    my_api.dac_value(12,1)
    my_api.label("test")
    my_api.dac_value(12,1)
    my_api.jump("test")
    my_sequencer.compile_sequence()
    my_sequencer.current_sequence.pop()
    my_sequencer.current_sequence.pop()
    my_sequencer.current_sequence.pop()
    my_sequencer.current_sequence.pop()
    my_sequencer.debug_sequence()
    j_insn=my_sequencer.current_sequence[9]
    label_insn=my_sequencer.current_sequence[4]
    self.assertEquals(label_insn.address,4)
    self.assertEquals(label_insn.name,"label")
    self.assertEquals(j_insn.name,"j")
    self.assertEquals(j_insn.target_address,4)
    del(my_sequencer)

  def test_compile_speed(self):
    """Test if 10000 DAC events may be compiled in under 1s
    """
    time1=time.time()
    my_sequencer=sequencer.sequencer()
    my_api=api.api(my_sequencer)
    N0=10000
    my_api.dac_value(12,1)
    my_api.jump("test")
    for i in range(N0):
        my_api.dac_value(N0,1)
    my_api.label("test")
    my_sequencer.compile_sequence()
    if N0 < 100:
        my_sequencer.debug_sequence()
    #    print my_my_sequencer.word_list
    time2=time.time()
    print str(time2-time1)
    if time2-time1 > 2:
      self.fail("Failed speed test")

#  def tearDown(self):

#------------------------------------------------------------------------------
# Collect all test suites for running
all_suites = unittest.TestSuite((
  unittest.makeSuite(Test_Sequencer)
  ))

def run():
  unittest.TextTestRunner(verbosity=2).run(all_suites)
