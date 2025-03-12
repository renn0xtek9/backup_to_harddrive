"""Module that backups file based on backup configurations."""

import datetime
import logging
import socket
import subprocess
from pathlib import Path
from typing import List

# from backup_to_harddrive.backup import RSYNC_OPTIONS
from backup_to_harddrive.config import (
    RunConfig,
    extract_valid_configuration_from_config_file,
)

RSYNC_OPTIONS = [
    "--mkpath",
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
]


def write_timetsamp_on_harddrive(harddrive_path: Path) -> None:
    """Write a timestamp on the harddrive.

    Args:
        harddrive_path [Path]: The path to the harddrive.
    """
    with open(harddrive_path / "Backup" / "timestamp.txt", "w", encoding="utf-8") as file:
        file.write(str(datetime.datetime.now()))


def path_to_backup_within_harddrive(harddrive_path: Path) -> Path:
    """Get the path to backup within the harddrive.

    Args:
        harddrive_path [Path]: The path to the harddrive.
    """
    return harddrive_path.absolute() / "Backup" / socket.gethostname()


def get_rsync_command_for(source_path: Path, harddrive_path: Path, excluded_path_list: List[Path]) -> List[str]:
    """Get the rsync command to run.

    Args:
        source_path [Path]: The source directory to backup.
        harddrive_path [Path]: The destination directory to backup to.
        excluded_path_list [List]: List of excluded paths.
    """
    return (
        ["rsync"]
        + RSYNC_OPTIONS
        + [f"--exclude={str(excluded_path.absolute())}" for excluded_path in excluded_path_list]
        + [str(source_path.absolute()), str(path_to_backup_within_harddrive(harddrive_path))]
    )


def get_list_of_rsync_command_for_this_run_configuration(run_config: RunConfig) -> List[List[str]]:
    """Get the list of rsync commands to run for this run configuration.

    Args:
        run_config [RunConfig]: The run configuration to use.
    """
    all_commands = []
    for backup_config in run_config.backup_configs:
        for harddrive in backup_config.list_of_harddrive:
            all_commands.append(
                get_rsync_command_for(backup_config.source, harddrive, backup_config.list_of_excluded_folders)
            )
    return all_commands


def run_backup_from_config_file(dry_run=False) -> None:
    """Run the backup based on the configuration.

    Args:
        dry_run [bool]: If True, the backup will not be executed. Rsync commands will only be printed.
    """
    run_config = extract_valid_configuration_from_config_file()
    rsync_commands = get_list_of_rsync_command_for_this_run_configuration(run_config)

    # pylint: disable=(consider-using-with)
    if not dry_run:
        processes = [subprocess.Popen(cmd) for cmd in rsync_commands]
        for proc in processes:
            proc.wait()
        for backup_config in run_config.backup_configs:
            for harddrive in backup_config.list_of_harddrive:
                write_timetsamp_on_harddrive(harddrive)
    else:
        logging.info("Dry run mode enabled. The following commands would be executed")
        for cmd in rsync_commands:
            print(" ".join(cmd))
