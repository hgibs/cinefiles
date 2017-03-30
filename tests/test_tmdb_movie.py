from cinefiles.tmdb import TMDb, Movie
from cinefiles.tmdb import exceptions
import pytest

TMDB_API_KEY = 'beb6b398540ccc4245a5b4739186a0bb'

@pytest.fixture(scope='module')
def defaultTMDb():
    return TMDb(TMDB_API_KEY,'en','US')
    
@pytest.fixture(scope='module')
def casablanca(defaultTMDb):
    basedict = {'id':'289'}
    return Movie(basedict,defaultTMDb)
    
@pytest.fixture(scope='module')
def inception(defaultTMDb):
    basedict = {'id':'27205'}
    out_movie = Movie(basedict,defaultTMDb)
    out_movie.fetchinfo()
    return out_movie
    
@pytest.fixture(scope='function')
def basicmovie(defaultTMDb):
    basedict = {'id':'1444'}
    return Movie(basedict,defaultTMDb)
    
def test_init_id(basicmovie):
    assert basicmovie.id == '1444'


basickeys = ['production_companies', 'original_title', 'videos', 
            'budget', 'runtime', 'backdrop_path', 'homepage', 'id', 
            'release_date', 'adult', 'genres', 'tagline', 'video', 
            'poster_path', 'title', 'popularity', 
            'production_countries', 'spoken_languages', 'imdb_id', 
            'images', 'revenue', 'vote_average', 'overview', 
            'vote_count', 'status', 'belongs_to_collection',
            'original_language','original_title']
            
@pytest.mark.parametrize('key',basickeys)
def test_init_keys(basicmovie, key):
    assert key in basicmovie.attributes
    
def test_fetch(casablanca, basicmovie):
    casablanca.fetchinfo()
    assert casablanca.fetched
    
    
minkeys = ['budget','id','imdb_id','title','genres','tagline','release_date']
            
@pytest.mark.parametrize('key',minkeys)
def test_fetch_results(casablanca, basicmovie, key):
    assert casablanca.attributes[key] != basicmovie.attributes[key]

def test_firsttrailer(inception):
    assert inception.firsttrailer().find('youtube.com/watch?v') > 0