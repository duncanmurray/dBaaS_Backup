DBaaS_Backup
============

```
usage: cdb_backup.py [-h] -i INSTANCE [-n NUMBER] -b BACKUP [-d DESCRIPTION]
                     [-c CREDENTIALS_FILE] [-r REGION] [-v]

Backup your Rackspace cloud database instance

optional arguments:
  -h, --help            show this help message and exit
  -i INSTANCE, --instance INSTANCE
                        The UUID of your cloud database instance
  -n NUMBER, --number NUMBER
                        The number of backups to keep. (Defaults to 7)
  -b BACKUP, --backup BACKUP
                        The identifying name of your backup
  -d DESCRIPTION, --description DESCRIPTION
                        A short description of the backup
  -c CREDENTIALS_FILE, --credfile CREDENTIALS_FILE
                        The location of your pyrax configuration file
  -r REGION, --region REGION
                        Region where your lsyncd configuration group is
                        (defaults to 'LON') [ORD, DFW, LON, SYD, IAD]
  -v, --verbose         Turn on debug verbosity
```
