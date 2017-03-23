from apiclient.discovery import build
from apiclient.errors import HttpError
import json

class GoogleSearch:
    # Here's my free API, please don't steal it. You're only stealing the
    # free API key anyway. Which is, you know, free to make yourself.
    GOOGLE_FREE_API_KEY = 'AIzaSyBLkr83ZK5OoGAUx0O4sizJc9UuKHRmTeA'
    ROGEREBERT_SEARCH_ENGINE_ID = '011435517851099762049:tg32kab0kxe'
    

    def __init__(self):
        # The build function creates a service object. It takes an API name and API
        # version as arguments.
        #note: this can take a few seconds to build
        service = build('customsearch', 'v1', developerKey=GOOGLE_FREE_API_KEY)

        # A collection is a set of resources. We know this one is called "cse"
        # because the CustomSearch API page tells us cse "Returns the cse Resource".
        self.collection = service.cse()
        self.get_link = get_link_API
        self.cxselect = ROGEREBERT_SEARCH_ENGINE_ID
        

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
                            +" cinefiles."
                            )
            self.get_link = get_link_scrape
            return self.get_link_scrape(query)
        
        numresults = int(response['searchInformation']['totalResults'])
        firstresult = response['items'][0]
        link = firstresult['link']
        if(link.find('/reviews/'<0)
            #best match wasn't a review
            link = ''
        return link
        
    
    def get_link_scrape(self, query):
        #use google search to find, can result in queries being
        #rejected because we aren't using the API
        query = parse.urlencode({'q':self.ftitle+" site:www.rogerebert.com"})
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
            return findlink
        else:
            return ''