from __future__ import unicode_literals

import youtube_dl
from urllib import parse
import requests
#from bs4 import beautifulsoup #beautifulsoup4
from selenium import webdriver
# from selenium.webdriver.phantomjs.phantomjs_binary import PhantomJSBinary
# from ghost import Ghost
# import cinefiles 

import logging
#from imdbparser import imdbparser.movie
from io import open as iopen
# from urllib.parse import urlsplit
from lxml import html ##, etree
import os, shutil
from string import Template
import json
import time

from langdetect import detect as detect_language


# from . import ydlhandlers as ydlhs
from . import templatex, cinefiles

# print(dir(Cinefiles))


class Title:  
    def __init__(self, folderstr, movie, caller=None, configdict={}):
        logging.info("Parsing "+folderstr)
        
        self.suffix_match = {'image/jpeg':'jpg','image/png':'png','image/bmp':'bmp',
                              'image/gif':'gif','image/svg+xml':'svg','image/tiff':'tiff',
                              'image/vnd.adobe.photoshop':'psd','image/x-citrix-jpeg':'jpg',
                              'image/x-citrix-png':'png','image/x-png':'png',}
        
        if(caller == None):
            self.higher = cinefiles.Cinefiles(internal_call=True)
        else:
            self.higher = caller
        
        self.movie = movie
        self.folderpath = folderstr
        self.configs = configdict
        
        self.initconfigs()
    
        
    
        
    
        self.checkarchive()
    
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.ERROR) #quiet this up a bit
        requests_log.propagate = True
    
    
        self.prephtml()
        
        
    
        ##self.movie.fetch() - we use requests right now
        try:
            self.process_movie()
            self.savemetadata()
        except Exception as e:
            logging.critical(str(e))
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
        
        
    def prephtml(self):
        self.rogerratingvalue = '0_0'
        self.rogerratingscale = '4'
        self.rogerratingauthor = "[No review found]"

        self.div = ''
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

#         self.ghostdriver = ghost()
#             service_args=["--webdriver-loglevel=SEVERE"])
        self.driver = webdriver.PhantomJS(
                port=0, 
                desired_capabilities={
                    'user-agent':'Mozilla/5.0 PhantomJS cinefiles',
                    'javascriptEnabled': True, 
                    'platform': 'ANY', 
                    'browserName': 'phantomjs', 
                    'version': ''}, 
                service_args=None, 
                service_log_path=None) 


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
  
    def logfiles(self):
        with open(self.archivefilename,'a') as archive:
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

                if(partlink == ''):
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

    def savetrailer(self, code):
        localres = self.higher.getstructurenames()['hiddenresfolder']

        if(not os.path.exists(localres)):
            os.makedirs(localres)

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

          self.trailerthumb = self.trailerfile[:-4]+'.jpg'
  
          self.trailerfile = localres+'/'+self.trailerfile
          self.trailerthumb = localres+'/'+self.trailerthumb
  
          prefix = self.folderpath+'/'
          self.addfiletolog(self.archivetypes['trailer-thumbnail'],prefix+self.trailerthumb)
          self.addfiletolog(self.archivetypes['trailer'],prefix+self.trailerfile)
          self.addfiletolog(self.archivetypes['ydlarch'],ydlarchive)
        except Exception as e:
          logging.critical(str(e))
          self.trailerfile=''



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
        self.rogereberthref = ''
        query = parse.urlencode({'q':self.ftitle+" site:www.rogerebert.com"})
        ## because screw using the API and it's limits
        googlereq = requests.get("https://www.google.com/search?"+query)
        print(".", end='', flush=True)
        logging.debug('Fetched '+googlereq.url)

        if(googlereq.status_code == requests.codes.ok):
            tree = html.fromstring(googlereq.content)

#             links = tree.xpath('//cite')
            links = tree.xpath('//div/h3[@class="r"]/a')
            findlink = links[0].attrib['href']
            findlink = findlink.split('?q=')[-1]
            findlink = findlink.split('&')[0]
            self.rogereberthref = findlink
