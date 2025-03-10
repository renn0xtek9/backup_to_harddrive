"""Unit test of backup module."""

import argparse
import codecs
import datetime
import os
import socket
import tempfile
import unittest
from pathlib import Path
from unittest.mock import call, mock_open, patch

from backup_to_harddrive.backup import (
    add_today_as_save_date,
    copy_restore_scripts,
    get_backup_status,
    get_destination_path,
    get_list_of_harddrive_to_backup,
    get_path_for_backup_status,
    get_path_to_backup_date_list,
    get_path_to_disk,
    get_path_to_list_of_harddrives,
    get_rsync_command,
    get_source,
    main,
    run,
    set_backup_status,
)

HOME = os.getenv("HOME")
USER = os.getenv("USER")


def create_a_dummy_harddrives_file(filepath: str) -> None:
    """Create a dummy harddrives file."""
    with codecs.open(filepath, "w", encoding="utf_8") as file:
        file.write("foo\n")
        file.write("bar\n")
        file.write("an/idiot/tried/to/put/relative_path_to_a_harddrive\n")
        file.close()


class TestGetListOfHarddriveToBackup(unittest.TestCase):
    def setUp(self):
        self.dummy_harddrives_file = tempfile.mktemp()
        create_a_dummy_harddrives_file(self.dummy_harddrives_file)

    def test_get_list_of_harddrive_to_backup_returns_correct_list(self):
        harddrives = get_list_of_harddrive_to_backup(self.dummy_harddrives_file)
        self.assertEqual(len(harddrives), 3)
        self.assertEqual(harddrives, ["foo", "bar", "relative_path_to_a_harddrive"])


