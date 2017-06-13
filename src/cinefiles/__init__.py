#! /usr/bin/env python3

## needs keyboard interrupt handling
## need to check dependencies
## make folder icon

from __future__ import print_function

# from .cinefiles import Cinefiles
# from .cinefolders import Cinefolders
from . import cinefiles


from os import name as osname

import sys
##only python3, because I need new OS import
if(sys.version_info[0]<=2):
  print("This script is only for python3.x")
  sys.exit(2)
  
__all__ = ["cinefiles","cinefolders","title"]

__version__ = '1.1.1'

__url__ = 'https://github.com/hgibs/cinefiles'

def running_on_windows():
    if(osname=='nt'):
        #codecov skip start
        ctypes.windll.kernel32.SetFileAttributesW.argtypes = (
                                    ctypes.c_wchar_p, ctypes.c_uint32)
        return True
        #codecov skip end
    return False
  
