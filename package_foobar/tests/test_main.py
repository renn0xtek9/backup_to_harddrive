"""Unit test of main."""

import unittest

from package_foobar.main import main


class TestMain(unittest.TestCase):
    def test_main(self):
        with self.assertRaises(NotImplementedError):
            main()
