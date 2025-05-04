"""Unit test for backup from config functionality."""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

from backup_to_harddrive.backup_from_config import (
    create_restore_script_for,
    create_restore_scripts_from_config,
    get_list_of_rsync_command_for_this_run_configuration,
    run_backup_from_config_file,
    write_timetsamp_on_harddrive,
)
from backup_to_harddrive.config import BackupConfig, RunConfig


class TestGetListOfRsyncCommandForThisRunConfiguration(unittest.TestCase):
    def test_get_list_of_rsync_command_for_this_run_configuration_empty_config(self):
        empty_config = RunConfig(backup_configs=[])
        self.assertEqual(len(get_list_of_rsync_command_for_this_run_configuration(empty_config)), 0)

    def test_get_list_of_rsync_command_for_this_run_configuration_multiple_config(self):
        dummy_config = RunConfig(
            backup_configs=[
                BackupConfig(
                    source=Path("/home/src1"),
                    list_of_harddrive=[Path("/media/HD1"), Path("/media/HD1")],
                    list_of_excluded_folders=[Path(".cache"), Path(".local")],
                    quick_restore_path=[],
                ),
                BackupConfig(
                    source=Path("/opt/src2"),
                    list_of_harddrive=[Path("/mnt/HD1")],
                    list_of_excluded_folders=[],
                    quick_restore_path=[],
                ),
            ]
        )
        list_of_cmd = get_list_of_rsync_command_for_this_run_configuration(dummy_config)
        self.assertEqual(len(list_of_cmd), 3, msg=[" ".join(cmd) for cmd in list_of_cmd])


class TestRunBackupFromConfig(unittest.TestCase):

    @patch("backup_to_harddrive.backup_from_config.write_timetsamp_on_harddrive")
    @patch("subprocess.Popen")
    @patch("backup_to_harddrive.backup_from_config.extract_valid_configuration_from_config_file")
    @patch("backup_to_harddrive.backup_from_config.get_list_of_rsync_command_for_this_run_configuration")
    def test_run_backup_from_config(self, mock_get_commands, mock_extract, mock_popen, mock_write_timestamp):
        mock_get_commands.return_value = [["rsync", "foo", "bar"], ["rsync", "foo2", "bar2"]]
        mock_extract.return_value = RunConfig(
            backup_configs=[
                BackupConfig(
                    source=Path(),
                    list_of_harddrive=[Path("/media/foo")],
                    list_of_excluded_folders=[],
                    quick_restore_path=[],
                ),
            ]
        )
        mock_process_1 = MagicMock()
        mock_process_2 = MagicMock()
        mock_process_1.wait.return_value = 0
        mock_process_2.wait.return_value = 0
        mock_popen.side_effect = [mock_process_1, mock_process_2]
        run_backup_from_config_file(dry_run=False)
        mock_popen.assert_has_calls([call(["rsync", "foo", "bar"]), call(["rsync", "foo2", "bar2"])])
        mock_process_1.wait.assert_called_once()
        mock_process_2.wait.assert_called_once()
        mock_write_timestamp.assert_called_once()

    @patch("backup_to_harddrive.backup_from_config.write_timetsamp_on_harddrive")
    @patch("logging.info")
    @patch("subprocess.Popen")
    @patch("backup_to_harddrive.backup_from_config.extract_valid_configuration_from_config_file")
    @patch("backup_to_harddrive.backup_from_config.get_list_of_rsync_command_for_this_run_configuration")
    def test_run_backup_from_config_dry_run(
        self, mock_get_commands, _, mock_popen, mock_log_info, mock_write_timestamp
    ):
        mock_get_commands.return_value = [["rsync", "foo", "bar"], ["rsync", "foo2", "bar2"]]

        mock_process_1 = MagicMock()
        mock_process_2 = MagicMock()
        mock_process_1.wait.return_value = 0
        mock_process_2.wait.return_value = 0
        mock_popen.side_effect = [mock_process_1, mock_process_2]
        run_backup_from_config_file(dry_run=True)
        mock_popen.assert_not_called()
        mock_process_1.wait.assert_not_called()
        mock_process_2.wait.assert_not_called()
        mock_log_info.assert_called_once()
        mock_write_timestamp.assert_not_called()


class TestWriteTimetsampOnHarddrive(unittest.TestCase):
    @patch("builtins.open", new_callable=MagicMock)
    def test_write_timetsamp_on_harddrive(self, mock_open):
        mock_file = mock_open.return_value.__enter__.return_value
        write_timetsamp_on_harddrive(Path("/media/foo"))
        mock_open.assert_called_once_with(Path("/media/foo/Backup/timestamp.txt"), "w", encoding="utf-8")
        mock_file.write.assert_called_once()


class TestCreateRestoreScriptFor(unittest.TestCase):

    @patch("builtins.open", new_callable=MagicMock)
    @patch("backup_to_harddrive.backup_from_config.path_to_backup_within_harddrive")
    def test_create_restore_script_for(self, _, mock_file):
        quick_restore_path = Path("/home/foo/Documents")
        hard_drive_path = Path("/media/hd1")
        source_path = Path("/home/foo")

        create_restore_script_for(quick_restore_path, hard_drive_path, source_path)

        # pylint: disable=(unnecessary-dunder-call)
        mock_file.assert_has_calls(
            [
                call().__enter__(),
                call()
                .__enter__()
                .write("#!/bin/bash\nset -euxo pipefail\nrsync -av --delete foo/Documents /home/foo\n"),
                call().__exit__(None, None, None),
            ]
        )


class TestCreateRestoreScriptsFromConfig(unittest.TestCase):
    @patch("backup_to_harddrive.backup_from_config.create_restore_script_for")
    def test_create_restore_scripts_from_config(self, mock_create_restore_script_for):
        create_restore_scripts_from_config(
            BackupConfig(
                source=Path("/home/foo"),
                list_of_harddrive=[Path("/media/hd1")],
                list_of_excluded_folders=[],
                quick_restore_path=[Path("/home/foo/Documents"), Path("/home/foo/Pictures")],
            )
        )
        mock_create_restore_script_for.assert_has_calls(
            [
                call(Path("/home/foo/Documents"), Path("/media/hd1"), Path("/home/foo")),
                call(Path("/home/foo/Pictures"), Path("/media/hd1"), Path("/home/foo")),
            ]
        )
