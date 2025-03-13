"""Unit tests for config module."""

import unittest
from pathlib import Path
from unittest.mock import patch

from parameterized import parameterized

from backup_to_harddrive.config import (
    extract_valid_configuration_from_config_file,
    extract_valid_configuration_from_configuration_dict,
    get_path_to_config_file_and_initialize_if_none,
)

DUMMY_YAML_FILE = """
backup_configurations:
  backup_of_foo:
    source: /home/foo
    list_of_harddrive:
      - /media/foo
      - /media/bar
    list_of_excluded_folders:
      - ".cache"
      - "/home/foo/.local"
    quick_restore_path:
      - Documents
      - Downloads
  backup_of_bar:
    source: /home/foo/bar
    list_of_harddrive:
      - /media/foo2
      - /media/bar2
    list_of_excluded_folders:
      - "excluded"
"""

ONE_ENTRY_YAML_FILE = """
backup_configurations:
  backup_of_foo:
    source: /home/foo
    list_of_harddrive:
      - /media/foo
      - /media/bar
    list_of_excluded_folders:
      - ".cache"
      - ".local"
"""

FILE_WITHOUT_BACKUP_CONFIGURATIONS = """"
some content
"""

FILE_WITH_EMPTY_BACKUP_CONFIGURATIONS = """"
backup_configurations:
"""
FILE_WITH_NONE_BACKUP_CONFIGURATIONS = """"backup_configurations: None"""

FILE_WITHOUT_SOURCE = """
backup_configurations:
  backup_of_foo:
    list_of_harddrive:
      - /media/foo
      - /media/bar
    list_of_excluded_folders:
      - ".cache"
      - ".local"
"""

FILE_WITHOUT_HARRDRIVE = """
backup_configurations:
  backup_of_foo:
    source: /home/foo
    list_of_excluded_folders:
      - ".cache"
      - ".local"
"""

FILE_WITHOUT_EXCLUDED_FOLDERS = """
backup_configurations:
  backup_of_foo:
    source: /home/foo
    list_of_harddrive:
      - /media/foo
      - /media/bar
"""

FILE_WITH_EXCLUDED_FOLDERS_BUT_EMPTY = """
backup_configurations:
  backup_of_foo:
    source: /home/foo
    list_of_harddrive:
      - /media/foo
      - /media/bar
    list_of_excluded_folders:
"""

EXCLUDED_FILE_OUTSIDE_OF_SOURCE = """
backup_configurations:
  backup_of_foo:
    source: /home/foo
    list_of_harddrive:
      - /media/foo
      - /media/bar
    list_of_excluded_folders:
      - "/home/bar/.cache"
      - ".local"
"""

EMPTY_FILE = """
"""

ONE_RESTORE_PATH = """
backup_configurations:
  backup_of_foo:
    source: /home/foo
    list_of_harddrive:
      - /media/foo
      - /media/bar
    list_of_excluded_folders:
      - ".cache"
      - ".local"
    quick_restore_path:
      - Documents
"""

ONE_EMPTY_RESTORE_PATH = """
backup_configurations:
  backup_of_foo:
    source: /home/foo
    list_of_harddrive:
      - /media/foo
      - /media/bar
    list_of_excluded_folders:
      - ".cache"
      - ".local"
    quick_restore_path:
"""

QUICK_RESTORE_PATH_OUTSIDE_OF_SOURCE = """
backup_configurations:
  backup_of_foo:
    source: /home/foo
    list_of_harddrive:
      - /media/foo
      - /media/bar
    list_of_excluded_folders:
      - ".cache"
      - ".local"
    quick_restore_path:
      - "/home/bar/Documents"
"""

QUICK_RESTORE_PATH_ABSOLUTE_INSIDE_SOURCE = """
backup_configurations:
  backup_of_foo:
    source: /home/foo
    list_of_harddrive:
      - /media/foo
      - /media/bar
    list_of_excluded_folders:
      - ".cache"
      - ".local"
    quick_restore_path:
      - "/home/foo/Documents"
"""


class TestConfig(unittest.TestCase):
    @patch("pathlib.Path.exists", return_value=False)
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.touch")
    def test_get_path_to_config_file_and_initialize_if_none_when_file_does_not_exist(self, mock_touch, mock_mkdir, _):
        config_file_path = get_path_to_config_file_and_initialize_if_none()
        self.assertIsInstance(config_file_path, Path)
        mock_touch.assert_called_once()
        mock_mkdir.assert_called_once()

    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.touch")
    def test_get_path_to_config_file_and_initialize_if_none_when_file_already_exists(self, mock_touch, mock_mkdir, _):
        config_file_path = get_path_to_config_file_and_initialize_if_none()
        self.assertIsInstance(config_file_path, Path)
        mock_touch.assert_not_called()
        mock_mkdir.assert_not_called()


def exists_mock_generator(invalid_path=Path("invalid")):
    """Generate function that mocks pathlib.Path.exists method.

    Args:
        invalid_path (Path, list): Path or list of Path that should be considered as invalid.
    Returns:
        function: Function that mocks pathlib.Path.exists
    """
    if isinstance(invalid_path, Path):

        def exists_mock_path(self):
            return self != invalid_path

        return exists_mock_path

    if isinstance(invalid_path, list):

        def exists_mock_list(self):
            return self not in invalid_path

        return exists_mock_list

    raise NotImplementedError(f"Mock not implemented for argument type: {type(invalid_path)}")


