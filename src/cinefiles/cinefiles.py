import getopt
import os
import sys
import requests
import html.parser
import datetime
import logging
import filecmp
import ctypes
import configparser
from time import strftime
import tkinter as tk #GUI options
from shutil import copy2, rmtree
import filecmp, mimetypes
from guessit import guessit
from io import open as iopen
from platform import system
import traceback
from lxml import etree

### Could thread this because it is a SO SLOOWWW

### Should definitely load the JS web driver at a higher level so we 
### aren't instantiating it for every movie poster


from . import title, templatex, googlesearch

from .__init__ import __version__, running_on_windows

from .tmdb import TMDb

TMDB_API_KEY = 'beb6b398540ccc4245a5b4739186a0bb'

class Cinefiles:
    def __init__(self, *args, **kwargs):
        if(running_on_windows() and __init__.__version__[0]!='2'):
            print(  "This code does not handle windows "
                    +"file paths correctly, so it cannot run yet. "
                    +"I am deeply sorry for this, please wait until "
                    +"version 2.0 is released. You could help this "
                    +"version get released faster by contributing to "
                    +"this project at github.com/hgibs/cinefiles")
            sys.exit(2)    
        logging.getLogger('requests').setLevel(logging.ERROR)
        
        self.configdict = { 'guess':True, 
                            'skip':False, 
                            'test':False,
                            'force':False,
                            'destroy':False,
                            'debugnum':logging.INFO,
                            'localresources':True,
                            'searchfolder':'',
                            'def_lang':'en',
                            'def_region':'US',
                            'win_hide':True,}
                                                
        self.matches = []
        self.choices = []
        
        self.indexlist = []
        
        self.structnames = {'hiddenresfolder':'.cinefiles',
                            'archive':'.archive.log'}
        
        if len(kwargs) == 0:
            #no supplied arguments try for default config file
            print("No arguments supplied, trying 'cinefiles.ini'")
            self.readconfigfile('cinefiles.ini')
        elif 'configfile' in kwargs:
            #The config file replaces all others
            self.readconfigfile(kwargs['configfile'])
        elif 'internal_call' in kwargs:
            #basically make this as fast as possible - default everything
            self.configdict.update({'internal_call':True})
        else:
            if 'guess' in kwargs:
                self.configdict.update({'guess':kwargs['guess']})
            if 'skip' in kwargs:
                self.configdict.update({'skip':kwargs['skip']})
            if 'test' in kwargs:
                self.configdict.update({'test':kwargs['test']})
            if 'force' in kwargs:
                self.configdict.update({'force':kwargs['force']})
            if 'destroy' in kwargs:
                self.configdict.update({'destroy':kwargs['destroy']})
            if 'debugnum' in kwargs:
                self.configdict.update({'debugnum':int(kwargs['debugnum'])})
            if 'localresources' in kwargs:
                self.configdict.update({'localresources':kwargs['localresources']})
            if 'searchfolder' in kwargs:
                self.configdict.update({'searchfolder':kwargs['searchfolder']})
            
            logging.basicConfig(
                    filename='Cinefiles.log', 
                    format='%(levelname)s:%(asctime)s:%(message)s',
                    datefmt='%H%M',
                    level=self.configdict['debugnum'])
        
        if('internal_call' in self.configdict):
            #do nothing - ignore that no search folder is specified
            pass
        elif(self.configdict['searchfolder']==''):
            logging.critical("'' is not a directory!!!")
            raise NotADirectoryError("'' is not a directory!!!")
        
