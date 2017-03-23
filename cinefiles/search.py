from urllib import parse
from lxml import html
# import requests
# import json
import logging

class Search:
    def __init__(self, title):
        self.title = title
    
    def getrogerebertlink(self):
        usegoogle = False
        
        if(usegoogle):
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
        else:
            #use phantomjs driver - slower (much slower)
            
            self.title.driver.set_window_size(1024, 768) #optional
            #http://www.rogerebert.com/search?q=pride+and+prejudice+and+zombies
            baselink = 'http://www.rogerebert.com/search?'
            querystr = parse.urlencode({'q':self.ftitle})
            self.title.driver.get(baselink+querystr)
            print(".", end='', flush=True)
            logging.debug('Fetched with driver '+baselink+querystr)
        
            tree = html.fromstring(self.title.driver.page_source)
            linklist = tree.xpath('//div[@class="gsc-url-bottom"]')
            link = linklist[0].text_content().strip().split('reviews/')[-1]
            
            return 'http://www.rogerebert.com/reviews/'+link
        