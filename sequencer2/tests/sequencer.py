# Module : bitmask
# Package: pcp.tests
# Unit tests for Bitmask class

import unittest
import sys
import time
import logging
USE_PSYCO = False
if USE_PSYCO:
  try:
    import psyco
  except:
    print("Psyco not found")
from  sequencer2 import sequencer
from  sequencer2 import api
from  sequencer2 import instructions
from  sequencer2 import outputsystem
from  sequencer2 import comm
#------------------------------------------------------------------------------
class Test_Sequencer(unittest.TestCase):

  def test_python_version(self):
    "checks if we are running a proper python version"
    print sys.version_info[0]
    if sys.version_info[0] > 2:
      self.fail("We are running a wrong python version !!!")

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

  def test_icnt(self):
    raise NotImplementedError

  def test_wtr(self):
    my_sequencer=sequencer.sequencer()
    my_api = api.api(my_sequencer)
    my_api.ttl_set_bit("18",1)
    my_api.ttl_set_bit("12",1)
    my_api.wait_trigger(0xf)
    my_api.ttl_set_bit("1",1)
    my_api.ttl_set_bit("6",1)
    my_sequencer.compile_sequence()
    my_sequencer.debug_sequence()
    my_comm = comm.PTPComm(nonet=True)
    my_comm.savebin(my_sequencer.word_list)


  def test_save_file(self):
    my_sequencer=sequencer.sequencer()
    my_api = api.api(my_sequencer)
    my_api.ttl_set_bit("1",1)
    my_api.ttl_set_bit("6",1)
    my_api.ttl_set_bit("18",1)
    my_sequencer.compile_sequence()
    my_sequencer.debug_sequence()
    my_comm = comm.PTPComm(nonet=True)
#    my_comm.savebin(my_sequencer.word_list)

  def test_ttl_multiple(self):
    "test the ttl_set_multiple api function"
    my_sequencer=sequencer.sequencer()
    my_api = api.api(my_sequencer)

    ttl_dict = {}
    ttl_dict["3"] = 1
    ttl_dict["20"] = 1 #FIXME ????
    my_api.ttl_set_multiple(ttl_dict)
    my_sequencer.compile_sequence()
    my_sequencer.debug_sequence()
    self.assertEquals(my_sequencer.current_output,[0,0,8,16])
    insn=my_sequencer.current_sequence[1]
    self.assertEquals(insn.output_state,16)


  def test_ttl_multiple_invert(self):
    "test the ttl_set_multiple api function with inverted channels"
    my_sequencer=sequencer.sequencer()
    my_api = api.api(my_sequencer)
    my_api.ttl_sys.ttl_dict["3"].is_inverted = True
    my_api.ttl_sys.ttl_dict["5"].is_inverted = True
    ttl_dict = {}
    ttl_dict["5"] = 1
    ttl_dict["3"] = 0
    ttl_dict["20"] = 1
    my_api.ttl_set_multiple(ttl_dict)
    my_sequencer.compile_sequence()
    my_sequencer.debug_sequence()
    self.assertEquals(my_sequencer.current_output,[0,0,8,16])
    insn=my_sequencer.current_sequence[0]
    self.assertEquals(insn.output_state,0x10)
    insn=my_sequencer.current_sequence[1]
    self.assertEquals(insn.output_state,0x8)


  def test_dac_sequence(self):
    """test if the dac instruction generates the right number of insns
    """
    my_sequencer=sequencer.sequencer()
    my_api = api.api(my_sequencer)
    my_api.dac_value(-12, 1)
    current_seq = my_sequencer.current_sequence
    my_sequencer.debug_sequence(force=False)
    self.assertEquals(len(current_seq),13)
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
    # The maximum wait time is 2^14 .
    # So if the wait time is bigger than this the command should be splitted up into
    # two commands. We check this here
    my_api = api.api(my_sequencer)
    cycles = (2**14+100)
    my_api.wait(cycles*0.01)
    current_seq = my_sequencer.current_sequence
    my_sequencer.debug_sequence(force=False)
    insn1 = current_seq[0]
    insn2 = current_seq[6]
    value = 0x9 << 28 | 2**14-1
    value1 = 0x9 << 28 | 100 - 1 - 2 * 5
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
    target_list = []
    for my_ins in my_sequencer.current_sequence:
      if my_ins.name == "call":
        target_list.append(my_ins.target_address)
    label_list = ['test', 'test1', 'test']
    for target in target_list:
      print target
      label=my_sequencer.current_sequence[target].label
      self.assertEquals(label, label_list.pop())


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
    target_list = []
    for my_ins in my_sequencer.current_sequence:
      if my_ins.name == "j":
        target_list.append(my_ins.target_address)
    label_list = ['test']
    for target in target_list:
      print target
      label=my_sequencer.current_sequence[target].label
      self.assertEquals(label, label_list.pop())
    del(my_sequencer)

  def test_compile_speed(self):
    """Test if 10000 DAC events may be compiled in under 1s
    """
    time1=time.time()
    try:
      psyco.full()
    except:
      print("Psyco not installed")

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

if __name__ == '__main__':
  print "running: "
  run()
