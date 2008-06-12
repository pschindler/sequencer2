# Module : __init__
# Package: pcp.tests
# Base module for unit tests in the main pcp package

import unittest


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
import user_function
all_suites.addTest(user_function.all_suites)
def run():
  unittest.TextTestRunner(verbosity=2).run(all_suites)

def debug():
  all_suites.debug()
