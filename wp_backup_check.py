#!/bin/python

import json
import os
import sys
import datetime
import time
import logging
from sys import argv
from time import sleep
from modules.gke_modules import *

script, s3_access, s3_key = argv

def main():
    logger = logging()
    backup_list(logger, s3_access, s3_key)
    podList = find_wp_gke()
    failedBackups = backup_check(podList, logger)
    if (failedBackups >0):
        print("The following backups failed")
        os.system("cat error.log")

def cleanup():
    os.remove('backup.list')
    os.remove('pods.json')

if __name__ == '__main__':
    main()
    cleanup()