#         self.runtotal = 0

        mimetypes.init()
        self.allowedvideoextensions = []
        for ext in mimetypes.types_map:
            if mimetypes.types_map[ext].split('/')[0] == 'video':
                self.allowedvideoextensions.append(ext)
                
        self.onceprintentry=None
        
        self.tmdb = TMDb(TMDB_API_KEY,
                        self.configdict['def_lang'],
                        self.configdict['def_region'])
        
        self.rogersearchengine = googlesearch.GoogleSearch()
        
        self.misses = []

    #####################
    # The init and prep #
    #####################
    
    def readconfigfile(self, file):
    
        #TODO: add region 'US' input
        config = configparser.ConfigParser()
        
        if os.path.exists(file):
            config.read(file)
        else:
            raise IOError('Config file not found!! ('+file+')')
        
        if 'cinefiles' not in config:
            raise ValueError("You must have a [cinefiles] section in the config file!!!")
        
         # 'guess','skip','test','force','destroy','debugnum','searchfolder'
        conf = config['cinefiles']
        
        guess_bool = conf.getboolean('guess',fallback=True)
        self.configdict.update({'guess':guess_bool})
        skip_bool = conf.getboolean('skip',fallback=False)
        self.configdict.update({'skip':skip_bool})
        test_bool = conf.getboolean('test',fallback=False)
        self.configdict.update({'test':test_bool})
        force_bool = conf.getboolean('force',fallback=False)
        self.configdict.update({'force':force_bool})
        destroy_bool = conf.getboolean('destroy',fallback=False)
        self.configdict.update({'destroy':destroy_bool})
        debugnum = conf.getint('debugnum',fallback=logging.INFO)
        self.configdict.update({'debugnum':debugnum})
        searchfolder = conf.get('searchfolder','')
        self.configdict.update({'searchfolder':searchfolder})
        langselect = conf.get('default_language','en')
        self.configdict.update({'def_lang':langselect})
        regselect = conf.get('default_country','US')
        self.configdict.update({'def_region':regselect})
        
        force_specific = conf.get('force-specific','')
        force_index = (force_specific.lower().find('index') >= 0)
        self.configdict.update({'force_index':force_index})
        
        localres_bool = conf.getboolean('localresources',fallback=True)
        self.configdict.update({'localresources':localres_bool})
        
        hiddenresfolder = conf.get('resource_folder_name',
                                    self.structnames['hiddenresfolder'])
        self.structnames.update({'hiddenresfolder':hiddenresfolder})
        
        archive = conf.get('file_archive_filename',
                           self.structnames['archive'])
        self.structnames.update({'archive':archive})

        logfilename = conf.get('logfilename','Cinefiles.log')
        self.configdict.update({'logfilename':logfilename})
        logformat = config['cinefiles'].get('logformat','L{colon}T{colon}M')
        logformat = logformat.replace('L','%(levelname)s')
        logformat = logformat.replace('F','%(filename)s')
        logformat = logformat.replace('P','%(pathname)s')
        logformat = logformat.replace('N','%(module)s')
        logformat = logformat.replace('T','%(asctime)s')
        logformat = logformat.replace('M','%(message)s')
        logformat = logformat.replace('{colon}',':')
        self.configdict.update({'logformat':logformat})
        
        logdateformat = config['cinefiles'].get('logdateformat','%H%M')
        fixedlogdate = self.fixlogdateformat(logdateformat)
        self.configdict.update({'logdateformat':fixedlogdate})
        
        logging.basicConfig(filename=self.configdict['logfilename'], 
                            format=self.configdict['logformat'],
                            datefmt=self.configdict['logdateformat'],
                            level=self.configdict['debugnum'])
                            
#         overridestr = conf.get('override_title','')
#         overridelist = overridestr.split('+')
#         for title in overridelist:
#             title = title.strip()
#         self.configdict.update({'override-title-list':overridelist})
        
        win_hide_bool = conf.getboolean('windows_hide_structure',fallback=True)
        self.configdict.update({'win_hide':win_hide_bool})

    def fixlogdateformat(self, format):
        format = format.replace('{a}','%a')
        format = format.replace('{A}','%A')
        format = format.replace('{b}','%b')
        format = format.replace('{B}','%B')
        format = format.replace('{c}','%c')
        format = format.replace('{d}','%d')
        format = format.replace('{H}','%H')
        format = format.replace('{I}','%I')
        format = format.replace('{j}','%j')
        format = format.replace('{m}','%m')
        format = format.replace('{M}','%M')
        format = format.replace('{p}','%p')
        format = format.replace('{S}','%S')
        format = format.replace('{U}','%U')
        format = format.replace('{w}','%w')
        format = format.replace('{W}','%W')
        format = format.replace('{x}','%x')
        format = format.replace('{X}','%X')
        format = format.replace('{y}','%y')
        format = format.replace('{Y}','%Y')
        format = format.replace('{Z}','%Z')
        format = format.replace('{colon}',':')

        return format
        
    def prepmainfolder(self):
        self.prepfolder(self.configdict['searchfolder'])

    def prepfolder(self, folder):
        resfolder = self.structnames['hiddenresfolder']
        newresources = folder+'/'+resfolder
        
        self.installresources = getmoduleresources()
        self.addedres = False
        self.recursiveupdate(self.installresources, newresources)
        
        if(running_on_windows() and self.configdict['win_hide']):
            FILE_ATTRIBUTE_HIDDEN = 0x02
            hide = ctypes.windll.kernel32.SetFileAttributesW(newresources,
                                                    FILE_ATTRIBUTE_HIDDEN)
            if not hide: # There was an error.
                raise ctypes.WinError()
            
    #this exists as to not replace the folder with copytree() but to add new resources
    #this allows already made indexes to use old files if they still need them
    def recursiveupdate(self, src, dst):
