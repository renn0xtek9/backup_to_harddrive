"""Example of unittest file"""

import unittest

from package_foobar.example import return_two


class TestReturnTwo(unittest.TestCase):
    def test_return_two(self):
        self.assertEqual(2, return_two())
