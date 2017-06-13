from __future__ import unicode_literals

import youtube_dl
from urllib import parse
import requests


import logging
from io import open as iopen
# from urllib.parse import urlsplit
from lxml import html ##, etree
import os, shutil, ctypes
from string import Template
import json
import time


# from . import ydlhandlers as ydlhs
from . import templatex, cinefiles
from .__init__ import __version__
# print(dir(Cinefiles))


class Title:  

    def __init__(self, folderstr, movieobj, caller=None, configdict={}):
        logging.info("Parsing "+folderstr)
        
        self.suffix_match = {'image/jpeg':'jpg','image/png':'png','image/bmp':'bmp',
                              'image/gif':'gif','image/svg+xml':'svg','image/tiff':'tiff',
                              'image/vnd.adobe.photoshop':'psd','image/x-citrix-jpeg':'jpg',
                              'image/x-citrix-png':'png','image/x-png':'png',}
        
        if(caller == None):
            self.higher = cinefiles.Cinefiles(internal_call=True)
        else:
            self.higher = caller
        
        self.movie = movieobj
        self.folderpath = folderstr
        self.configs = configdict
        
        self.initconfigs()
    
        self.checkarchive()
    
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.ERROR) #quiet this up a bit
        requests_log.propagate = True
    
        self.prephtml()

        try:
            self.process_movie()
            self.savemetadata()
        except Exception as e:
            self.higher.critical(e)
            print('ERROR!')
        finally:
    #       logging.debug('Finally writing archive:'+str(self.filearchive))
            self.logfiles()
    
    
    ################
    # INIT Portion #
    ################

    ## really only for user-called version of this class - which shouldn't happen
    def initconfigs(self):
        self.texticons = ['/','-','\\','|']
    
        self.archivelist = {}#existing files [type:name]
        self.filearchive = []#files written this time in form of [time,type,name]
        self.archivetypes = { 'trailer':'T',
                              'poster':'P', 
                              'trailer-thumbnail':'t', 
                              'index':'H',
                              'ydlarch':'y',}
        
        for c in cinefiles.getconfiglist():
            #this overwrites non-relevant debugnum to false - this doesn't matter
            if c not in self.configs:
                self.configs.update({c:False})
        if 'def_lang' not in self.configs:
            self.configs.update({'def_lang':'en'})

        archivename = self.higher.getstructurenames()['archive']
        self.archivefilename = self.folderpath+'/'+archivename

        self.maxactors = 10
        
        self.indexfile = ''
        self.lang_title = ''
        
        
        
        self.postersrc = ''
        self.trailerthumb = ''
        self.trailerfile = ''
        self.rogerratingvalue = '0_0'
        self.rottenrating = ''
        self.metarating = ''
        
        self.archiveheader = (
            '# This file is used by cinefiles.py to track what \n'
            +'# components have been downloaded. If you delete this \n'
            +'# file, then Cinefiles().run() will re-download and \n'
            +'# index this folder.\n')
            
        self.title = self.movie.title
        
        self.updated = False
        if('force_index' in self.configs):
            self.updated = self.configs['force_index']
        
    def prephtml(self):
        self.rogerratingvalue = '0_0'
        self.rogerratingscale = '4'
        self.rogerratingauthor = "[No review found]"

#         self.div = ''
        self.writernum = 0 ###TODO: init all html variables to be safe
        ##need to support windows style:
        #     self.rel_path = self.folderpath+'/../resources/'
        if not self.configs['localresources']:
          self.res_path = cinefiles.getmoduleresources()+'/'
        else:
          self.res_path = (self.folderpath+'/'
                          +self.higher.getstructurenames()['hiddenresfolder']
                          +'/')
        #this is the main file we have to be very careful to be backwards compatible with



    def checkarchive(self):
        if(os.path.exists(self.archivefilename)):
            with open(self.archivefilename,'r') as archive:
                for line in archive:
                    if not line.startswith('#'):
                        typechar = line[11:12]
                        filename = line[13:-1]
                        self.archivelist.update({typechar:filename})

                        if(not self.configs['force']):
                          #so that we don't have multiple ghost file archive lists
                          #this only adds files if we aren't going to overwrite them later
                          #this is because we clear the archive every run
                          self.addfiletolog(typechar,filename)
        else:
            with open(self.archivefilename,'a') as newarchive:
                newarchive.write('#'+__version__+'\n'
                                 +self.archiveheader)
    
            logging.debug('Created new '+self.archivefilename)
