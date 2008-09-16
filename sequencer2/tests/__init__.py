# Module : __init__
# Package: pcp.tests
# Base module for unit tests in the main pcp package

import unittest
import sequencer2.sequencer

#------------------------------------------------------------------------------
class Test_BaseFunctions(unittest.TestCase):
  test="123"

#------------------------------------------------------------------------------
# Collect all test suites for running
all_suites = unittest.TestSuite((
  unittest.makeSuite(Test_BaseFunctions)
  ))

# Run all sub-test modules in this package by importing them
#import sequencer2.tests.sequencer
import sequencer
import ad9910
all_suites.addTest(sequencer.all_suites)
all_suites.addTest(ad9910.all_suites)
def run():
  unittest.TextTestRunner(verbosity=2).run(all_suites)

def debug():
  all_suites.debug()
