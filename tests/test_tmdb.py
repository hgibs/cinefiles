from cinefiles.tmdb import TMDb
from cinefiles.tmdb import exceptions
import pytest

TMDB_API_KEY = 'beb6b398540ccc4245a5b4739186a0bb'

def test_init_minimal():
    t = TMDb(TMDB_API_KEY)
    assert t.lang == 'en'
    assert t.region == 'US'
    
def test_safeapi():
    t = TMDb(TMDB_API_KEY)
    resp = t.safeapi('https://api.themoviedb.org/3/configuration?'
                    +'api_key='+TMDB_API_KEY)
                    
def test_safeapi_badkey():
    t = TMDb(TMDB_API_KEY)
    with pytest.raises(exceptions.APIKeyException):
        resp = t.safeapi('https://api.themoviedb.org/3/configuration?'
                    +'api_key=asdfsdf')
    
def test_bad_api():
    with pytest.raises(exceptions.APIKeyException):
        badkey = TMDb('FFFFFFFFFFFFFFFFFFFFFFF')
    
def test_init_configs():
    t = TMDb(TMDB_API_KEY, 'en', 'us')
    