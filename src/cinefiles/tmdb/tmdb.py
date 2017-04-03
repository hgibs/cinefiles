from urllib import parse
import requests
import json
import pycountry
import logging
from math import floor
from time import sleep, time

from . import movie, exceptions

class TMDb:
    def __init__(self, api_key, language='en', region='US'):
        self.api_key = api_key
        langs = []
        for lang in pycountry.languages:
            if hasattr(lang, 'alpha_2'):
                langs.append(lang.alpha_2)
                
        self.lang = language[0:2].lower() #ISO 639-1 standard, i.e. 'en'
        if(not self.lang in langs):
            raise Exception(self.lang+" is not a valid ISO-639-1 language code")
            
        self.region = region
        if(region is not None):
            regions = []
            checkregion = region[0:2].upper()
            for country in pycountry.countries:
                if hasattr(country, 'alpha_2'):
                    regions.append(country.alpha_2)
            if(not checkregion in regions):
                raise Exception(region+" is not a valid ISO-3166-1 country code")
            self.region = checkregion
          
        self.safetime = 0.0
        self.process_api_configs()
            
        
    
    def process_api_configs(self):
        query = parse.urlencode({'api_key':self.api_key})
        baseurl = 'https://api.themoviedb.org/3/configuration?'
        fullurl = baseurl+query
        req = self.safeapi(fullurl)
        data = json.loads(req.text)
        
        self.imgbase = data['images']['secure_base_url']
        self.imgsize = 'original'
        self.available_poster_sizes = data['images']['poster_sizes']
        self.available_backdrop_sizes = data['images']['backdrop_sizes']
    
    def search(self, title, year=None):
        results = []
        #not searching by region, to get maximum results
        api_dict = {'api_key':self.api_key,
                    'query':title}
                    
        if(year is not None):
            api_dict.update({'year':str(year)})
        query = parse.urlencode(api_dict)
        baseurl = 'https://api.themoviedb.org/3/search/movie?'
        fullurl = baseurl+query
        req = self.safeapi(fullurl)
        data = json.loads(req.text)
        for res in data['results']:
            
            newmovie = movie.Movie(res,self)
            results.append(newmovie)
            
        return results
        
    def getmovie(self, id):
        idnum = int(id)
        return movie.Movie({'id':idnum},self)
        
        
    def safeapi(self, url, callnum=0):
#         now = floor(time())
        sleepdelta = self.safetime-time()
        if(sleepdelta > 0):
            #wait until safe to start API access again
            logging.info("TMDb API is reaching rate limit - please notify the API owner!")
            sleep(sleepdelta)
        thisrequest = requests.get(url)
        if(thisrequest.ok):
            self.safetime = self.checktime(thisrequest)
            if(self.getremainingreqs(thisrequest) < 3):
                #with small buffer, set wait-out until rate-limit clears
                self.safetime = self.getresettime(thisrequest)
        elif(thisrequest.status_code == 429 and callnum < 3):
            self.sleepuntil(self.getresettime(thisrequest))
            return self.safeapi(url,1)
        else:
            tdata = json.loads(thisrequest.text)
            if('status_code' in tdata):
                if(tdata['status_code']==7):
                    raise exceptions.APIKeyException(tdata['status_message'])
            raise requests.exceptions.ConnectionError('Request got code '+str(thisrequest.status_code))
            return None
        
        return thisrequest
            
    def checktime(self, request):
        #returns the time the next request should wait to before starting
        #make sure we aren't exceeding our rate limit of 40 requests / 10 seconds
        now = floor(time())
        resettime = self.getresettime(request)
        secondsrem = (resettime-now)
        #average 4/second
        reqsrem = self.getremainingreqs(request)
        if(secondsrem > 0):
            reqratio = reqsrem/secondsrem
            if(reqsrem <= 1):
                #be safe and wait it out
                return float(request.headers['X-RateLimit-Reset'])
            if(reqratio < 4.0):
                #wait until average is back up to 4.0/sec
                sleepdelta = secondsrem-(reqsrem-1)/reqratio
                return now+sleepdelta
            else:
                #ratio is good
                return now
        else:
            #0 seconds remaining
            return now
            
    def getresettime(self, request):
        if('X-RateLimit-Reset' in request.headers):
            return float(request.headers['X-RateLimit-Reset'])
        else:
            tdata = json.loads(request.text)
            if('Retry-After' in tdata):
                return time()+float(tdata['Retry-After'])
            else:
                return time()+10.0
        
    def getremainingreqs(self, request):
        if('X-RateLimit-Remaining' in request.headers):
            return float(request.headers['X-RateLimit-Remaining'])
        else:
            return 0
        
    def sleepuntil(self, endtime):
        delta = endtime-time()
        if(delta > 0):
            sleep(delta)
        
    