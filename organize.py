#! /usr/bin/env python3

import cinefiles.cinefolders as cf
# import logging

# print(dir(cinefiles))

# directory = "/Volumes/Holland Gibson Ext HDD/Movies/testbed"

# search = cf.Cinefiles(searchfolder=directory, guess_flag=True, skip_flag=False, test_flag=False, 
#                 force_flag=False, destroy_flag=False, debug=logging.DEBUG)

organize = cf.Cinefolders(configfile='cinefiles.ini')
# search = cf.Cinefiles()
              
# organize.moveintofolders()
organize.organizefolder()