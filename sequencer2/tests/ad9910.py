# Module : bitmask
# Package: pcp.tests
# Unit tests for Bitmask class

import unittest
import time
from sequencer2 import sequencer
from sequencer2 import api
from sequencer2 import instructions
from sequencer2 import ad9910
#------------------------------------------------------------------------------
class Test_AD9910(unittest.TestCase):
  """ Test class for the AD9910
  """
  def test_init_ad9910(self):
    """Test the default DDS registers
    """
    device = ad9910.AD9910(1, 1e3)
    val_cfr1 = device.reg_value_dict[device.CFR1]
    val_cfr2 = device.reg_value_dict[device.CFR2]
    self.assertEquals(val_cfr1, 0x2000)
    self.assertEquals(val_cfr2, 0x5f)

  def test_freq_ad9910(self):
    """Tests the freq profile value of the dds
    """
    device = ad9910.AD9910(1, 1e3)
    device.set_freq_register(1, 10)
    addr_tuple = (0xf, 64)
    val_prof1 = device.reg_value_dict[addr_tuple]
    print val_prof1
    self.assertAlmostEqual(val_prof1, 0x08B50000028F5C29, 64)
#  def tearDown(self):

#------------------------------------------------------------------------------
# Collect all test suites for running
all_suites = unittest.TestSuite((
  unittest.makeSuite(Test_AD9910)
  ))

def run():
  unittest.TextTestRunner(verbosity=2).run(all_suites)
