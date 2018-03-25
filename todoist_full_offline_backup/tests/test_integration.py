#!/usr/bin/python3
""" Integration test """
# pylint: disable=invalid-name
import unittest
#from .. import *

class TestIntegration(unittest.TestCase):
    """ Integration test """

    def test_integration(self):
        """ Integration test
        with patch.object(sys, 'argv',
            ["program", "--verbose", "download", "LATEST", "--token", "xxx"]):
            main()

            # Arrange
            self.assertEqual(1+1, 3)
        """
