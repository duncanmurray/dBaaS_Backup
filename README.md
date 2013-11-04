dBaaS_Backup
============

```
usage: cdb_backup.py [-h] -i INSTANCE [-n NUMBER] -b BACKUP [-d DESCRIPTION]
                     [-c CREDENTIALS_FILE] [-p LOG_DIRECTORY] [-r REGION] [-v]

Backup your Rackspace cloud database instance

optional arguments:
  -h, --help            show this help message and exit
  -i INSTANCE, --instance INSTANCE
                        The UUID of your cloud database instance.
  -n NUMBER, --number NUMBER
                        The number of backups to keep matching the provided
                        backup and and UUID. To override use 0. Defaults to 7)
  -b BACKUP, --backup BACKUP
                        The identifying name of the backup set. The backup
                        name along with UUID will determine what backups if
                        any to delete.
  -d DESCRIPTION, --description DESCRIPTION
                        A short description of the backup. If none is set it
                        will default to the creation date.
  -c CREDENTIALS_FILE, --credfile CREDENTIALS_FILE
                        The location of your pyrax configuration file.
                        Defaults to '~/.rackspace_cloud_credentials'.
  -p LOG_DIRECTORY, --logdirectory LOG_DIRECTORY
                        The directory to create log files in. Defaults to
                        '/var/log/'.
  -r REGION, --region REGION
                        The region where you dBaaS instance is located.
                        Default to 'LON'. Possible [ORD, DFW, LON, SYD, IAD,
                        HKG]
  -v, --verbose         Turn on debug verbosity
```
