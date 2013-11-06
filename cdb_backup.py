#!/usr/bin/env python2.7

##############################################################################
#                                                                            #          
# A script to backup your Rackspace cloud database Instance to your cloud    #
# files account. https://github.com/duncanmurray/DBaaS_Backup                #
#                                                                            #
#                        Author: Duncan Murray 2013                          #
#                                                                            #
# Licensed under the Apache License, Version 2.0 (the "License");            #
# you may not use this file except in compliance with the License.           #
# You may obtain a copy of the License at                                    #
#                                                                            #
#     http://www.apache.org/licenses/LICENSE-2.0                             #
#                                                                            #
# Unless required by applicable law or agreed to in writing, software        #
# distributed under the License is distributed on an "AS IS" BASIS,          #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.   #
# See the License for the specific language governing permissions and        #
# limitations under the License.                                             #
#                                                                            # 
##############################################################################      

'''
### Import all used modules
'''

import sys
import os
import pyrax
import uuid
import logging
import argparse
import datetime
import smtplib
import socket
import getpass
from email.mime.text import MIMEText
from pyrax import exceptions as pex

'''
## Set the default variables
'''

# Set default location of pyrax configuration file
CREDFILE = "~/.rackspace_cloud_credentials"
# Set the default location of log files
LOGPATH = "/var/log/"
# Set the default email address to send notifications to
EMAIL = "root@localhost"
# The default from email address. currentuser@hostname
FROMEMAIL = "%s@%s" % (getpass.getuser(), socket.gethostname())

'''
## Read in arguments from the command line
'''

parser = argparse.ArgumentParser(description=("Backup your Rackspace cloud database instance"))
parser.add_argument("-i", "--instance", action="store", required=True,
                    metavar="INSTANCE", type=str,
                    help=("The UUID of your cloud database instance."))
parser.add_argument("-n", "--number", action="store", required=False,
                    metavar="NUMBER", type=int,
                    help=("The number of backups to keep matching the "
                          "provided backup and and UUID. To store indefinately "
                          "use '0'. Defaults to '7'"),
                    default=7)
parser.add_argument("-b", "--backup", action="store", required=True,
                    metavar="BACKUP", type=str,
                    help=("The identifying name of the backup set. The "
                          "backup name along with UUID will determine what "
                          "backups if any to delete."))
parser.add_argument("-d", "--description", action="store", required=False,
                    metavar="DESCRIPTION", type=str,
                    help=("A short description of the backup. If none is "
                          "set it will default to the creation date."))
parser.add_argument("-c", "--credfile", action="store", required=False,
                    metavar="CREDENTIALS_FILE", type=str,
                    help=("The location of your pyrax configuration file. "
                          "Defaults to '%s'." % (CREDFILE)),
                    default=CREDFILE)
parser.add_argument("-p", "--logdirectory", action="store", required=False,
                    metavar="LOG_DIRECTORY", type=str,
                    help=("The directory to create log files in. Defaults "
                          "to '%s'." % (LOGPATH)),
                    default=LOGPATH)
parser.add_argument("-r", "--region", action="store", required=False,
                    metavar="REGION", type=str,
                    help=("The region where you dBaaS instance is located. "
                          "Default to 'LON'. "
                          "Possible [ORD, DFW, LON, SYD, IAD, HKG]"),
                    choices=["ORD", "DFW", "LON", "SYD", "IAD", "HKG"],
                    default="LON")
parser.add_argument("-e", "--email", action="store", required=False,
                    metavar="EMAIL", type=str,
                    help=("The email address to send notifications to. To send "
                          "no email use '0'. Defaults to '%s'." % (EMAIL)),
                    default=EMAIL)
parser.add_argument("-v", "--verbose", action="store_true", required=False,
                    help=("Turn on debug verbosity"),
                    default=False)
# Parse arguments (validate user input)
args = parser.parse_args()

'''
## Configure the logging utility
'''

# Configure log formatting
logFormatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
rootLogger = logging.getLogger()
# Check what level we should log with
if args.verbose:
    rootLogger.setLevel(logging.DEBUG)
else:
    rootLogger.setLevel(logging.WARNING)
# Configure logging to console
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)
# Configure logging to file
try:
    fileHandler = logging.FileHandler("{0}/{1}.log".format(args.logdirectory, os.path.basename(__file__)))
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)
except IOError:
    rootLogger.critical("Unable to write to log file directory '%s'." % (args.logdirectory))
    exit(1)

'''
## Define the main program
'''

