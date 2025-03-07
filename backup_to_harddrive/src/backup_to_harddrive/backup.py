#!/usr/bin/env python3
"""Backup to harddrive module."""

import argparse
import codecs
import datetime
import getpass
import os
import shutil
import socket
import subprocess
from pathlib import Path

SCRIPT_DIR_PATH = Path(os.path.dirname(os.path.realpath(__file__)))
RSYNC_OPTIONS = [
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
EXCLUDE_LIST_FILE_PATH = Path(SCRIPT_DIR_PATH, "excludelist.txt")


def get_rsync_command(source, destination):
    """Get the rsync command to run.

    Args:
        source (str): The source directory to backup.
        destination (str): The destination directory to backup to.
    Returns:
        list: The rsync command to run.
    """
    return ["rsync"] + RSYNC_OPTIONS + ["--exclude-from", str(EXCLUDE_LIST_FILE_PATH.absolute()), source, destination]


def get_list_of_harddrive_to_backup(filepath):
    """Get the list of harddrives to backup.

    Args:
        filepath (str): The path to the file containing the list of harddrives to backup.
    Returns:
        list: The list of harddrives to backup.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        harddriveslist = [os.path.basename(line.rstrip("\n")) for line in f]

    return harddriveslist


def get_path_to_list_of_harddrives():
    """Get the path to the file containing the list of harddrives to backup.

    Returns:
        str: The path to the file containing the list of harddrives to backup.
    """
    return os.path.expanduser("~") + "/.backup/harddrives.txt"


def get_path_to_backup_date_list(diskname, hostname):
    """Get the path to the file containing the list of backup dates.

    Args:
        diskname (str): The name of the disk to backup to.
        hostname (str): The hostname of the machine.
    Returns:
        str: The path to the file containing the list of backup dates.
    """
    return Path(
        "/media/",
        getpass.getuser(),
        diskname,
        "Backup",
        hostname,
        "backup_date_list.txt",
    )


def get_path_for_backup_status():
    """Get the path to the file containing the backup status.

    Returns:
        str: The path to the file containing the backup status.
    """
    return Path(os.path.expanduser("~"), ".backup", "backup_status.txt")


def get_backup_status(filename=get_path_for_backup_status()):
    """Get the backup status.

    Args:
        filename (str): The path to the file containing the backup status.
    Returns:
        bool: The backup status.
    """
    try:
        with open(filename, "r", encoding="utf-8") as file:
            content = [line.rstrip("\n") for line in file]
        return content[0] == "On"
    except FileNotFoundError:
        print("Backup status file not found")
        return True


def get_path_to_disk(diskname):
    """Get the path to the disk.

    Args:
        diskname (str): The name of the disk.
    Returns:
        str: The path to the disk.
    """
    return Path("/media/" + getpass.getuser() + "/" + diskname)


def get_source():
    """Get the source directory to backup.

    Returns:
        str: The source directory to backup.
    """
    return Path(os.path.expanduser("~"))


def get_destination(diskname, hostname):
    """Get the destination directory to backup to.

    Args:
        diskname (str): The name of the disk.
        hostname (str): The hostname of the machine.
    Returns:
        str: The destination directory to backup to.
    """
    return Path(get_path_to_disk(diskname), "Backup", hostname)


def create_path_if_necessary(path):
    """Create a path if it does not exist.

    Args:
        path (str): The path to create.
    """
    if not os.path.isdir(str(path.absolute())):
        os.makedirs(str(path.absolute()))


def set_backup_status(on_or_off):
    """Set the backup status.

    Args:
        on_or_off (bool): The backup status.
    """
    create_path_if_necessary(get_path_for_backup_status().parent)
    with codecs.open(str(get_path_for_backup_status().absolute()), "w", encoding="utf_8") as file:
        if on_or_off:
            file.write("On")
        else:
            file.write("Off")


def add_today_as_save_date(diskname, hostname):
    """Add today as a save date.

    Args:
        diskname (str): The name of the disk.
        hostname (str): The hostname of the machine.
    """
    backupdatelistpath = get_path_to_backup_date_list(diskname, hostname)
    create_path_if_necessary(backupdatelistpath.parent)
    if not os.path.isfile(backupdatelistpath):
        with codecs.open(backupdatelistpath, "w", encoding="utf_8") as file:
            file.write("List of Backup date")
    with codecs.open(backupdatelistpath, "a", encoding="utf_8") as file:
        now = datetime.datetime.now()
        file.write("\n" + now.strftime("%d_%m_%Y"))


def get_restore_script_path():
    """Get the path to the restore scripts.

    Returns:
        str: The path to the restore scripts.
    """
    return Path(SCRIPT_DIR_PATH, "quick_restore_scripts")


def copy_restore_scripts(destination):
    """Copy the restore scripts to the destination.

    Args:
        destination (str): The destination to copy the restore scripts to.
    """
    restore_script_path = get_restore_script_path()
    scripts = [
        Path(restore_script_path, f)
        for f in os.listdir(restore_script_path)
        if os.path.isfile(os.path.join(restore_script_path, f))
    ]
    for scriptpath in scripts:
        print(scriptpath)
        shutil.copy2(scriptpath, destination)


def run():
    """Run the backup."""
    if get_backup_status() is False:
        return

    hostname = socket.gethostname()
    for diskname in get_list_of_harddrive_to_backup(get_path_to_list_of_harddrives()):
        if os.path.isdir(get_path_to_disk(diskname)):
            command = get_rsync_command(str(get_source().absolute()), str(get_destination(diskname, hostname)))
            print(" ".join(command))
            with subprocess.Popen(command) as spc:
                spc.wait()

            add_today_as_save_date(diskname, hostname)
            copy_restore_scripts(get_destination(diskname, hostname))
        else:
            print(f"Harddrive not mounted: {get_path_to_disk(diskname)}")


def main():
    """Implement main function."""
    parser = argparse.ArgumentParser(description="Script that performs backup of home directory")
    parser.add_argument("--switch-on", help="Switch the backup functionality on", action="count")
    parser.add_argument("--switch-off", help="Switch the backup functionality off", action="count")
    args = parser.parse_args()

    if args.switch_on == 1:
        set_backup_status(True)
        return 0
    if args.switch_off == 1:
        set_backup_status(False)
        return 0

    run()
    return 0


if __name__ == "__main__":
    main()  # pragma: no cover
