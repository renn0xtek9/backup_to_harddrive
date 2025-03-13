"""Main function."""

import argparse
import logging

from backup_to_harddrive.backup_from_config import run_backup_from_config_file
from backup_to_harddrive.backup_status import is_backup_switched_on, set_backup_status


def main() -> int:
    """Implement main function.

    Returns:
        Int : 0 if the function runs successfully.
    """
    parser = argparse.ArgumentParser(description="Script that performs backup of home directory")
    parser.add_argument(
        "--dry-run",
        help="Perform dry run (Displays rsync commands without execution)",
        action="count",
        required=False,
        default=0,
    )
    parser.add_argument("--switch-on", help="Switch the backup functionality on", action="count")
    parser.add_argument("--switch-off", help="Switch the backup functionality off", action="count")
    parser.add_argument("--status", help="Get the status of the backup", action="count")
    args = parser.parse_args()

    dry_run = "dry_run" in args and args.dry_run == 1

    if "status" in args and args.status == 1:
        if is_backup_switched_on():
            print("Backup is switched on.")
            return 0
        print("Backup is switched off.")
        return 2

    if args.switch_on == 1:
        set_backup_status(True)
        logging.info("Backup is switched on.")
        return 0
    if args.switch_off == 1:
        set_backup_status(False)
        logging.info("Backup is switched off.")
        return 0

    if is_backup_switched_on() is False:
        logging.info("Backup is switched off. Exiting.")
        return 0
    run_backup_from_config_file(dry_run=dry_run)

    return 0