def main():

    # Define the authentication credentials file location and request that
    # pyrax makes use of it. If not found, let the client/user know about it.

    # Use a credential file in the following format:
    # [rackspace_cloud]
    # username = myusername
    # api_key = 01234567890abcdef
    # region = LON

    # Set identity type as rackspace
    pyrax.set_setting("identity_type", "rackspace")

    # Test that the pyrax configuration file provided exists
    try:
        creds_file = os.path.expanduser(args.credfile)
        pyrax.set_credential_file(creds_file, args.region)
    # Exit if authentication fails
    except pex.AuthenticationFailed:
        rootLogger.critical("Authentication failed")
        rootLogger.info("%s", """Please check and confirm that the API username,
                                     key, and region are in place and correct."""
                       )
        exit(2)
    # Exit if file does not exist
    except pex.FileNotFound:
        rootLogger.critical("Credentials file '%s' not found" % (creds_file))
        rootLogger.info("%s", """Use a credential file in the following format:\n
                                 [rackspace_cloud]
                                 username = myuseername
                                 api_key = 01sdf444g3ffgskskeoek0349"""
                       )
        exit(3)

    # Shorten the call to cloud databases
    cdb = pyrax.cloud_databases

    # Try to find the instance matching UUID provided
    try:
        mycdb = cdb.find(id=args.instance)
    except pex.NotFound:
        rootLogger.critical("No instances found matching '%s'" % (args.instance))
        exit(4)

    # Create a new backup
    if args.description:
        description = args.description
    else:
        description = "Created on " + datetime.datetime.now().strftime("%Y-%b-%d-%H:%M")
    
    try:
        rootLogger.info("Creating backup of '%s'." % (mycdb.name))
        new_backup = mycdb.create_backup(args.backup + '-' + datetime.datetime.now().strftime("%y%m%d%H%M"), description=description)
    except pex.ClientException:
        type, value, traceback = sys.exc_info()
        rootLogger.critical(value.message)
        exit(5)

    # Put our current backups in a list
    backups = []
    for backup in mycdb.list_backups():
        if backup.name.startswith(args.backup) and backup.name[10:].isnumeric:
            backups.append(backup)
            
    # Sort out backups by date (this is probably not a very reliable way)
    backups.sort(key=lambda backup: backup.created, reverse=True)

    # Print our current backups
    rootLogger.info("Current backups of '%s' below:" % (mycdb.name))
    for backup in backups:
        rootLogger.info("Name: '%s' Created on '%s'" % (backup.name, backup.created))

    # Check if backups need to be deleted
    if len(backups) > args.number and args.number is not 0:
        # Warn of backups being deleted
        rootLogger.warning("There are '%i' backups. Need to delete '%i'." % (len(backups), len(backups) - args.number))
        # Delete oldest backups if current backups > target backups
        for backup in backups[args.number:]:
            try:
                rootLogger.warning("The below backups will be deleted.")
                rootLogger.warning("Name: '%s' Created on '%s'." % (backup.name, backup.created))
                backup.delete()
            except pex.ClientException:
                type, value, traceback = sys.exc_info()
                rootLogger.critical(value.message)
                exit(6)

            # Wait until the instance is active
            pyrax.utils.wait_for_build(mycdb,"status", "ACTIVE", interval=1, attempts=30)
    
    exit(0)

def email_notification(ecode):
    if ecode == 0:
        msg = '''Backup of Rackspace Cloud Database %s completed successfully at %s.''' % (args.instance, datetime.datetime.now().strftime("%Y-%b-%d-%H:%M"))
        msg = MIMEText(msg)
        msg['Subject'] = "Backup of Rackspace Cloud Database SUCCESSFUL"
        msg['From'] = FROMEMAIL
        msg['To'] = args.email
    else:
        msg = '''Backup of Rackspace Cloud Database %s failed at %s. Backup operation failed with exit code %s. Please check %s%s for more information.''' % (args.instance, datetime.datetime.now().strftime("%Y-%b-%d-%H:%M"), ecode, args.logdirectory, os.path.basename(__file__))
        msg = MIMEText(msg)
        msg['Subject'] = "Backup of Rackspace Cloud Database FAILED"
        msg['From'] = FROMEMAIL
        msg['To'] = args.email

    try:
        smail = smtplib.SMTP('localhost')
        smail.sendmail(FROMEMAIL, args.email, msg.as_string())
        smail.quit()
        rootLogger.info("Sending notification email to '%s'." % (args.email))
    except smtplib.SMTPException:
        type, value, traceback = sys.exc_info()
        rootLogger.warning("Sending email notification to '%s' failed - '%s'" %(args.email, value))
        pass
    except socket.error:
        type, value, traceback = sys.exc_info()
        rootLogger.warning("Sending email notification to '%s' failed - '%s'" %(args.email,value))
        pass

'''
## Run the main program
'''

if __name__ == '__main__':
    try:    
        main()
    except SystemExit as ecode:
        if args.email == str(0):
            pass
        else:
            email_notification(ecode[0])
        if ecode[0] == 0:
            rootLogger.info("Backup completed successfully.")
        else:
            rootLogger.critical("Backup failed with exit code %i" % (ecode.args[0]))
        exit(ecode.args[0])
