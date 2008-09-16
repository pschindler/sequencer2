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
    """Test the default ad9910 registers
    """
    device = ad9910.AD9910(1, 1e3)
    val_cfr1 = device.reg_value_dict[device.CFR1]
    val_cfr2 = device.reg_value_dict[device.CFR2]
    print ""
    print hex(val_cfr1)
    print hex(val_cfr2)
    self.assertEquals(val_cfr1, 0x2000)
    self.assertEquals(val_cfr2, 0x50)

  def test_freq_ad9910(self):
    """Tests the freq profile value of the ad9910
    """
    device = ad9910.AD9910(1, 1e3)
    device.set_freq_register(1, 10)
    addr_tuple = (0xf, 64)
    val_prof1 = device.reg_value_dict[addr_tuple]
    print ""
    print hex(val_prof1)
    self.assertAlmostEqual(val_prof1, 0x08B50000028F5C29, 64)
    #def tearDown(self):
  def test_api_ad9910(self):
    """Tests the api functions for the ad9910
    """
    dds_device = ad9910.AD9910(1, 1e3)
    my_sequencer=sequencer.sequencer()
    my_api=api.api(my_sequencer)
    my_api.init_dds(dds_device)
    my_sequencer.compile_sequence()
    my_sequencer.debug_sequence()

  def test_freq_api_ad9910(self):
    "Tests the API set freq fcuntion for the ad9910"
    dds_device = ad9910.AD9910(1, 1e3)
    my_sequencer=sequencer.sequencer()
    my_api=api.api(my_sequencer)
    my_api.init_dds(dds_device)
    my_api.set_dds_freq(dds_device, 300, 2)
    my_sequencer.compile_sequence()
    my_sequencer.debug_sequence()
#------------------------------------------------------------------------------
# Collect all test suites for running
all_suites = unittest.TestSuite((
  unittest.makeSuite(Test_AD9910)
  ))

def run():
  unittest.TextTestRunner(verbosity=2).run(all_suites)
