"""Test backup status functionality."""

import unittest
from unittest.mock import mock_open, patch

from backup_to_harddrive.backup_status import (
    get_path_for_backup_status,
    is_backup_switched_on,
    set_backup_status,
)


class TestBackupStatus(unittest.TestCase):

    def test_get_path_for_backup_status(self):
        self.assertTrue(".config/backup_to_harddrive/backup_status.txt" in str(get_path_for_backup_status()))

    @patch("builtins.open")
    def test_get_backup_status_when_file_does_not_exist(self, mock_open_file):
        mock_open_file.side_effect = FileNotFoundError
        self.assertTrue(is_backup_switched_on())

    @patch("builtins.open", mock_open(read_data="On"))
    def test_get_backup_status_when_file_contains_on(self):
        self.assertTrue(is_backup_switched_on())

    @patch("builtins.open", mock_open(read_data="Off"))
    def test_get_backup_status_when_file_contains_off(self):
        self.assertFalse(is_backup_switched_on())

    @patch("codecs.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_set_backup_status(self, _, mock_open_file):
        set_backup_status(False)
        mock_open_file.assert_called_with(str(get_path_for_backup_status().absolute()), "w+", encoding="utf_8")
        mock_open_file().write.assert_called_with("Off")

        set_backup_status(True)
        mock_open_file.assert_called_with(str(get_path_for_backup_status().absolute()), "w+", encoding="utf_8")
        mock_open_file().write.assert_called_with("On")
