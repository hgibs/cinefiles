from cinefiles.tmdb import TMDb
from cinefiles.tmdb import exceptions
import pytest
from time import time
import threading

TMDB_API_KEY = 'beb6b398540ccc4245a5b4739186a0bb'

@pytest.fixture(scope='module')
def defaultTMDb():
    return TMDb(TMDB_API_KEY,'en','US')
    
def test_init_config_imgbase(defaultTMDb):
    assert 'imgbase' in defaultTMDb.__dict__
    assert defaultTMDb.imgbase != ''
    
def test_init_config_imgsize(defaultTMDb):
    assert 'imgsize' in defaultTMDb.__dict__
    assert defaultTMDb.imgsize == 'original'
    
def test_init_config_available_poster_sizes(defaultTMDb):
    assert 'available_poster_sizes' in defaultTMDb.__dict__
    assert defaultTMDb.available_poster_sizes != []
    
def test_init_config_available_backdrop_sizes(defaultTMDb):
    assert 'available_backdrop_sizes' in defaultTMDb.__dict__
    assert defaultTMDb.available_backdrop_sizes != []

def test_safeapi_overall(defaultTMDb):
    resp = defaultTMDb.safeapi('https://api.themoviedb.org/3/configuration?'
                    +'api_key='+TMDB_API_KEY)
                
def test_safeapi_badkey(defaultTMDb):
    with pytest.raises(exceptions.APIKeyException):
        resp = defaultTMDb.safeapi('https://api.themoviedb.org/3/configuration?'
                    +'api_key=asdfsdf')
  
class APIThread (threading.Thread):
    def __init__(self, tmdbobj):
        threading.Thread.__init__(self)
        self.tmdbobj = tmdbobj
    
    def run(self):
        self.tmdbobj.safeapi('https://api.themoviedb.org/3/configuration?'
                            +'api_key='+TMDB_API_KEY)

def test_safeapi_timing(defaultTMDb):
    defaultTMDb.safeapi('https://api.themoviedb.org/3/configuration?'
                            +'api_key='+TMDB_API_KEY)
          
    mainstart = defaultTMDb.safetime
    
    #get closer to maxing out the 40 requests per 10 seconds
    threads = []
    for r in range(38):
        apithread = APIThread(defaultTMDb)
        apithread.start()
        threads.append(apithread)
    
    times = []
    
    for a in range(5):
        #first one should get the new timing and auto-block
        thisstart = time()
        defaultTMDb.safeapi('https://api.themoviedb.org/3/configuration?'
                            +'api_key='+TMDB_API_KEY)
        times.append(thisstart)
        
    lateststarttime = 0.0
    for starttime in times:
        if starttime > lateststarttime:
            lateststarttime = starttime
            
    #wait for all threads to close
    for api in threads:
        api.join()
        
    #one of the threads should block until the 10 second window has reopened
    assert lateststarttime > mainstart+10.0
    
def test_bad_api():
    with pytest.raises(exceptions.APIKeyException):
        badkey = TMDb('FFFFFFFFFFFFFFFFFFFFFFF')
        
def test_init_minimal():
    t = TMDb(TMDB_API_KEY)
    assert t.lang == 'en'
    assert t.region == 'US'
    
                  #title            year    id
testsearches = [('Casablanca',      1942,   289),
                ('Citizen Kane',    1941,   15),
                ('Gates of Heaven', 1978,   24998),
                ('Inception',       2010,   27205),
                ('Schindlers List', 1993,   424)]
                
@pytest.mark.parametrize("title,year,id",testsearches)
def test_search(defaultTMDb, title, year, id):
    results = defaultTMDb.search(title,year)
    assert int(results[0].id) == id