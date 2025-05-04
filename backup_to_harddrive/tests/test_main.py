"""Unit test of main module."""

import argparse
import unittest
from unittest.mock import patch

from backup_to_harddrive.main import main


class TestMainFunction(unittest.TestCase):

    def setUp(self):
        """Set up the test case."""
        self.patcher = patch("backup_to_harddrive.main.check_if_rsync_is_installed_and_log_if_not")
        self.mock_check_rsync = self.patcher.start()
        self.mock_check_rsync.return_value = True

    @patch("backup_to_harddrive.main.run_backup_from_config_file")
    @patch("backup_to_harddrive.main.set_backup_status")
    @patch("backup_to_harddrive.main.argparse.ArgumentParser.parse_args")
    def test_main_switch_on(self, mock_parse_args, mock_set_backup_status, mock_run):
        mock_parse_args.return_value = argparse.Namespace(switch_on=1, switch_off=None, dry_run=1)

        self.assertEqual(main(), 0)

        mock_set_backup_status.assert_called_once_with(True)
        mock_run.assert_not_called()

    @patch("backup_to_harddrive.main.run_backup_from_config_file")
    @patch("backup_to_harddrive.main.set_backup_status")
    @patch("backup_to_harddrive.main.argparse.ArgumentParser.parse_args")
    def test_main_switch_off(self, mock_parse_args, mock_set_backup_status, mock_run):
        mock_parse_args.return_value = argparse.Namespace(switch_on=None, switch_off=1, dry_run=1)

        self.assertEqual(main(), 0)

        mock_set_backup_status.assert_called_once_with(False)
        mock_run.assert_not_called()

    @patch("backup_to_harddrive.main.is_backup_switched_on")
    @patch("backup_to_harddrive.main.run_backup_from_config_file")
    @patch("backup_to_harddrive.main.argparse.ArgumentParser.parse_args")
    def test_dry_run(self, mock_parse_args, mock_run, mock_get_status):
        mock_parse_args.return_value = argparse.Namespace(switch_on=None, switch_off=None, dry_run=1)
        mock_get_status.return_value = True
        self.assertEqual(main(), 0)
        mock_run.assert_called_with(dry_run=True)

    @patch("backup_to_harddrive.main.is_backup_switched_on")
    @patch("backup_to_harddrive.main.run_backup_from_config_file")
    @patch("backup_to_harddrive.main.argparse.ArgumentParser.parse_args")
    def test_wet_run_switched_on(self, mock_parse_args, mock_run, mock_is_backup_switched_on):
        mock_is_backup_switched_on.return_value = True
        mock_parse_args.return_value = argparse.Namespace(switch_on=None, switch_off=None)
        self.assertEqual(main(), 0)
        mock_run.assert_called_with(dry_run=False)

    @patch("logging.info")
    @patch("backup_to_harddrive.main.is_backup_switched_on")
    @patch("backup_to_harddrive.main.run_backup_from_config_file")
    @patch("backup_to_harddrive.main.argparse.ArgumentParser.parse_args")
    def test_wet_run_switched_off(self, mock_parse_args, mock_run, mock_is_backup_switched_on, mock_log_info):
        mock_is_backup_switched_on.return_value = False
        mock_parse_args.return_value = argparse.Namespace(switch_on=None, switch_off=None, dry_run=1)
        self.assertEqual(main(), 0)
        mock_run.assert_not_called()
        mock_log_info.assert_called()

    @patch("logging.info")
    @patch("backup_to_harddrive.main.is_backup_switched_on")
    @patch("backup_to_harddrive.main.run_backup_from_config_file")
    @patch("backup_to_harddrive.main.argparse.ArgumentParser.parse_args")
    def test_status_when_switched_off(self, mock_parse_args, mock_run, mock_is_backup_switched_on, mock_log_info):
        mock_is_backup_switched_on.return_value = False
        mock_parse_args.return_value = argparse.Namespace(status=1, switch_off=None, dry_run=None)
        self.assertEqual(main(), 2)
        mock_run.assert_not_called()
        mock_log_info.assert_not_called()
        mock_is_backup_switched_on.assert_called()

    @patch("logging.info")
    @patch("backup_to_harddrive.main.is_backup_switched_on")
    @patch("backup_to_harddrive.main.run_backup_from_config_file")
    @patch("backup_to_harddrive.main.argparse.ArgumentParser.parse_args")
    def test_status_when_switched_on(self, mock_parse_args, mock_run, mock_is_backup_switched_on, mock_log_info):
        mock_is_backup_switched_on.return_value = True
        mock_parse_args.return_value = argparse.Namespace(status=1, switch_off=None, dry_run=None)
        self.assertEqual(main(), 0)
        mock_run.assert_not_called()
        mock_log_info.assert_not_called()
        mock_is_backup_switched_on.assert_called()

    @patch("logging.error")
    @patch("backup_to_harddrive.main.is_backup_switched_on")
    @patch("backup_to_harddrive.main.run_backup_from_config_file")
    @patch("backup_to_harddrive.main.argparse.ArgumentParser.parse_args")
    def test_wet_run_rsync_not_installed(self, mock_parse_args, mock_run, mock_is_backup_switched_on, mock_log_error):
        mock_is_backup_switched_on.return_value = True
        mock_parse_args.return_value = argparse.Namespace(switch_on=None, switch_off=None)
        self.mock_check_rsync.return_value = False
        self.assertEqual(main(), 1)
        mock_run.assert_not_called()
        mock_log_error.assert_called()
