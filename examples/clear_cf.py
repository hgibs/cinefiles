#! /usr/bin/env python3

import cinefiles as cf
import logging

# print(dir(cinefiles))

# directory = "/Volumes/Holland Gibson Ext HDD/Movies/testbed"

clear_run = cf.Cinefiles(configfile='cinefiles.ini')

clear_run.purgecinefiles()