#             self.rogereberthref = 'http://'+links[0].text_content()
#         logging.debug(self.rogereberthref)
        if(self.rogereberthref.find("www.rogerebert.com/reviews")>=0):
            ##scrape his review page
            rogerreq = requests.get(self.rogereberthref.replace(' ',''))
            print(".", end='', flush=True)
            logging.debug('Fetched '+rogerreq.url)

            if(rogerreq.status_code == requests.codes.ok):
                rogertree = html.fromstring(rogerreq.content)

                #get rating
                metarating = rogertree.xpath('//meta[@itemprop="ratingValue"]')[0]
                roger_float = float(metarating.values()[0])
                self.rogerratingvalue = str(int(roger_float)) #get the first digit
                self.rogerratingvalue += '_'+str(int(roger_float*10)-int(roger_float)*10) #add the tenths-place digit
                ## 3.5 => 3_5

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
            self.rogereberthref = ''
            self.review_first = ''
            self.review_rest = ''

    #Rotten Tomatoes scrape
    def rottentomatoes(self):
        # 43% (69/161)
        self.rottenhtml = ''
        self.rottenhref = 'https://www.rottentomatoes.com/m/'

        self.rottenrating = 'None'

        query = parse.urlencode({'q':self.ftitle+" site:www.rottentomatoes.com"})
        rottengreq = requests.get("https://www.google.com/search?"+query)
        print(".", end='', flush=True)
        logging.debug('Fetched '+rottengreq.url)

        if(rottengreq.ok):
          gtree = html.fromstring(rottengreq.content)
          links = gtree.xpath('//div[@class="kv"]/cite')
          self.rottenhref += links[0].text_content().split('/')[-2]
  
        #       logging.debug(self.rottenhref)
          rottenreq = requests.get(self.rottenhref.replace(' ',''))
          print(".", end='', flush=True)
          logging.debug('Fetched '+rottenreq.url)
  
          if(rottenreq.ok):
            tree = html.fromstring(rottenreq.content)
            percentage = tree.xpath('//a[@id="tomato_meter_link"]/span')
            self.rottenhtml += percentage[1].text_content()
            self.rottenrating = percentage[1].text_content()
            scorestats = tree.xpath('//div[@id="scoreStats"]/div[@class="superPageFontColor"]')
  
            fresh = scorestats[2].text_content().replace('\n','').replace('\t','').strip()
            fresh = fresh[fresh.find(':')+1:].strip()
            self.rottenhtml += ' ('+fresh+'/'
  
            numscored = scorestats[1].text_content().replace('\n','').replace('\t','').strip()
            numstr = numscored[numscored.find(':')+1:].strip()
            self.rottenhtml += numscored[numscored.find(':')+2:]+')'
          else:
            self.rottenhtml = "The 'tomatometer' couldn't be found."
        else:
          self.rottenhtml = "The rotten tomatoes link couldn't be found."

    # Get the metacritic off IMDB
    def metacritic(self):
        self.metacritichtml = ''
        self.metarating = 'None'
        #     45 (Based on 34 critic reviews provided by Metacritic.com)
        imdblink = 'http://www.imdb.com/title/tt'+self.movie.imdb_id+'/criticreviews'
        metareq = requests.get(imdblink)
        print(".", end='', flush=True)
        logging.debug('Fetched '+metareq.url)

        if(metareq.ok):
        #       logging.debug(str(dir(metareq)))
            metatree = html.fromstring(metareq.content)
            nocontent = metatree.xpath('//div[@id="main"]/div[@class="article"]/span[id="noContent"]')

            rating = metatree.xpath('//div[@class="metascore_wrap"]/div/span[@itemprop="ratingValue"]')
            reviewcount=metatree.xpath('//div[@class="metascore_block"]/span[@itemprop="ratingCount"]')
  
