#! /usr/bin/env python3

import logging
import shutil
from shutil import copy2, move
from os import path, scandir, makedirs
# import os
from sys import maxsize
from guessit import guessit
import configparser

from .cinefiles import Cinefiles

# from guessit import guessit

# 
# defaultPath = "/Volumes/Holland Gibson Ext HDD/Movies/Movies"
# path = input("What folder contains the movies you want to rename/place 
# in folders?\n("+defaultPath+"): ")

class Cinefolders:
    def __init__(self, *args, **kwargs):
        self.configdict = { 'configfile':'',
                            'dirpath':'',
                            'srcpath':'',
                            'copy':True,
                            'limit':maxsize,
                            }

        for k in kwargs:
            if k not in self.configdict:
                print(k+" isn't a valid key")
        
        if('configfile' in kwargs):
            self.configdict.update({'configfile':kwargs['configfile']})
            self.readconfigs(kwargs['configfile'])
        elif(len(kwargs)==0):
            defaultconfig = 'cinefiles.ini'
            print("No arguments specified, searching for "+defaultconfig)
            self.configdict.update({'configfile':defaultconfig})
            self.readconfigs(defaultconfig)
        else:
            if('folder' in kwargs):
                self.configdict.update({'dirpath':kwargs['folder']})
    
    def readconfigs(self, file):
        config = configparser.ConfigParser()
        
        if path.exists(file):
            config.read(file)
        else:
            print('Config file not found!!')
            exit()
        
        if 'cinefolders' not in config:
            print(  "You must have a [cinefolders] section in the"
                    +"config file!!!")
            exit()
        
        conf = config['cinefolders']
        
        folder = conf.get('mainfolder',fallback='')
        self.configdict.update({'dirpath':folder})
        srcfolder = conf.get('source_folder',fallback='')
        self.configdict.update({'srcpath':srcfolder})
        copy_flag = conf.getboolean('copy',fallback=True)
        self.configdict.update({'copy':copy_flag})
        numlimit = conf.getint('max_number',fallback=maxsize)
        self.configdict.update({'limit':numlimit})
        
#         print(self.configdict)

    def organizefolder(self):
        folder = self.configdict['dirpath']
        self.moveintofolders(src=folder, copy=False)
        
#     def renameexisting(self):
#         folders = scandir(src)
#         for item in folders:
#             if(item.is_folder()):
#                 if(not item.name.startswith('.')):
#                     
        
    def fixname(self, en):
        i_info = guessit(en.name)
        newName = i_info['title'].lower()
                
        if(newName[0:4] == 'the '):
            newName.replace('the ','')
            newName = newName + ', The '
        newName = newName.title()

        if('year' in i_info):
            year = str(i_info['year'])
            newName = newName.strip()+' ('+year+')'
        
        return newName

    def moveintofolders(self,src=None, limit=None, copy=None):
        if(src==None):
            src=self.configdict['srcpath']
        if(limit==None):
            limit=self.configdict['limit']
        if(copy==None):
            copy=self.configdict['copy']
            
        dirpath = self.configdict['dirpath']
#         print(dirpath)
        
        if not path.exists(dirpath):
            raise NotADirectoryError(dirpath+" does not exist")
    #       fixedpath = path.replace('\\','').rstrip()
    
        list = scandir(src)
        num = 0
        
        same_folder = (src==dirpath)
    
        if(not copy and not same_folder):
            confirmtxt = ""
            while(not (confirmtxt=="yes" or confirmtxt=="no")):
                confirmtxt = input( 
                    "I highly reccomend you copy movies first, if you "
                    +"don't want an error to delete or corrupt your "
                    +"movies. Are you sure you want to proceed with "
                    +"moving movies into folders? (yes or no) ")
                confirmtxt = confirmtxt.lower()
                if(not (confirmtxt=="yes" or confirmtxt=="no")):
                    print("Please enter 'yes' or 'no'")
    
        for item in list:
            if(item.is_file() and num<=limit):
                if(not item.name.startswith('.')):
                    newName = self.fixname(item)
            
                    print('Copying to '+newName)
                    logging.info(newName)
                    makedirs(dirpath+'/'+newName)
                    if(copy):
                        copy2(item.path, dirpath+'/'+newName+'/'+item.name)
                    else:
                        move(item.path, dirpath+'/'+newName+'/'+item.name)
                    num+=1
                
        if(copy):
            returnstmt = str(num)+" movies copied into better-named folders."
        else:
            returnstmt = str(num)+" movies moved into better-named folders."
        print(returnstmt)
        
        