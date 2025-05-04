# Use cases

## UC1: simple backup

* Given a config file like this `~/.config/backup_to_harddrive/config.yaml`

```yaml
backup_configurations:
  my_backup:
    source: /home/foo
    list_of_harddrive:
      - /media/foo/hd1
```

* Running `backup_to_harddrive` shall trigger

```bash
rsync --mkpath --delete --delete-before --update --progress -t -a -r -v -E -c -h
 /home/foo /media/foo/hd1/Backup/$(hostname)/
```

## UC2: excluding folder

* Given a config file like this `~/.config/backup_to_harddrive/config.yaml`

```yaml
backup_configurations:
  my_backup:
    source: /home/foo
    list_of_harddrive:
      - /media/foo/hd1
    list_of_excluded_folders:
      - .cache
```

* Running `backup_to_harddrive` shall trigger

```bash
rsync --mkpath --delete --delete-before --update --progress -t -a -r -v -E -c -h
 --exclude=/home/foo/.cache /home/foo /media/foo/hd1/Backup/$(hostname)/
```

## UC3: switching backup off

* Running `backup_to_harddrive --switch-off` shall switch the bakcup off
* Running `backup_to_harddrive` afterwards shall not issue any rsync command

## UC3: switching backup on

* Running `backup_to_harddrive --switch-off` shall switch the bakcup off
* Running `backup_to_harddrive --switch-on` shall switch the bakcup on
* Running `backup_to_harddrive` afterwards shall not issue rsync command
 according to [config_file](~/.config/backup_to_harddrive/config.yaml)

## UC4: creation of quick restore script

* Given a config file like this `~/.config/backup_to_harddrive/config.yaml`

```yaml
backup_configurations:
  my_backup:
    source: /home/foo
    list_of_harddrive:
      - /media/foo/hd1
    quick_restore_path:
      - Documents
```

* Running `backup_to_harddrive` shall trigger

```bash
rsync --mkpath --delete --delete-before --update --progress -t -a -r -v -E -c -h
 --exclude=/home/foo/.cache /home/foo /media/foo/hd1/Backup/$(hostname)/
```

* A script shall be created in `/media/foo/hd1/Backup/$(hostname)/restore_Documents.sh`

```bash
#!/bin/bash
set -euxo pipefail
cd "$USER"
rsync -avc --delete Development /home/foo
```

* The script `/media/foo/hd1/Backup/$(hostname)/restore_Documents.sh` shall have
execution permission set.

## UC5: write time stamp of last successful backup

* Given a config file like this `~/.config/backup_to_harddrive/config.yaml`

```yaml
backup_configurations:
  my_backup:
    source: /home/foo
    list_of_harddrive:
      - /media/foo/hd1
    quick_restore_path:
      - Documents
```

* Running `backup_to_harddrive` shall write or overwrite a file
`/media/foo/hd1/Backup/timestamp.txt` that contains the timestamp of the backup
 after successful execution.

## UC6: log warning or error if rsync is not installed and prevent execution

* Given a Linux system were `rsync` is not found in the path.

* And given a valid configuration like this

```yaml
backup_configurations:
  my_backup:
    source: /home/foo
    list_of_harddrive:
      - /media/foo/hd1
    quick_restore_path:
      - Documents
```

* When the user issue `backup_to_harddrive`
  * Then an error message `"Rsync not found in path ! Consider installing rsync
   with sudo apt-get install rsync"` shall appear
  * And then no rsync command shall be issue
  * And then backup timestamp shall not be updated
  * And then the execution shall return 1
* When the user issue `backup_to_harddrive --switch-on`
  * Then a warning message "Rsync not found in path ! Consider installing rsync
   with sudo apt-get install rsync"` shall appear
  * And then the backup status shall be switch to on
* When the user issue `backup_to_harddrive --switch-off`
  * Then a warning message "Rsync not found in path ! Consider installing rsync
   with sudo apt-get install rsync"` shall appear
  * And then the backup status shall be switch to on

[See test cases](validation/usecase_6_test_list.txt)
