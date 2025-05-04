"""Unit tests for rsync installation checks."""

import unittest
from unittest.mock import patch

from parameterized import parameterized

from backup_to_harddrive.rsync_installation_check import (
    RSYNC_NOT_INSTALL_LOG_MSG,
    check_if_rsync_is_installed_and_log_if_not,
)


class TestRsyncInstallationCheck(unittest.TestCase):

    @parameterized.expand(
        [
            ["dry_run enabled - rsync installed", True, True, False, False],
            ["dry_run not enabled - rsync installed", False, True, False, False],
            ["dry_run enabled - rsync not installed", True, False, False, True],
            ["dry_run not enabled - rsync not installed", False, False, True, False],
        ]
    )
    @patch("logging.warning")
    @patch("logging.error")
    def test_rsync_installed_dry_run(  # pylint: disable=(too-many-positional-arguments)
        self,
        _,
        dry_run_enabled,
        rsync_installed,
        log_error_expected,
        log_warning_expected,
        mock_log_error,
        mock_log_warning,
    ):
        """Test that rsync is installed."""
        with patch("shutil.which", return_value="/usr/bin/rsync" if rsync_installed else None):
            result = check_if_rsync_is_installed_and_log_if_not(dry_run_enabled=dry_run_enabled)
            self.assertEqual(result, rsync_installed)
            if log_error_expected:
                mock_log_error.assert_called_once_with(RSYNC_NOT_INSTALL_LOG_MSG)
            else:
                mock_log_error.assert_not_called()
            if log_warning_expected:
                mock_log_warning.assert_called_once_with(RSYNC_NOT_INSTALL_LOG_MSG)
            else:
                mock_log_warning.assert_not_called()