#           should we auto-hide the archive? Let's go with no, for now..
#             if(self.onwindows and self.higher.configdict['win_hide']):
#                 FILE_ATTRIBUTE_HIDDEN = 0x02
#                 hide = ctypes.windll.kernel32.SetFileAttributesW(
#                                                 self.archivefilename,
#                                                 FILE_ATTRIBUTE_HIDDEN)
#                 if not hide: # There was an error.
#                     raise ctypes.WinError()
  
    def logfiles(self):
        with open(self.archivefilename,'w') as archive:
            for f in self.filearchive:
                archive.write(f[0]+':'+f[1]+':'+f[2]+'\n')

    def addfiletolog(self,type,filename):
        #time() string is 18 characters
        #type is 1 character
        timestr = str(time.time())[0:10]
        self.filearchive.append([timestr,type,filename])

    def purgefiles(self):
        if(self.configs['destroy']):
            ###TODO share from self.checkarchive()
            with open(self.archivefilename,'r') as archive:
                for line in archive:
                    os.remove(line[21:-1])
                    logging.info('Deleted '+line[21:-1])
            os.remove(self.archivefilename)
            logging.info('Deleted '+self.archivefilename)
        else:
          logging.error('Did not purge files, destroy-flag not set to '
                        +'True')

    def omdbsearch(self):
        self.omdbdata = {}
        self.omdbdata.update({'imdbRating':'','tomatoURL':''})
        try:
            baseurl = 'http://www.omdbapi.com/?'
            query = parse.urlencode({   'i':self.movie.imdb_id,
                                        'tomatoes':'true',})
            fullurl = baseurl+query
            req = requests.get(fullurl)
            print('.',end='',flush=True)
            data = json.loads(req.text)
            self.omdbdata.update(data)
        except Exception as err:
            logging.error("Error fetching OMDb info: "+str(err))

    ####################
    # Trailer download #
    ####################

    def findyoutubetrailer(self):
        if((not self.archivetypes['trailer'] in self.archivelist) 
            and (not self.configs['force'])):

            search_query = {"search_query" : 'official trailer ' 
                            +self.ftitle}

            ytreq = requests.get("http://www.youtube.com/results", 
                                 stream=True, params=search_query)
            ytreq.raw.decode_content = True # handle spurious Content-Encoding
            print(".", end='', flush=True)
            logging.debug('Fetched '+ytreq.url)

            if(ytreq.status_code == requests.codes.ok):
                tree = html.fromstring(ytreq.content)
                partlink = ''

                results = tree.xpath('//h3[@class="yt-lockup-title "]') 

                partlink = self.getytfirstlink(results)

                if(partlink == '' or partlink is None):
                    logging.error(  "Couldn't find suitable youtube"
                                    + "trailer")
                else:
                    videocode = partlink.split('=')[1]
                    self.savetrailer(videocode)
            else:
                logging.error("Bad youtube request for title:"+title)
                logging.debug("Got code:"+ytreq.status_code)

        else:
            logging.info('Skipping trailer download')
            atrail = self.archivetypes['trailer']
            atrailthumb = self.archivetypes['trailer-thumbnail']
            relative_trailer = self.archivelist[atrail].split(self.folderpath)[-1]
            self.trailerfile = relative_trailer[1:]
            
            relative_thumb = self.archivelist[atrailthumb].split(self.folderpath)[-1]
            self.trailerthumb = relative_thumb[1:]

    def getytfirstlink(self,h3_tree):
        for h3 in h3_tree:
            for child in h3.iterchildren():
                if(child.tag == "a"):
                    if(child.text_content().lower().find('trailer')>=0):
                        for item in child.values():
                            if(item.find('watch')>=0):
                                return item
                        #return first one

    def ydlprogressterm(self):
        if(self.iconnum >= len(self.texticons)):
            self.iconnum = 0
        print('\b'+self.texticons[self.iconnum], end='', flush=True)
        self.iconnum += 1

    def ydlhook(self, d):
        #only for filedownloader - youtube-dl constraint
        if(d['status'] == 'downloading'):
            self.ydlprogressterm()
        elif(d['status'] == 'finished'):
            print("\b.", end='', flush=True)
            self.trailerfile = d['filename'].split('/')[-1]
        elif(d['status'] == 'error'):
            logging.warn('Failed to download youtube trailer')
            self.trailersuccess = False

    def savetrailer(self, code):
        self.trailersuccess = True
        localres = self.higher.getstructurenames()['hiddenresfolder']

        if(not os.path.exists(localres)):
            os.makedirs(localres)
            if(running_on_windows() and self.higher.configdict['win_hide']):
                FILE_ATTRIBUTE_HIDDEN = 0x02
                hide = ctypes.windll.kernel32.SetFileAttributesW(
                                                localres,
                                                FILE_ATTRIBUTE_HIDDEN)
                if not hide: # There was an error.
                    raise ctypes.WinError()

        self.iconnum = 0

        ydlarchive = self.folderpath+'/'+localres+'/ydlarchive'

        ydl_opts = {
          'quiet'         :True,
          'ignoreerrors'  :True,
          'format'        :'best[ext=mp4]/best',
          'postprocessors':[{'key':'FFmpegVideoConvertor','preferedformat':'mp4'}],
          'nooverwrites'  :not self.configs['destroy'], #deletes old .thumb.jpg and *.mp4
          ###'logger'        :ydlhs.loghandler(),
          'writethumbnail':True,
          'skip_download' :self.configs['test'],
          'progress_hooks':[self.ydlhook],
        #       'writeinfojson' :True,
          'outtmpl':self.folderpath+'/'+localres+'/%(title)s.%(ext)s',
          'restrictfilenames':True,
          'download_archive':ydlarchive
        }

        fixedcode = "https://www.youtube.com/watch?v="+code

        #       logging.debug(str(ydl_opts))
        logging.debug('Trailer at '+fixedcode)

        try:
            print('X',end='',flush=True)

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([fixedcode])
    
            if(self.trailerfile == ''):
                logging.warn('Failed to download youtube trailer')
                self.trailersuccess = False

            if(self.trailersuccess):
                self.trailerthumb = self.trailerfile[:-4]+'.jpg'

                self.trailerfile = localres+'/'+self.trailerfile
                self.trailerthumb = localres+'/'+self.trailerthumb

                prefix = self.folderpath+'/'
                self.addfiletolog(self.archivetypes['trailer-thumbnail'],prefix+self.trailerthumb)
                self.addfiletolog(self.archivetypes['trailer'],prefix+self.trailerfile)
                self.addfiletolog(self.archivetypes['ydlarch'],ydlarchive)
        except Exception as e:
            logging.warn(str(e))
            self.trailerfile=''

        self.updated = self.updated or self.trailersuccess


    ###################
    # Reviews portion #
    ###################

    ## TODO: see if a website out there already has this info so we can do fewer request

    def getreviews(self):
        self.getrogerebertinfo()
        self.rottentomatoes()
        self.metacritic()

    #Roger ebert info scrape
    def getrogerebertinfo(self):
        qtitle = ''
        if(self.movie.ftitle == ''):
            qtitle = self.movie.title
        else:
            qtitle = self.movie.ftitle
        self.rogereberthref = self.higher.rogersearchengine.get_link(qtitle)
        if(self.rogereberthref.find("www.rogerebert.com/reviews")>=0):
            ##scrape his review page
            rogerreq = requests.get(self.rogereberthref.replace(' ',''))
            print(".", end='', flush=True)
            logging.debug('Fetched '+rogerreq.url)

            if(rogerreq.status_code == requests.codes.ok):
                rogertree = html.fromstring(rogerreq.content)

                #get rating
                metarating = []
                if(len(rogertree.xpath('//meta[@itemprop="ratingValue"]')) > 0):
                    metarating = rogertree.xpath('//meta[@itemprop="ratingValue"]')[0]
                if(len(metarating.values()) > 0):
                    roger_float = float(metarating.values()[0])
                    self.rogerratingvalue = str(int(roger_float)) #get the first digit
                    self.rogerratingvalue += '_'+str(int(roger_float*10)-int(roger_float)*10) #add the tenths-place digit
                    ## 3.5 => 3_5
                else:
                    self.rogerratingvalue = '0_0'

                # metascale = rogertree.xpath('//meta[@itemprop="bestRating"]')[0]
                #         self.rogerratingscale = metascale.values()[0]
                authspan = rogertree.xpath('//span[@itemprop="author"]/span[@itemprop="name"]')[0]
                if((authspan is not None) and (authspan.text is not None)):
                    self.rogerratingauthor = authspan.text

                #get review
                reviewroot = rogertree.xpath('//div[@itemprop="reviewBody"]')[0]
                self.review_p = []
                for subtree in reviewroot.getiterator():
                    if((subtree.tag is not None) and (subtree.tag=='p')):
                        self.review_p.append(subtree.text_content())
                    if((subtree.tag is not None) and (subtree.tag=='h4')): ##review is over
                        break

                para = 0
                while(para < len(self.review_p)):
                    #get rid of those pesky 'Advertisements
                    if(self.review_p[para]=='Advertisement'):
                        self.review_p.pop(para)
                    para += 1

                self.review_first = self.review_p[0]
                self.review_rest = ''

                for a in range(1,len(self.review_p)):
                  self.review_rest += '<p>'+self.review_p[a]+'</p>'
            else:
                self.rogereberthref = ''
                self.review_first = ''
                self.review_rest = ''
        else:
            ##either didn't find it or returned non-review link
            logging.info("No roger ebert review found for "
                        +self.movie.ftitle+" ("+self.rogereberthref+")")
            self.rogereberthref = ''
            self.review_first = ''
            self.review_rest = ''

    #Rotten Tomatoes scrape
    def rottentomatoes(self):
        # 43% (69/161)
        self.rottenhtml = ''
        self.rottenhref = self.omdbdata['tomatoURL']
        self.rottenrating = 'None'
        if(self.rottenhref.lower().find('http') >= 0):
            rottenreq = requests.get(self.rottenhref)
            print(".", end='', flush=True)
            logging.debug('Fetched '+rottenreq.url)

            if(rottenreq.ok):
                tree = html.fromstring(rottenreq.content)
                percentage = tree.xpath('//a[@id="tomato_meter_link"]/span')
                scorestats = tree.xpath('//div[@id="scoreStats"]/div[@class="superPageFontColor"]')
                if(len(percentage) > 0 and len(scorestats) >= 2):
                    self.rottenhtml += percentage[1].text_content()
                    self.rottenrating = percentage[1].text_content()
                    fresh = scorestats[2].text_content().replace('\n','').replace('\t','').strip()
                    fresh = fresh[fresh.find(':')+1:].strip()
                    self.rottenhtml += ' ('+fresh+'/'

                    numscored = scorestats[1].text_content().replace('\n','').replace('\t','').strip()
                    numstr = numscored[numscored.find(':')+1:].strip()
                    self.rottenhtml += numscored[numscored.find(':')+2:]+')'
                else:
                    self.rottenhtml = "The 'tomatometer' couldn't be found."
                    logging.error('There was a problem with the tomato meter. % ='
                                    +str(percentage)+'\nscorestats = '+str(scorestats)
                                    +'\n@'+rottenreq.url)
            else:
                self.rottenhtml = "The 'tomatometer' had a problem during parsing."
        else:
            self.rottenhtml = "No rotten tomatoes exists for this movie."

    # Get the metacritic off OMDb
    def metacritic(self):
        #http://www.metacritic.com/search/all/pride+and+prejudice+and+zombies/results
        self.metacritichtml = ''
        if('Metascore' in self.omdbdata.keys()):
            self.metacritichtml = self.omdbdata['Metascore']
            self.metarating = self.omdbdata['Metascore']
        else:
            logging.debug("No metacritic key from OMDb")
            



    ##################
    # Poster portion #
    ##################

    def getposter(self, url):
        # booleq = (self.archivetypes['poster'] in self.archivelist) or (self.configdict['force'])
        #     logging.debug('poster in dict>'+str(booleq))
        if (not self.archivetypes['poster'] in self.archivelist) and (not self.configs['force']):  
            self.saveimage(url)
            self.updated = True
        else:
            logging.info('Skipping poster download')
            tempstr = self.archivelist[self.archivetypes['poster']]
            relative_poster = tempstr.split(self.folderpath)[-1]
            self.postersrc = relative_poster[1:]


    def saveimage(self, url):
        imgreq = requests.get(url, stream=True)
        imgreq.raw.decode_content = True # handle spurious Content-Encoding
        print(".", end='', flush=True)
        logging.debug('Fetched '+imgreq.url)

        if(imgreq.headers['content-type'] in self.suffix_match and 
            imgreq.status_code == requests.codes.ok):
  
          resfolder = self.higher.getstructurenames()['hiddenresfolder']
          #make path if not there
          if(not os.path.exists(resfolder)):
            os.makedirs(resfolder)
  
          suffix = self.suffix_match[imgreq.headers['content-type']]
          outname = self.folderpath+'/'+resfolder+'/'+self.movie.id+' POSTER'+'.'+suffix
  
          with iopen(outname, 'wb') as file:
            file.write(imgreq.content)

          self.postersrc = resfolder+'/'+self.movie.id+' POSTER'+'.'+suffix
          self.addfiletolog(self.archivetypes['poster'],outname)
        else:
          logging.error("Bad image request for title:"+title)
          logging.debug("Got code:"+imgreq.status_code+" and content-type:"+imgreq.headers['content-type'])



    ########################
    # Write the index.html #
    ########################

    def writeout(self):
        if (self.archivetypes['index'] not in self.archivelist or
                self.configs['force'] or self.updated):
            logging.debug('Processing variables for index.htm')
            with open(self.res_path+'index.html','r') as templatefile:
                templatehtml = templatex.TemplateX(templatefile.read().replace('\n', '').replace('\t', ''))

            pkeywords = ''
