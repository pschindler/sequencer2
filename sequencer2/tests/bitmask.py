# Module : bitmask
# Package: pcp.tests
# Unit tests for Bitmask class

import unittest
from sequencer.pcp         import *
from sequencer.pcp.bitmask import *

#------------------------------------------------------------------------------
class Test_Bitmask(unittest.TestCase):

  def setUp(self):
    self.b1 = Bitmask(label = "b1", width = 5, shift = 2)
    self.b2 = Bitmask(label = "b2", width = 1, shift = 3)
    self.b3 = Bitmask(label = "b3", width = 3, shift = 7)
    self.b4 = Bitmask(label = "b4", width = 3, shift = 0)

  def test_init(self):
    self.assertEquals("b1", self.b1.get_label())
    self.assertEquals(5   , self.b1.get_width())
    self.assertEquals(2   , self.b1.get_shift())
    self.assertEquals(7   , self.b1.get_end())
    self.assertEquals(0x1F, self.b1.get_mask())

  def test_zero(self):
    z = Bitmask(label = "z", width = 0, shift = 1)
    self.assertEquals(0, z.get_shifted_value(0xF))
    # Checks that a zero-width bitmask never overlaps with anything else
    self.assertEquals(False, z.is_overlapping(self.b4))

  def test_get_shifted_value(self):
    self.assertEquals(0x1A << 2, self.b1.get_shifted_value(0x1A))

  def test_check_value(self):
    self.assertRaises(MaskError, self.b1.check_value, 0xFF)
    self.b1.check_value(0x1F)

  def test_get_index_set(self):
    self.assertEquals((2, 3, 4, 5, 6), self.b1.get_index_set())

  def test_is_overlapping(self):
    self.assertEquals(True, self.b1.is_overlapping(self.b1))
    self.assertEquals(True, self.b1.is_overlapping(self.b2))
    self.assertEquals(False, self.b1.is_overlapping(self.b3))

  def test_is_superset(self):
    self.assertEquals(True, self.b1.is_superset(self.b2))
    self.assertEquals(True, self.b1.is_superset(self.b1))
    self.assertEquals(False, self.b2.is_superset(self.b1))
    self.assertEquals(False, self.b1.is_superset(self.b4))

  def test_eq(self):
    self.assertNotEquals(self.b2, self.b1)
    self.assertNotEquals(self.b3, self.b1)
    b4 = Bitmask(label = "b1", width = 5, shift = 2)
    self.assertEquals(b4, self.b1)

  def tearDown(self):
    del self.b1
    del self.b2
    del self.b3

#------------------------------------------------------------------------------
# Collect all test suites for running
all_suites = unittest.TestSuite((
  unittest.makeSuite(Test_Bitmask)
  ))

def run():
  unittest.TextTestRunner(verbosity=2).run(all_suites)