#           logging.debug('recursiveupdate =>\n\tsrc='+src+'\n\tdst='+dst)
        if not os.path.exists(dst):
            os.makedirs(dst)
        src_it = os.scandir(src)
        for entry in src_it:
#               relpath = entry.path.split(self.installresources)[1]
            relpath = entry.path.split('/')[-1]
#               logging.debug('relpath is:'+relpath)
            if entry.is_dir():
                #go deeper
#                   logging.debug('!!!!!!!!'+entry.path+', '+dst+'/'+relpath)
                self.recursiveupdate(entry.path, dst+'/'+relpath)
            else:
                #it's a file
                if(entry.name != '.DS_Store'): #mac specific - really not that important
                    realsrc = entry.path
                    realdst = dst+'/'+entry.name
#                       logging.debug(entry.name+'>'+realdst+'='+str(filecmp.cmp(src,dst)))
                    if(os.path.exists(realdst)):
                        #if it exists already is the module resources file different
                        if(not filecmp.cmp(realsrc,realdst)):
                            self.logcopy(realsrc,realdst)
                    else:
                        self.logcopy(realsrc,realdst)
                        
    def logcopy(self,src,dst):
        try:
            logging.debug('Copy/Overwriting =>'+dst)
            copy2(src, dst)
            self.addedres = True
#                       except FileNotFoundError as e:
#                           logging.critical('Resource '+entry.path+' not found (')
        except IOError as e:
            self.critical(e)


    #################################
    # The execution overall handler #
    #################################

    def run(self):
        
        logging.info(strftime('Starting Cinefiles run at %d %b %Y %X'))
        logging.info("Search folder is: "+self.configdict['searchfolder'])

        self.prepmainfolder()
        
        #with os.scandir(self.searchfolder) as it:
        it = os.scandir(self.configdict['searchfolder'])
        print('🔥    Performing inital search...')
        for entry in it:
            #scan folders
            if not (entry.name.startswith('.') 
                    or entry.name in self.structnames.values()):
                #skip hidden/system folders
                self.recursefolder(entry)
            
        self.processchoices()
        
        self.makemasterindex()
        
        self.runtotal = len(self.matches)
        print("🔥    Done! Scanned "+str(self.runtotal)+" entries.")
        logging.info(strftime('Complete at %d %b %Y %X'))
        logging.info("Scanned "+str(self.runtotal)+" entries.")
        misstotal = len(self.misses)
        if(misstotal > 0):
            self.recordmisses()
        logging.info(str(misstotal)+" did not result in a match")
        logging.info('-'*60)
        
    def printoncerecursevely(self,en):
        if(en!=self.onceprintentry):
            print("Searching sub-directory: "+en.name)
        self.onceprintentry = en
        
    #to see if the existing archive is complete
    def checkarchive(self, archive):
        with open(archive.path,'r') as arch:
            archivechecks = {'T':False,
                             'P':False, 
                             't':False, 
                             'H':False,
                             'y':False,}
            for line in arch:
                if not line.startswith('#'):
                    typechar = line[11:12]
                    filename = line[13:-1]
                    if(typechar in archivechecks):
                        archivechecks.update({typechar:True})
        
        for tkey in archivechecks:
            if not archivechecks[tkey]:
                return False
        
        return True
    
    #for recursively searching folders  
    def recursefolder(self, entry):
        if entry.is_dir():
            #found folder
            #foldername = entry.name
            #is .archive in there?
            subit = os.scandir(entry.path)
            alreadyparsed = False
            foundvideo = False
            subfolder = False
            for subentry in subit:
                if(subentry.name == self.structnames['archive']):
                    alreadyparsed = self.checkarchive(subentry)
                elif('.'+subentry.name.split('.')[-1] in self.allowedvideoextensions):
                    foundvideo = True
                elif(subentry.name not in self.structnames.values()):
                    if(subentry.is_dir() and not subentry.name.startswith('.')):
                        logging.debug('Recursively searching '+subentry.name)
                        self.printoncerecursevely(entry)
                        subfolder = self.recursefolder(subentry)
                  
            force_extra = False
            if('force_index' in self.configdict):
                   force_extra = self.configdict['force_index']
                   
            if(foundvideo):
                if(alreadyparsed): 
                    logging.info(entry.name+'\talready processed')
                    if(self.configdict['force'] or force_extra):
                        logging.info('Processing movie, [force] is set to True')
                        self.process_movie(entry)
                    else:
                        print(entry.name+' already parsed on a previous iteration')
                        self.indexlist.append(self.getattrfrommetadata(entry.path))
                else:
                    #subfolder doesn't have a movie in it
                    if(not subfolder):
                        self.process_movie(entry)
                
            return foundvideo
        else:
            return False
                
    def processchoices(self):
        #try to put all the choices up front first as to not waste user's time
        if len(self.choices)>0:
            print('🔥    Presenting choices...')
        for m in self.choices:
            self.manymatch(m[0],m[1])
        
        if len(self.matches)>0:
            print('🔥    Parsing matched movies...')
        for m in self.matches:
            self.match(m[0],m[1])
    
    
    #Process an individual movie found
    def process_movie(self,en,newname=''):