#             for p in self.movie.plot_keywords:
#                 pkeywords+=p+' '
  
        #     twidth = int(self.metadata['width'])
        #     theight = int(self.metadata['height'])

#             h5entries = self.movie.tree.xpath('//div[@class="info"]/h5')
#             extended_movie_info = {}
#             for e in h5entries:
#                 if(e.text is not None):
#                     thiskey = e.text.strip()
# 
#                     next = e.getnext()
#                     if(next is None or next.text is None):
#                         thisvalue = ''
#                     else:
#                         thisvalue = next.text.replace('\n','').strip()
# 
#                     extended_movie_info.update({thiskey:thisvalue})
              ##not really that great, misses all linked text
    
        #         if(thiskey=='Writers:' or thiskey=='Writer:'):
        #           #dependent on only 1 match of 'Writers:' - pretty safe IMO
        #           self.writerhtml = ''
        #           
        #           writerdiv = e.getnext()
        #           for(subtag in writerdiv.iterchildren()):
        #             if(subtag.tag.lower() == 'a'): #got to skip the '<br>'
        #               self.writernum+=1
        #               if(self.writernum>1):
        #                 writerhtml+=', '
        #               
        #               writerhtml+="<a href='http://akas.imdb.com"+subtag.values()[0]+"'>"
        #               writerhtml+=subtag.text
        #               writerhtml+='</a>'+subtag.tail
            writernum = len(self.movie.writers)
            writerhtml = ''
            for wr in range(writernum):
                writerdict = self.movie.writers[wr]
                if(wr>0):
                    writerhtml+=', '
                writerhtml += "<a href='https://www.themoviedb.org/person/"+str(writerdict['id'])+"'>"
                writerhtml += writerdict['name']
                writerhtml += "</a>"
    
            taglinetext = self.movie.tagline
            if(taglinetext==''):
                taglinetext = '[No tagline text found]'
  
            plottext = self.movie.overview
            if(plottext==''):
                plottext = '[No plot text found]'

        #     directors = self.movie.tree.xpath('//div[@id="director-info"]/div[@class="info-content"]/a')
        #     directorhtml = ''
        #     for d in range(len(directors)):
        #       directorhtml += "<a href='http://akas.imdb.com"+directors[d].values()[0]+"'>"
        #       directorhtml += directors[d].text
        #       directorhtml += "</a>"
        #       if(d<len(directors)-1):
        #         directorhtml+=', '

            directornum = 0
            directorhtml = ''
        #       logging.debug(str(dir(self.movie)))
        #       logging.debug(self.movie.directors)
            for d in range(len(self.movie.directors)):
                directordict = self.movie.directors[d]
                if(d>0):
                    directorhtml+=', '
                directorhtml += "<a href='http://www.imdb.com/name/nm"+str(directordict['id'])+"'>"
                directorhtml += directordict['name']
                directorhtml += "</a>"

            if(len(self.movie.directors)==0):
                directornumtxt = '[No director information found]'
            elif(len(self.movie.directors)==1):
                directornumtxt = 'Director:'
            else:
                directornumtxt = 'Directors:'
  
            if(writernum>1):
                writernumtxt = 'Writers:'
            else:
                writernumtxt = 'Writer:'
    
            actornum = len(self.movie.cast)
            actorhtml = ''
  
            for a in range(min(actornum,self.maxactors)):
                actordict = self.movie.cast[a]
                if(a>0):
                    actorhtml+=', '
                actorhtml += "<a href='https://www.themoviedb.org/person/"+str(actordict['id'])+"'>"
                actorhtml += actordict['name']
                actorhtml += "</a>"
    
            if(actornum>1):
                actornumtxt = 'Actors:'
            else:
                actornumtxt = 'Actor:'
    
          ## All of this should be relative links if it is locally stored

            if not self.configs['localresources']:
                res_folder = '../'+self.higher.getstructurenames()['hiddenresfolder']
            else:
                res_folder = self.higher.getstructurenames()['hiddenresfolder']

            headjs = ''
            jsdict = {'trailer_thumbnail':self.trailerthumb,
                    'trailer_source': self.trailerfile}
            
            if(os.path.exists(self.folderpath+'/'+self.trailerfile)):
                with open(self.res_path+'script-insert.html','r') as templatefile:
                    jstemplate = templatex.TemplateX(templatefile.read().replace('\n', '').replace('\t', ''))
                    headjs = jstemplate.substitute(jsdict)
      
        #       logging.debug(jsdict)

            replacedict = { 'headertitle':self.ftitle,
                          'keywords':pkeywords,
                          'cf_res':res_folder,
                          'trailer_thumbnail':self.trailerthumb,
                          'trailer_source': self.trailerfile,
                          'title':self.title,
                          'alt_title':self.lang_title,
                          'header_script': headjs,
                          'postersrc':self.postersrc,
                          'year':str(self.movie.year),
                          'tagline':taglinetext,
                          'runtime':str(self.movie.runtime),
                          'plot':plottext,
                          'directornum':directornumtxt,
                          'directors':directorhtml,
                          'writernum':writernumtxt,
                          'writers':writerhtml,
                          'actornum':actornumtxt,
                          'actors':actorhtml,
                          'rogerebertlink':self.rogereberthref,
                          'rogerrating':self.rogerratingvalue,
                          'rogername':self.rogerratingauthor,
                          'rogertext1':self.review_first,
                          'rogertextx':self.review_rest,
                          'imdb_userrating':self.omdbdata['imdbRating'],
                          'rottenlink':self.rottenhref,
                          'rotten_rating':self.rottenhtml,
                          'ttnumber':self.movie.imdb_id,
                          'metacritic':self.metacritichtml,
                          'tmdb_logo':res_folder+'/images/tmdb-attribution-rectangle.png'}
                  
        #       logging.debug(replacedict)
                
        #       logging.debug(str(replacedict))

        #       templatehtml.safe_substitute({headertitle:self.ftitle,
            writeouthtml = templatehtml.substitute(replacedict)
                                
  

            htmlfilename = self.folderpath+"/index.htm"

            if(os.path.isfile(htmlfilename)):
                os.remove(htmlfilename)

            with iopen(htmlfilename, 'x') as file:
                file.write(writeouthtml)

            self.addfiletolog(self.archivetypes['index'],htmlfilename)
            self.indexfile = htmlfilename
        else:
            ##File already written
            logging.info('Skipping making the index.htm')
            #self.addfiletolog(self.archivetypes['index'],self.archivelist[self.archivetypes['index']])
            self.indexfile = self.archivelist[self.archivetypes['index']]

    def getattributes(self):