#             logging.debug(str(len(nocontent))+'-'+str(len(rating))+'-'+str(len(reviewcount)))
  
            if(len(nocontent)==0 and len(rating)>0 and len(reviewcount)>0):
            #       Yay we found some reviews
                self.metacritichtml+= rating[0].text
                self.metarating = rating[0].text
                self.metacritichtml+=" (Based on "
                reviewcount=metatree.xpath('//div[@class="metascore_block"]/span[@itemprop="ratingCount"]')
                self.metacritichtml+=reviewcount[0].text
                self.metacritichtml+=" critic reviews provided by <a href='"+imdblink+"'>Metacritic.com</a>)"
            else:
                # no metacritic :(
                self.metacritichtml = "No Metacritic information is available." 
        else:
          logging.error('Bad response on metacritic scrape'+str(metareq))



    ##################
    # Poster portion #
    ##################

    def getposter(self, url):
        # booleq = (self.archivetypes['poster'] in self.archivelist) or (self.configdict['force'])
        #     logging.debug('poster in dict>'+str(booleq))
        if (not self.archivetypes['poster'] in self.archivelist) and (not self.configs['force']):
          #This is a javascript loaded page...
          #preq = requests.get(url)
            try:
#                 content
                self.driver.set_window_size(1024, 768) #optional
                self.driver.get(url)
                
            
                print(".", end='', flush=True)
                logging.debug('Fetched with driver '+url)

                postertree = html.fromstring(self.driver.page_source) 
                imglist = postertree.xpath('//img[@class="pswp__img"]')
                for i in imglist:
                  if(i.attrib['style'].find('display') >= 0): #this is the displayed image
                    self.image_url = i.attrib['src']
                    break
                #self.image_url = postertree.xpath('//img[@class="pswp__img"]')[0].attrib['src']
                self.saveimage()
            except KeyboardInterrupt:
                logging.warn('Received KeyboardInterrupt')
                self.logfiles()
                exit()
            except Exception as e:
                logging.critical(str(e))
                self.logfiles()
                exit()
  
        else:
          logging.info('Skipping poster download')
          
          tempstr = self.archivelist[self.archivetypes['poster']]
#           toplevel = self.higher.configdict['searchfolder']
          relative_poster = tempstr.split(self.folderpath)[-1]
          self.postersrc = relative_poster[1:]


    def saveimage(self):
        imgreq = requests.get(self.image_url, stream=True)
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
          outname = self.folderpath+'/'+resfolder+'/'+self.movie.imdb_id+' POSTER'+'.'+suffix
  
          with iopen(outname, 'wb') as file:
            file.write(imgreq.content)

          self.postersrc = resfolder+'/'+self.movie.imdb_id+' POSTER'+'.'+suffix
          self.addfiletolog(self.archivetypes['poster'],outname)
        else:
          logging.error("Bad image request for title:"+title)
          logging.debug("Got code:"+imgreq.status_code+" and content-type:"+imgreq.headers['content-type'])



    ########################
    # Write the index.html #
    ########################

    def writeout(self):
        if (self.archivetypes['index'] not in self.archivelist
                and not self.configs['force']):
            logging.debug('Processing variables for index.html')
            with open(self.res_path+'index.html','r') as templatefile:
                templatehtml = templatex.TemplateX(templatefile.read().replace('\n', '').replace('\t', ''))

            pkeywords = ""
            for p in self.movie.plot_keywords:
                pkeywords+=p+' '
  
        #     twidth = int(self.metadata['width'])
        #     theight = int(self.metadata['height'])

            h5entries = self.movie.tree.xpath('//div[@class="info"]/h5')
            extended_movie_info = {}
            for e in h5entries:
                if(e.text is not None):
                    thiskey = e.text.strip()

                    next = e.getnext()
                    if(next is None or next.text is None):
                        thisvalue = ''
                    else:
                        thisvalue = next.text.replace('\n','').strip()

                    extended_movie_info.update({thiskey:thisvalue})
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
                if(wr>0):
                    writerhtml+=', '
                writerhtml += "<a href='http://www.imdb.com/name/nm"+self.movie.writers[wr].imdb_id+"'>"
                writerhtml += self.movie.writers[wr].name
                writerhtml += "</a>"
    
            if('Tagline:' in extended_movie_info):
                taglinetext = extended_movie_info['Tagline:']
            else:
                taglinetext = '[No tagline text found]'
  
            if('Plot:' in extended_movie_info):
                plottext = extended_movie_info['Plot:']
            else:
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
                if(d>0):
                    directorhtml+=', '
                directorhtml += "<a href='http://www.imdb.com/name/nm"+self.movie.directors[d].imdb_id+"'>"
                directorhtml += self.movie.directors[d].name
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
    
            actornum = len(self.movie.actors)
            actorhtml = ''
  
            for a in range(min(actornum,self.maxactors)):
                if(a>0):
                    actorhtml+=', '
                actorhtml += "<a href='http://www.imdb.com/name/nm"+self.movie.actors[a].imdb_id+"'>"
                actorhtml += self.movie.actors[a].name
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
                          'runtime':str(self.movie.duration),
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
                          'imdb_userrating':str(self.movie.rating),
                          'rottenlink':self.rottenhref,
                          'rotten_rating':self.rottenhtml,
                          'ttnumber':'tt'+self.movie.imdb_id,
                          'metacritic':self.metacritichtml  }
                  
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
            logging.info('Skipping making the index.html')
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
                      'runtime':str(self.movie.duration),
                      'roger':self.rogerratingvalue.replace('_','.'),
                      'imdb':str(self.movie.rating),
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
        detected_lang = detect_language(self.title)
        lang_code = self.configs['def_lang'].strip()
        if(detected_lang != lang_code):
            logging.debug(  "Original title is not in desired language:"
                            +lang_code)
            self.lang_title = ( '<br /><h4 class="inline">'
                                +self.movie.title+'&nbsp;'
                                +'</h4><h5 class="inline">'
                                +'(original title)</h5>'    )
                            
