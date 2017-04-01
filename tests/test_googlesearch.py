import pytest

import cinefiles.googlesearch as gs

@pytest.fixture(scope='function')
def gs_obj():
    return gs.GoogleSearch()

def test_nointernet(gs_obj,disable_socket):
    assert gs_obj.try_ALL_API('Some old movie...') == ''
    
def test_rogerAPI(gs_obj):
    gs_obj.get_link = gs_obj.use_roger_API
    assert gs_obj.get_link('Inception').find('reviews') > 0
    
def test_get_link_API(gs_obj):
    gs_obj.get_link = gs_obj.get_link_API
    assert gs_obj.get_link('Inception').find('reviews') > 0
    
#this may or may not work on travis-ci
def test_get_link_scrape(gs_obj):
    gs_obj.get_link = gs_obj.get_link_scrape
    assert gs_obj.get_link('Inception').find('reviews') > 0
    
