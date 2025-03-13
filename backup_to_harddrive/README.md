# backup_to_harddrive

This script can typically be trigger when you want to backup files from your
home folder to one or more backup path (e.g harddrives.)

## Targeted platform

| Platform       | Implemented |
|----------------|--------------------|
| Linux          | [ x ]  |
| Windows        | [ ] |
| macOS          | []  |

## Features included

- Exclude folders by list
- CLI switch on and off function (useful if you want to quickly reboot
the computer without triggering a long backup)
- CLI retrieval of last date of backup
- Creation of quick restore shell script. This is useful to quickly restore
part of a backup (for instance, only document, or music etc.) on another machine.

## Configuration file

Create a config file in `~/.config/backup_to_harddrive/config.yaml`.
Follow this example

```yaml
backup_configurations:
  my_backup:
    source: /home/foo
    list_of_harddrive:
      - /media/foo/hd1
      - /media/foo/hd2
    list_of_excluded_folders:
     - .cache
     - /home/foo/excluded
  backup_two:
    source: /home/bar
    list_of_harddrive:
      - /mnt/bar
    list_of_excluded_folders:
     - .config
     - .cache
```

## Use cases

See [USECASES.md](USECASES.md)

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md)