class TestExistsMockGenerator(unittest.TestCase):
    def test_path(self):
        exists_mock = exists_mock_generator(Path("invalid"))
        self.assertTrue(exists_mock(Path("valid")))
        self.assertFalse(exists_mock(Path("invalid")))

    def test_list(self):
        exists_mock = exists_mock_generator([Path("invalid1"), Path("invalid2")])
        self.assertTrue(exists_mock(Path("valid")))
        self.assertFalse(exists_mock(Path("invalid1")))
        self.assertFalse(exists_mock(Path("invalid2")))

    def test_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            exists_mock_generator(1)


class TestReadConfigFromYaml(unittest.TestCase):
    @patch("builtins.open", new_callable=unittest.mock.mock_open, read_data=DUMMY_YAML_FILE)
    @patch(
        "backup_to_harddrive.config.get_path_to_config_file_and_initialize_if_none",
        return_value=Path("/fake/path/config.yaml"),
    )
    def test_read_config_from_yaml_dummy_folder(self, _, __):
        with patch.object(Path, "exists", exists_mock_generator()):
            config = extract_valid_configuration_from_config_file()

            self.assertEqual(len(config.backup_configs), 2)

            backup_foo = config.backup_configs[0]
            self.assertEqual(backup_foo.source, Path("/home/foo"))
            self.assertEqual(backup_foo.list_of_harddrive, [Path("/media/foo"), Path("/media/bar")])
            self.assertEqual(backup_foo.list_of_excluded_folders, [Path("/home/foo/.cache"), Path("/home/foo/.local")])
            self.assertEqual(backup_foo.quick_restore_path, [Path("/home/foo/Documents"), Path("/home/foo/Downloads")])

            backup_bar = config.backup_configs[1]
            self.assertEqual(backup_bar.source, Path("/home/foo/bar"))
            self.assertEqual(backup_bar.list_of_harddrive, [Path("/media/foo2"), Path("/media/bar2")])
            self.assertEqual(backup_bar.list_of_excluded_folders, [Path("/home/foo/bar/excluded")])

    @parameterized.expand(
        [
            ["Empty file", 0, 0, 1, Path("None"), EMPTY_FILE],
            ["No backup configuration", 0, 0, 1, Path("None"), FILE_WITHOUT_BACKUP_CONFIGURATIONS],
            ["Empty backup configuration", 0, 0, 1, Path("None"), FILE_WITH_EMPTY_BACKUP_CONFIGURATIONS],
            ["backup_configuration is None", 0, 0, 1, Path("None"), FILE_WITH_NONE_BACKUP_CONFIGURATIONS],
            ["No source entry", 0, 0, 1, Path("None"), FILE_WITHOUT_SOURCE],
            ["No harddrive entry", 0, 0, 1, Path("None"), FILE_WITHOUT_HARRDRIVE],
            ["No excluded folder entry", 1, 0, 0, Path("None"), FILE_WITHOUT_EXCLUDED_FOLDERS],
            ["Excluded folder present by empty", 1, 1, 0, Path("None"), FILE_WITH_EXCLUDED_FOLDERS_BUT_EMPTY],
            ["File with fully valid entry", 1, 0, 0, Path("None"), ONE_ENTRY_YAML_FILE],
            ["Source does not exists", 0, 0, 1, Path("/home/foo"), ONE_ENTRY_YAML_FILE],
            ["One harddrive not mounted", 1, 0, 1, Path("/media/foo"), ONE_ENTRY_YAML_FILE],
            ["No harddrive mounted", 0, 0, 3, [Path("/media/foo"), Path("/media/bar")], ONE_ENTRY_YAML_FILE],
            ["Excluded outside of source", 1, 1, 0, Path("None"), EXCLUDED_FILE_OUTSIDE_OF_SOURCE],
            ["One quick restore path", 1, 0, 0, Path("None"), ONE_RESTORE_PATH],
            ["One empty restore path", 1, 1, 0, Path("None"), ONE_EMPTY_RESTORE_PATH],
            ["One restore path outside of source", 1, 1, 0, Path("None"), QUICK_RESTORE_PATH_OUTSIDE_OF_SOURCE],
            [
                "Restore path absolute inside of source",
                1,
                0,
                0,
                Path("None"),
                QUICK_RESTORE_PATH_ABSOLUTE_INSIDE_SOURCE,
            ],
        ]
    )
    @patch("logging.warning")
    @patch("logging.error")
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    @patch(
        "backup_to_harddrive.config.get_path_to_config_file_and_initialize_if_none",
        return_value=Path("/fake/path/config.yaml"),
    )
    # pylint: disable=too-many-positional-arguments
    def test_non_nominal_config(
        self,
        _,
        expected_config_number,
        expected_warning_log,
        expected_error_log,
        invalid_path,
        content,
        __,
        mock_open,
        mock_logging_error,
        mock_logging_warning,
    ):
        with patch.object(Path, "exists", exists_mock_generator(invalid_path=invalid_path)):
            mock_open = unittest.mock.mock_open(read_data=content)
            __builtins__["open"] = mock_open
            config = extract_valid_configuration_from_config_file()
            self.assertEqual(len(config.backup_configs), expected_config_number)
            self.assertEqual(mock_logging_warning.call_count, expected_warning_log)
            self.assertEqual(mock_logging_error.call_count, expected_error_log)


class TestExtractValidConfigurationFromConfigurationDict(unittest.TestCase):
    @patch("logging.error")
    def test_extract_valid_configuration_from_configuration_dict(self, mock_error):
        extract_valid_configuration_from_configuration_dict({"backup_configurations": None})
        mock_error.assert_called_once()
