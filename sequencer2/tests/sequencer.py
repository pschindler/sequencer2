# Module : bitmask
# Package: pcp.tests
# Unit tests for Bitmask class

import unittest
import time
from  sequencer2 import sequencer
#------------------------------------------------------------------------------
class Test_Sequencer(unittest.TestCase):

#  def setUp(self):


  def test_p(self):
    """
    test if the p instruction generates the right number of insns
    """
    my_sequencer=sequencer.sequencer()
    my_sequencer.dac_value(12,1)
    current_seq=my_sequencer.current_sequence
    self.assertEquals(len(current_seq),3)
    del(my_sequencer)
#    my_sequencer.current_sequence=[]

  def test_j(self):
    """
    test the jump address
    """
    my_sequencer=sequencer.sequencer()
    my_sequencer.dac_value(12,1)
    my_sequencer.label("test")
    my_sequencer.dac_value(12,1)
    my_sequencer.jump("test")
    my_sequencer.compile_sequence()
    my_sequencer.current_sequence.pop()
    my_sequencer.current_sequence.pop()
    my_sequencer.current_sequence.pop()
    j_insn=my_sequencer.current_sequence.pop()
    label_insn=my_sequencer.current_sequence[3]
    self.assertEquals(label_insn.address,3)
    self.assertEquals(label_insn.name,"label")
    self.assertEquals(j_insn.name,"j")
    self.assertEquals(j_insn.target_address,3)
    del(my_sequencer)

  def test_compile_speed(self):
    """
    Test if 10000 DAC events may be compiled in under 1s
    """
    time1=time.time()
    my_sequencer=sequencer.sequencer()
    N0=10000
    my_sequencer.dac_value(12,1)
    my_sequencer.jump("test")
    for i in range(N0):
        my_sequencer.dac_value(N0,1)
    my_sequencer.label("test")
    my_sequencer.compile_sequence()
    if N0 < 100:
        my_sequencer.debug_sequence()
    #    print my_my_sequencer.word_list
    time2=time.time()
    print str(time2-time1)
    if time2-time1 > 1:
      self.fail("Failed speed test")

#  def tearDown(self):

#------------------------------------------------------------------------------
# Collect all test suites for running
all_suites = unittest.TestSuite((
  unittest.makeSuite(Test_Sequencer)
  ))

def run():
  unittest.TextTestRunner(verbosity=2).run(all_suites)
