#! /usr/bin/env python3

import cinefiles.cinefiles as cf
import logging

search = cf.Cinefiles(configfile='cinefiles.ini')
# search = cf.Cinefiles()
              
search.run()