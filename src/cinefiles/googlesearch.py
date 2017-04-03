from apiclient.discovery import build
from apiclient.errors import HttpError
from urllib import parse
import json
import logging
import requests
from lxml import html

# Here's my free API, please don't steal it. Or do, I don't really care.
# You're only stealing the free API key anyway. Which is, you know, free
# to make yourself.
GOOGLE_FREE_API_KEY = 'AIzaSyBLkr83ZK5OoGAUx0O4sizJc9UuKHRmTeA'
ROGEREBERT_SEARCH_ENGINE_ID = '011435517851099762049:tg32kab0kxe'

class GoogleSearch:
    
    def __init__(self):
        logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
        logging.getLogger('googleapiclient.discovery').setLevel(logging.WARNING)
        # The build function creates a service object. It takes an API name and API
        # version as arguments.
        #note: this can take a few seconds to build
        service = build('customsearch', 'v1', developerKey=GOOGLE_FREE_API_KEY)
        # A collection is a set of resources. We know this one is called "cse"
        # because the CustomSearch API page tells us cse "Returns the cse Resource".
        self.collection = service.cse()
#         self.linksearch = {'roger':True,'link':True,'scrape':True}
        self.get_link = self.try_ALL_API
        self.cxselect = ROGEREBERT_SEARCH_ENGINE_ID
        
    def try_ALL_API(self, query):
        #first try using his provided API
        link = ''
        try:
            link = self.use_roger_API(query)
        except Exception as err:
            logging.error(str(err))
            link = ''
        
        if(link!=''):
            return link
            
            
        #that didn't work, use mine
        logging.debug("use_roger_API failed")
        try:
            link = self.get_link_API(query)
        except:
            link = ''
        
        if(link!=''):
            return link
            
        #damn both APIs are down, just scrape google I guess
        logging.debug("get_link_API failed")
        try:
            link = self.get_link_scrape(query)
        except:
            link = ''
        
        return link

    def use_roger_API(self, query):
        baseurl = 'https://www.googleapis.com/customsearch/v1element?'
        querydict = parse.urlencode({   'key':'AIzaSyCVAXiUzRYsML1Pv6RwSG1gunmMikTzQqY',
                                        'rsz':'filtered_cse',
                                        'num':'10',
                                        'hl':'en',
                                        'prettyPrint':'false',
                                        'source':'gcsc',
                                        'gss':'.com',
                                        'sig':'581c068e7ad56cae00e4e2e8f7dc3837',
                                        'cx':'004943367334924041372:turuh-9ckxm',
                                        'googlehost':'www.google.com',
                                        'gs_l':'partner.12...218683.226149.0.235267.12.10.0.0.0.0.2971.12428.4-2j3j2j9-3.10.0.gsnos%2Cn%3D13...0.7497j30721759j12j1..1ac.1.25.partner..11.1.431.izeCjn_DLtQ',
                                        'q':query,})
        fullurl = baseurl+querydict
        req = requests.get(fullurl)
        print('.',end='',flush=True)
        data = json.loads(req.text)
        self.debugroger = data
        if('results' in data):
            results = data['results']
            if(len(results) > 0):
                firstresult = results[0]
                if('unescapedUrl' in firstresult):
                    return firstresult['unescapedUrl']
                
        return ''
    
    def get_link_API(self, query):
        request = self.collection.list( q=query,
                                        num=10, #default is 10 anyway
                                        start=1,
                                        cx=self.cxselect,)
        try:
            response = request.execute()
            print(".", end='', flush=True)
        except HttpError as err:
            #malformed or (more likely) over the query limit
            logging.error(  "Got code "+err.resp['status']+" for google "
                            +"API access. Please contact the developer of"
                            +" cinefiles.")
            return ''
        
        numresults = int(response['searchInformation']['totalResults'])
        firstresult = response['items'][0]
        self.debuglink = response
        link = firstresult['link']
        if(link.find('/reviews/')<0):
            #best match wasn't a review
            link = ''
        return link
        
    
    def get_link_scrape(self, query):
        #use google search to find, can result in queries being
        #rejected because we aren't using an API
        fquery = parse.urlencode({'q':query+" site:www.rogerebert.com"})
        googlereq = requests.get("https://www.google.com/search?"+fquery)
        print(".", end='', flush=True)
        logging.debug('Fetched '+googlereq.url)

        if(googlereq.status_code == requests.codes.ok):
            tree = html.fromstring(googlereq.content)

#             links = tree.xpath('//cite')
            links = tree.xpath('//div/h3[@class="r"]/a')
            findlink = links[0].attrib['href']
            findlink = findlink.split('?q=')[-1]
            findlink = findlink.split('&')[0]
            self.debugscrape = links
            return findlink
        else:
            return ''