#         logging.debug('Getting attributes..')
#         logging.debug(self.archivelist)
        top_level = self.higher.configdict['searchfolder']
        foldername = self.folderpath.split(top_level)[-1]
        #remove leading /
        foldername = foldername[1:]
        
        attributes = {'foldername':foldername,
                      'postersrc':self.postersrc,
                      'title':self.title,
                      'year':str(self.movie.year),
                      'runtime':str(self.movie.runtime),
                      'roger':self.rogerratingvalue.replace('_','.'),
                      'imdb':self.omdbdata['imdbRating'],
                      'rotten':self.rottenrating,
                      'meta':self.metarating}
        return attributes
        
    def savemetadata(self):
        metafile = self.res_path+'metadata.txt'
        metadata = ''
        attr = self.getattributes()
        for key in attr:
            metadata += key+'>'+attr[key]+'\n'
            
        if(os.path.isfile(metafile)):
            os.remove(metafile)
        with iopen(metafile, 'x') as file:
            file.write(metadata)
    
    def getrealtitle(self):
        self.title = self.movie.title
        self.lang_title = ''
        if(self.movie.title!=self.movie.original_title):
            logging.debug(  "Received title is not original title")
            self.lang_title = ( '<br /><h4 class="inline">'
                                +self.title+'&nbsp;'
                                +'</h4><h5 class="inline">'
                                +'(original title)</h5>'    )
            self.title = self.movie.original_title
        
        self.ftitle = self.title+' ('+str(self.movie.year)+')'

    ###############################
    # The main handler/dispatcher #
    ###############################

    def process_movie(self):
        print("\tdownloading", end='', flush=True)
#         base_url = self.movie._get_url()
        #     logging.debug(base_url)

        self.movie.fetchinfo()
        print(".", end='', flush=True)
        logging.debug('Fetched info on '+self.title)
        
        self.omdbsearch()

        #     if(r.status_code == requests.codes.ok):
        self.getrealtitle()

        self.getposter(self.movie.poster_path)
        self.findyoutubetrailer()

        indexnotinarch = self.archivetypes['index'] not in self.archivelist
        if(indexnotinarch or self.updated or self.configs['force']):
            self.getreviews()
            self.writeout()
        else:
            logging.info("Not writing index.htm, already exists and no updates")
            self.indexfile = self.archivelist[self.archivetypes['index']]
          #log.append(MovieLog(file.name, "IMDb download error -   "+r.status_code))
        print("done")
#         open(self.folderpath+'/'+self.higher.getstructurenames()['hiddencompletelog'],'a').close()