class TestGettingInformation(unittest.TestCase):
    def test_get_path_to_list_of_harddrives_returns_correct_path(self):
        self.assertEqual(get_path_to_list_of_harddrives(), Path(HOME + "/.backup/harddrives.txt"))

    def test_get_path_to_disk_gives_correct_path(self):
        self.assertEqual(get_path_to_disk("foo"), Path("/media/" + USER + "/foo"))

    def test_get_destination(self):
        self.assertEqual(
            get_destination_path("foo", "dellPC"),
            Path("/media/" + USER + "/foo/Backup/dellPC"),
        )

    def test_get_path_for_backup_status(self):
        self.assertEqual(
            get_path_for_backup_status(),
            Path("/home/" + USER + "/.backup/backup_status.txt"),
        )

    def test_get_backup_status_file_does_no_yet_exist(self):
        self.assertTrue(get_backup_status("/whatever"))

    def test_get_backup_status_return_false_if_off(self):
        backup_status_file = tempfile.mktemp()
        with codecs.open(backup_status_file, "w", encoding="utf_8") as file:
            file.write("Off")
        self.assertFalse(get_backup_status(backup_status_file))

    def test_get_backup_status_return_true_if_off(self):
        backup_status_file = tempfile.mktemp()
        with codecs.open(backup_status_file, "w", encoding="utf_8") as file:
            file.write("On")
        self.assertTrue(get_backup_status(backup_status_file))

    @patch("codecs.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_set_backup_status(self, _, mock_open):
        set_backup_status(False)
        mock_open.assert_called_with(str(get_path_for_backup_status().absolute()), "w+", encoding="utf_8")
        mock_open().write.assert_called_with("Off")

        set_backup_status(True)
        mock_open.assert_called_with(str(get_path_for_backup_status().absolute()), "w+", encoding="utf_8")
        mock_open().write.assert_called_with("On")

    def test_get_path_to_backup_date_list(self):
        self.assertTrue(
            get_path_to_backup_date_list("foo", "dellPC"),
            Path("/media/" + USER + "/foo/Backup/dellPC/backup_date_liste.txt"),
        )

    def test_get_source(self):
        self.assertEqual(get_source(), Path(HOME))


class TestAddTodayAsSaveDate(unittest.TestCase):

    @patch("codecs.open", new_callable=mock_open)
    @patch("backup_to_harddrive.backup.datetime")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.is_file")
    def test_add_today_as_save_date_if_file_exist(self, mock_is_file, _, mock_datetime, mock_file):
        mock_is_file.return_value = True
        mock_datetime.datetime.now.return_value = datetime.datetime(2023, 10, 10)
        mock_datetime.datetime.strftime = datetime.datetime.strftime

        add_today_as_save_date("foo", "dellPC")

        backupdatelistpath = get_path_to_backup_date_list("foo", "dellPC")
        mock_file.assert_called_with(backupdatelistpath, "a", encoding="utf_8")
        mock_file().write.assert_called_with("\n10_10_2023")

    @patch("codecs.open", new_callable=mock_open)
    @patch("backup_to_harddrive.backup.datetime")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.is_file")
    def test_add_today_as_save_date_if_file_does_not_exist(self, mock_is_file, _, mock_datetime, mock_file):
        mock_is_file.return_value = False
        mock_datetime.datetime.now.return_value = datetime.datetime(2023, 10, 10)
        mock_datetime.datetime.strftime = datetime.datetime.strftime

        add_today_as_save_date("foo", "dellPC")

        backupdatelistpath = get_path_to_backup_date_list("foo", "dellPC")
        # pylint: disable=(unnecessary-dunder-call)
        mock_file.assert_has_calls(
            [
                call(backupdatelistpath, "w", encoding="utf_8"),
                call().__enter__(),
                call().write("List of Backup date"),
                call().__exit__(None, None, None),
                call(backupdatelistpath, "a", encoding="utf_8"),
                call().__enter__(),
                call().write("\n10_10_2023"),
                call().__exit__(None, None, None),
            ]
        )


class TestCopyRestoreScripts(unittest.TestCase):
    def test_copy_restore_scripts(self):
        directory = tempfile.mkdtemp()
        print(directory)
        copy_restore_scripts(directory)


RUN_SCRIPT_DIR_PATH = Path(os.path.dirname(os.path.realpath(__file__))).parent / "src" / "backup_to_harddrive"


class TestGetRsyncCommand(unittest.TestCase):
    def test_get_rsync_command(self):
        source = "/home/user"
        destination = "/media/user/backup"
        # pylint: disable=(duplicate-code)
        expected_command = [
            "rsync",
            "--delete",
            "--delete-before",
            "--update",
            "--progress",
            "-t",
            "-a",
            "-r",
            "-v",
            "-E",
            "-c",
            "-h",
            "--exclude-from",
            str(RUN_SCRIPT_DIR_PATH / "excludelist.txt"),
            source,
            destination,
        ]
        self.assertEqual(get_rsync_command(source, destination), expected_command)


class TestRun(unittest.TestCase):
    @patch("backup_to_harddrive.backup.get_backup_status")
    @patch("backup_to_harddrive.backup.get_list_of_harddrive_to_backup")
    @patch("backup_to_harddrive.backup.get_path_to_list_of_harddrives")
    @patch("backup_to_harddrive.backup.get_path_to_disk")
    @patch("subprocess.Popen")
    @patch("backup_to_harddrive.backup.add_today_as_save_date")
    @patch("backup_to_harddrive.backup.copy_restore_scripts")
    @patch("pathlib.Path.is_dir")
    # pylint: disable=(too-many-positional-arguments)
    def test_run_backup_enabled(
        self,
        mock_isdir,
        mock_copy_restore_scripts,
        mock_add_today_as_save_date,
        mock_popen,
        mock_get_path_to_disk,
        mock_get_path_to_list_of_harddrives,
        mock_get_list_of_harddrive_to_backup,
        mock_get_backup_status,
    ):
        mock_isdir.return_value = True
        mock_get_backup_status.return_value = True
        mock_get_list_of_harddrive_to_backup.return_value = ["disk1"]
        mock_get_path_to_list_of_harddrives.return_value = "/dummy/path/to/harddrives.txt"
        mock_get_path_to_disk.return_value = Path("/media/user/disk1")
        mock_popen.return_value.wait.return_value = None

        run()

        mock_get_backup_status.assert_called_once()
        mock_get_list_of_harddrive_to_backup.assert_called_once_with("/dummy/path/to/harddrives.txt")
        mock_get_path_to_disk.assert_has_calls([call("disk1"), call("disk1")])
        mock_popen.assert_called_once()
        mock_add_today_as_save_date.assert_called_once_with("disk1", socket.gethostname())
        mock_copy_restore_scripts.assert_called_once_with(Path("/media/user/disk1/Backup", socket.gethostname()))

    @patch("backup_to_harddrive.backup.get_backup_status")
    @patch("backup_to_harddrive.backup.get_list_of_harddrive_to_backup")
    @patch("backup_to_harddrive.backup.get_path_to_list_of_harddrives")
    @patch("backup_to_harddrive.backup.get_path_to_disk")
    @patch("subprocess.Popen")
    @patch("backup_to_harddrive.backup.add_today_as_save_date")
    @patch("backup_to_harddrive.backup.copy_restore_scripts")
    @patch("pathlib.Path.is_dir")
    # pylint: disable=(too-many-positional-arguments)
    def test_run_harddrive_not_mounted(
        self,
        mock_isdir,
        mock_copy_restore_scripts,
        mock_add_today_as_save_date,
        mock_popen,
        mock_get_path_to_disk,
        mock_get_path_to_list_of_harddrives,
        mock_get_list_of_harddrive_to_backup,
        mock_get_backup_status,
    ):
        mock_isdir.return_value = False
        mock_get_backup_status.return_value = True
        mock_get_list_of_harddrive_to_backup.return_value = ["disk1"]
        mock_get_path_to_list_of_harddrives.return_value = "/dummy/path/to/harddrives.txt"
        mock_get_path_to_disk.return_value = Path("/media/user/disk1")
        mock_popen.return_value.wait.return_value = None

        run()

        mock_get_backup_status.assert_called_once()
        mock_get_list_of_harddrive_to_backup.assert_called_once_with("/dummy/path/to/harddrives.txt")
        mock_get_path_to_disk.assert_has_calls([call("disk1"), call("disk1")])
        mock_popen.assert_not_called()
        mock_add_today_as_save_date.assert_not_called()
        mock_copy_restore_scripts.assert_not_called()

    @patch("backup_to_harddrive.backup.get_backup_status")
    def test_run_backup_disabled(self, mock_get_backup_status):
        mock_get_backup_status.return_value = False

        run()

        mock_get_backup_status.assert_called_once()


class TestMainFunction(unittest.TestCase):
    @patch("backup_to_harddrive.backup.run")
    @patch("backup_to_harddrive.backup.set_backup_status")
    @patch("backup_to_harddrive.backup.argparse.ArgumentParser.parse_args")
    def test_main_switch_on(self, mock_parse_args, mock_set_backup_status, mock_run):
        mock_parse_args.return_value = argparse.Namespace(switch_on=1, switch_off=None)

        self.assertEqual(main(), 0)

        mock_set_backup_status.assert_called_once_with(True)
        mock_run.assert_not_called()

    @patch("backup_to_harddrive.backup.run")
    @patch("backup_to_harddrive.backup.set_backup_status")
    @patch("backup_to_harddrive.backup.argparse.ArgumentParser.parse_args")
    def test_main_switch_off(self, mock_parse_args, mock_set_backup_status, mock_run):
        mock_parse_args.return_value = argparse.Namespace(switch_on=None, switch_off=1)

        self.assertEqual(main(), 0)

        mock_set_backup_status.assert_called_once_with(False)
        mock_run.assert_not_called()

    @patch("backup_to_harddrive.backup.run")
    @patch("backup_to_harddrive.backup.set_backup_status")
    @patch("backup_to_harddrive.backup.argparse.ArgumentParser.parse_args")
    def test_main_run(self, mock_parse_args, mock_set_backup_status, mock_run):
        mock_parse_args.return_value = argparse.Namespace(switch_on=None, switch_off=None)

        self.assertEqual(main(), 0)

        mock_set_backup_status.assert_not_called()
        mock_run.assert_called_once()