#             self.title = '(Desired language title not found)'
            for altt in self.movie.alternative_titles:
                check_lang = detect_language(altt)
                if(check_lang == lang_code):
                    self.title = altt
            
            
            
            if(self.title == self.movie.title):
                self.title = self.movie.title
                # self.lang_title = ( '<h5>(Desired language ('
#                                     +self.configs['def_lang']
#                                     +') title could not be found)</h5>')
                                
        if('override-title-list' in self.configs):
            for spec_title in self.configs['override-title-list']:
                if(spec_title.lower() == self.movie.title.lower()):
                    #We are keeping this title regardless
                    self.title = self.movie.title
                    self.lang_title = ''
                    logging.debug('Title change overridden by/to:'+spec_title)
                elif spec_title in self.movie.alternative_titles:
                    self.title = spec_title
        
        self.ftitle = self.movie.title+' ('+str(self.movie.year)+')'

    ###############################
    # The main handler/dispatcher #
    ###############################

    def process_movie(self):
        print("\tdownloading", end='', flush=True)
        base_url = self.movie._get_url()
        #     logging.debug(base_url)

        self.movie.fetch()
        
        print(".", end='', flush=True)
        logging.debug('Fetched '+base_url)
        #movie.fetch()
        #movie.tree
        #htmlparser = IMDBPageParser()

        #     if(r.status_code == requests.codes.ok):
        self.getrealtitle()

        tree = self.movie.tree 
        if(len(tree)>0): ##this is the wrong way to do this
  
            imgpage = "http://akas.imdb.com"
            imgpage += tree.xpath('//a[@name="poster"]')[0].attrib['href']

            self.getposter(imgpage)
            self.findyoutubetrailer()

            self.div+=html.tostring(tree.xpath('//div[@id="tn15main"]')[0]).decode('utf-8')

            if (self.archivetypes['index'] not in self.archivelist
                    and not self.configs['force']):
                self.getreviews()
                self.writeout()
            else:
                logging.info("Not writing index.html, already exists")
                self.indexfile = self.archivelist[self.archivetypes['index']]
    
        else:
            logging.error("Couldn't get IMDb movie from link")
        #       loggin.debug("Got code:"r.status_code)
            print("ERROR!! ", end='', flush=True)
          #log.append(MovieLog(file.name, "IMDb download error -   "+r.status_code))
        print("done")
#         open(self.folderpath+'/'+self.higher.getstructurenames()['hiddencompletelog'],'a').close()