#         self.runtotal+=1
        title = ''
        year = None
        if(newname != ''):
            print("> ",end='',flush=True)
            guessattr = guessit(en.name)
            if('title' in guessattr):
                title = guessattr['title']
            else:
                title = en.name
            if('year' in guessattr):
                year = guessattr['year']
        else:
            title = en.name
           
        searchresults = []
        
        trylink = self.readlink(en)
        if(trylink is not None):
            searchresults = [self.tmdb.getmovie(trylink)]
        else:
            searchresults = self.tmdb.search(title,year)
        
        print('"'+title+'" ', end='', flush=True)
        if(len(searchresults)==0):
            #couldn't find a match :(
            if(newname!=''):
                logging.info('Extended searching on '+title+' found'+
                             ' no matches!!')
                return False
            self.nomatch(en)
        elif(len(searchresults)==1):
            #we got a direct match!
            self.addmatch(en, searchresults[0])
            logging.info('Found '+en.name)
            print('Found!')
        elif(len(searchresults)>1):
            #uh oh, multiple found
            print("Multiple matches found", end='', flush=True)
            if(self.configdict['skip']):
                print(" skipping this entry.")
                logging.info(file.name+" SKIPPED - too many results")
            elif(self.configdict['guess']):
                print(" making best guess.")
                self.addmatch(en, searchresults[0])
            else:
                self.addchoice(en, searchresults)
                print('')
        return True
        
        
    def readlink(self, folder):
        linkfile = folder.path+'/link.xml'
        if(os.path.exists(linkfile)):
            doc = etree.parse(linkfile)
            root = doc.getroot()
            for child in root:
                if(child.tag == 'tmdbid'):
                    return child.text
        return None
        
    def recordmisses(self):
        misspath = self.configdict['searchfolder']+'/cinefiles-misses.txt'
        with open(misspath, w) as missfile:
            missfile.write( 'The following movies resulted in no matches! '
                    'Try renaming the folders, or adding a link.xml file: \n'
                    '<dict><tmdbid>999</tmdbid></dict>\nwhere 999 is the number '
                    'of the movie in The Movie Database.\n')
            for name in self.misses:
                missfile.write(name+'\n')

    ##########################
    # The No-Matches portion #
    ##########################

    def nomatch(self, file):
        #Try to search with a better name from guessit
        #Maybe this should just be on by default
        logging.info("No match on "+file.name)
        if(not self.process_movie(file,newname=file.name)):
            #the movie still wasn't found so we stop the loop
            logging.error("NO MATCHES for "+file.name)
            print("\tNo match!!")
    
    def addmiss(self, file):
        spath = file.path
        self.misses.append(spath.split(self.configdict['searchfolder'])[-1])
        
        
        
    ############################
    # The Single-Match portion #
    ############################
    
    def match(self, folder, movie):
        print('"'+folder.name+'" ', end='', flush=True)
        if (self.configdict['localresources']):
            #it's easier to copy resources now
            self.prepfolder(folder.path)
        m = title.Title(folder.path, movie, self, self.configdict)
        self.indexlist.append(m.getattributes())
        
    def addmatch(self, fol, mov):
#           print('\tFound!')
        self.addlink(fol,mov)
        self.matches.append((fol,mov))

    def addlink(self, folder, movie):
        idkey = 'tmdbid'
        linkfile = folder.path+'/link.xml'
        root = etree.Element('dict')
        addedtmdbid = False
        if(os.path.exists(linkfile)):
            olddoc = etree.parse(linkfile)
            root = olddoc.getroot()
            for child in root:
                if(child.tag == idkey):
                    child.text = movie.id
                    addedtmdbid = True
            if(not addedtmdbid):
                tmdbid = etree.SubElement(root,idkey)
                tmdbid.text = movie.id
        else:
            tmdbid = etree.SubElement(root,idkey)
            tmdbid.text = movie.id
        doc = etree.ElementTree(root)
        with open(linkfile, 'wb') as outfile:
            doc.write(outfile)
        

    ############################
    # The Many-Matches portion #
    ############################
    def addchoice(self, fol, res):
        self.choices.append((fol,res))
    
    def tkselect(self):
        self.popup.destroy()
#           print(dir(self.selvar))
        print("matched movie id "+self.selvar.get())
        self.choiceselect = self.selvar.get()
        self.tkcleanup()
        
    def tkskip(self):
        self.popup.destroy()
        print("Skipped!")
        self.tkcleanup()
        
    def tkskipall(self):
        self.popup.destroy()
        print("🔥    Skipping all and supressing the GUI")
        self.configdict.update({'skip':True})
        self.tkcleanup()
        
    def tkcleanup(self):
        self.popup = None
        self.selvar = None

    def manymatch(self, file, results):
        if(self.configdict['skip']): # this must have been selected by the GUI
            logging.info(file.name+" SKIPPED - too many results")
        else:
            # global log, skip_flag
            self.popup = tk.Tk()
            #popup.geometry("100x200")
            self.selvar = tk.StringVar()
            label = tk.Label(self.popup, text=(
                    "More than one movie was found matching the "
                    +"movie title in TMDb, please select the "
                    +"correct one:"))
            label.pack()
        
            choosebtn = tk.Button(  self.popup, 
                                    text="Select", 
                                    command=self.tkselect, 
                                    width='70', 
                                    bg='white', 
                                    fg='black')
                                    
            skipbtn = tk.Button(self.popup, 
                                text="Skip", 
                                command=self.tkskip, 
                                bg='red', 
                                fg='white')
                                
            skipallbtn = tk.Button( self.popup, 
                                    text="Skip All", 
                                    command=self.tkskipall, 
                                    bg='gray', 
                                    fg='black')
            radiolist = []
    
            first = True
            for movie in results:
                radiotxt = movie.title+" ("+str(movie.year)+")"
                radiobtn = tk.Radiobutton(  self.popup, 
                                            text=radiotxt, 
                                            variable=self.selvar, 
                                            value=movie.id)
                radiobtn.pack()
                if(first):
                    first=False
                    radiobtn.select()
            
            choosebtn.pack( fill=tk.Y, 
                            side=tk.TOP,
                            expand=1, 
                            padx=1, 
                            pady=1)
                            
            skipbtn.pack(   fill=tk.Y, 
                            side=tk.LEFT, 
                            expand=1, 
                            padx=1, 
                            pady=1)
                            
            skipallbtn.pack(fill=tk.Y, 
                            side=tk.RIGHT, 
                            expand=1, 
                            padx=1, 
                            pady=1)
                            
            self.popup.pack_propagate(1)
            self.choiceselect = None
            self.popup.mainloop()
            if(self.choiceselect is not None):
                self.addmatch(file, tmdb.getmovie(self.choiceselect))
            #choosing/skipping is done by button call
   
   
    ##################
    # error handling #
    ##################
        
    def critical(self, err):
        logging.critical(str(err)+'\n'+traceback.format_exc())
        
        
    #######################
    # cinefiles utilities #
    #######################
    
    def makemasterindex(self):
        html = ''
        tablerow= (
                '<tr class="">'
                +'<td><a class="rowlink" href="$%{foldername}/index.htm">'
                +'<img class="thumbnail" src="$%{foldername}/$%{postersrc}"></a></td>'
                +'<td class="rowtitle">$%{title}</td>'
                +'<td class="rowyear">$%{year}</td>'
                +'<td class="rowruntime">$%{runtime}</td>'
                +'<td class="rowroger">$%{roger}</td>'
                +'<td class="rowimdb">$%{imdb}</td>'
                +'<td class="rowrotten">$%{rotten}</td>'
                +'<td class="rowmeta">$%{meta}</td>'
                +'</a></tr>')
        
        tablerows = ''
        template = templatex.TemplateX(tablerow)
        
        for f in self.indexlist:
            movieattributes = { 'foldername':'',
                                'postersrc':'',
                                'title':'',
                                'year':'',
                                'runtime':'',
                                'roger':'',
                                'imdb':'',
                                'rotten':'',
                                'meta':''}
            movieattributes.update(f)
            tablerows+=template.substitute(movieattributes)
            
        res_path = getmoduleresources()+'/'
        with open(res_path+'masterindex.html','r') as templatefile:
                formatstr = templatefile.read().replace('\n', '')
                formatstr = formatstr.replace('\t', '')
                html = templatex.TemplateX(formatstr)
        
        replacedict = { 'headertitle':self.configdict['searchfolder'].split('/')[-1],
                        'cf_res':self.structnames['hiddenresfolder'],
                        'table_rows':tablerows,
                        'tmdb_logo':'/images/tmdb-attribution-rectangle.png',}
        
        writeouthtml = html.substitute(replacedict)
        
        htmlfilename = self.configdict['searchfolder']+'/index.htm'

        if(os.path.isfile(htmlfilename)):
            os.remove(htmlfilename)
            logging.info('Deleted '+htmlfilename)

        with iopen(htmlfilename, 'x') as file:
            file.write(writeouthtml)
            logging.info('Wrote new '+htmlfilename)
        
            
    def getstructurenames(self):
        return self.structnames
        
    #Clear everything / sorta like uninstall
    def purgecinefiles(self):
        it = os.scandir(self.configdict['searchfolder'])
        hiddenres = self.structnames['hiddenresfolder']
        
        for entry in it:
            #scan folders
            if( entry.name == hiddenres ):
                print("Removing directory "+entry.path)
                rmtree(entry.path)
            elif not entry.name.startswith('.'):
                #skip other hidden or system folders
                if entry.is_dir():
                    #found folder
                    #foldername = entry.name
                    #is .archive in there?
                    self.purgerecursevily(entry)
                            
    def purgerecursevily(self,entry):
        hiddenres = self.structnames['hiddenresfolder']
        archivename = self.structnames['archive']
        subit = os.scandir(entry.path)
        for subentry in subit:
            if(subentry.is_dir() and subentry.name == hiddenres):
                print("Removing directory "+subentry.path)
                rmtree(subentry.path)
            elif(subentry.is_dir()):
                self.purgerecursevily(subentry)
            elif(subentry.name == archivename):
                self.cleararchive(subentry.path)
    
    def cleararchive(self, archivepath):
        with open(archivepath,'r') as arch:
            for line in arch:
                if(not line.startswith('#')):
                    file = self.getarchfile(line)
                    if(os.path.isfile(file)):
                        print("Removing "+file)
                        os.remove(file)
                    else:
                        print(file+" already gone!")
        
        print("Removing "+archivepath)
        os.remove(archivepath)
        
    def getarchfile(self, line):
        return line[13:-1]
        
    def getattrfrommetadata(self, path):
        resname = self.structnames['hiddenresfolder']
        movieattributes = { 'indexfile':'',
                            'postersrc':'',
                            'title':'',
                            'year':'',
                            'runtime':'',
                            'roger':'',
                            'imdb':'',
                            'rotten':'',
                            'meta':'',}
                            
        metadatapath = path+'/'+resname+'/metadata.txt'
        
        with open(metadatapath,'r') as mdata:
            for line in mdata:
                vals = line.split('>')
                movieattributes.update({vals[0]:vals[1].strip()})
                
        return movieattributes
        
        
    ######################
    # Module-level stuff #
    ######################
    
def getconfiglist():
    #this should stay static as to not confuse anyone about the default 
    #CLI configs
    return ['guess','skip','test','force','destroy','debugnum',
            'searchfolder','localresources']
    
def getmoduleresources():
    #This also can be module-level as it's about the actual cinefiles.py 
    #file
    resfull = os.path.abspath(sys.modules['cinefiles'].__file__)
    res = resfull.split('/__init__.py')[0]
    res += '/resources'
    return res
    