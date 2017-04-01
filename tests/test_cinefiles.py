import pytest, os, shutil

import glob
from pprint import pprint
from lxml import html

import cinefiles.cinefiles as cf

def test_import():
    import cinefiles

movies = [  '5th Element','Amour','Astronaut Farmer',
            'Down Periscope','Grand Budapest Hotel, The (2014)',
            'Interstellar (2014)','Invisible War, The',
            'Men Who Stare at Goats, The','Mulan (1998)',
            'Soylent Green (1973)','Thin Red Line']

@pytest.fixture(scope='module')
def directoryA(tmpdir_factory):
    testbed = tmpdir_factory.mktemp('testA')
    for m in movies:
        tempmovie = testbed.mkdir('/'+m).join('/movie.mp4')
        tempmovie.write('movie code')
    return testbed

def test_directoryA(directoryA):
    assert os.path.exists(str(directoryA)+'/Thin Red Line/movie.mp4')
    
@pytest.fixture(scope='module')
def examples(tmpdir_factory):
    safe_examples = tmpdir_factory.mktemp('safe_examples')
    shutil.copytree('examples',str(safe_examples)+'/examples')
    return safe_examples.join('examples')
    
def test_safe_examples_dir(examples):
    assert os.path.exists(str(examples)+'/run_cf.py')

@pytest.mark.skipif(os.environ['LOGNAME'] == 'holland',
                    reason="Don't run on home computer")
def test_examplerunA(directoryA, examples, monkeypatch):
    monkeypatch.chdir(examples)
    
    import cinefiles.cinefiles as cf
    import logging
    search = cf.Cinefiles(configfile=str(examples)+'/cinefiles.ini')
    #we must change searchfolder to temporary directory
    search.configdict.update({'searchfolder':str(directoryA)})
    search.run()
    #check basic structure
    for item in directoryA.listdir():
        if(item.isdir()):
            foldername = str(item).split('/')[-1]
            print(foldername)
            if(foldername != 'cinefiles' and foldername != '.cinefiles'):
                index = item.join('/index.htm')
                assert index.exists()
                
@pytest.fixture(scope='session')
def dirA_complete(tmpdir_factory):
    testbed = tmpdir_factory.mktemp('testA_complete')
    for m in movies:
        tempmovie = testbed.mkdir('/'+m).join('/movie.mp4')
        tempmovie.write('movie code')
    search = cf.Cinefiles(searchfolder=str(testbed))
    search.run()
    return testbed
    
@pytest.mark.skipif(os.environ['LOGNAME'] == 'holland',
                    reason="Don't run on home computer")
def test_checkarchive(dirA_complete, monkeypatch):
    monkeypatch.chdir(dirA_complete)
    assert dirA_complete.join('/5th Element/index.htm').exists()
    newsearch = cf.Cinefiles(searchfolder=str(dirA_complete))
#     newsearch.run()
    it = os.scandir(str(dirA_complete))
    for entry in it:
        if entry.is_dir():
            subit = os.scandir(entry.path)
            for subentry in subit:
                if(subentry.name == 'archive.log' or subentry.name == '.archive.log'):
                    assert newsearch.checkarchive(subentry)

#all of these movies have all 3 reviews
moviesB = [ '5th Element','Grand Budapest Hotel, The (2014)',
            'Interstellar (2014)','Thin Red Line']                    

@pytest.fixture(scope='session')
def directoryB(tmpdir_factory):
    testbed = tmpdir_factory.mktemp('testB')
    for m in moviesB:
        tempmovie = testbed.mkdir('/'+m).join('/movie.mp4')
        tempmovie.write('movie code')
    search = cf.Cinefiles(searchfolder=str(testbed))
    search.run()
    return testbed

@pytest.mark.skipif(os.environ['LOGNAME'] == 'holland',
                    reason="Don't run on home computer")
def test_metadata(directoryB):
    newsearch = cf.Cinefiles(searchfolder=str(directoryB))
    for m in moviesB:
        pathobj = directoryB.join('/'+m)
        resultdict = newsearch.getattrfrommetadata(str(pathobj))
        print(str(pathobj))
        for key in resultdict:
            if(key != 'indexfile'):
                #indexfile is set later
                print(key)
                assert resultdict[key] != ''

@pytest.mark.skipif(os.environ['LOGNAME'] == 'holland',
                    reason="Don't run on home computer")            
def test_masterindex_imdb(directoryB):
    masterindex = directoryB.join('/index.htm')
    htmlstring = ''
    for line in masterindex.readlines():
        htmlstring += line
    tree = html.fromstring(htmlstring)
    results = tree.xpath('//td[@class="rowimdb"]')
    for r in results:
        assert r.text_content != ''
    
@pytest.mark.skipif(os.environ['LOGNAME'] == 'holland',
                    reason="Don't run on home computer")            
def test_masterindex_meta(directoryB):
    masterindex = directoryB.join('/index.htm')
    htmlstring = ''
    for line in masterindex.readlines():
        htmlstring += line
    tree = html.fromstring(htmlstring)
    results = tree.xpath('//td[@class="rowmeta"]')
    for r in results:
        assert r.text_content != ''
    
@pytest.mark.skipif(os.environ['LOGNAME'] == 'holland',
                    reason="Don't run on home computer")            
def test_masterindex_meta(directoryB):
    masterindex = directoryB.join('/index.htm')
    htmlstring = ''
    for line in masterindex.readlines():
        htmlstring += line
    tree = html.fromstring(htmlstring)
    results = tree.xpath('//td[@class="rowroger"]')
    for r in results:
        assert r.text_content != ''
    
@pytest.fixture(scope='function')
def min_ini(tmpdir_factory):
    minimal = tmpdir_factory.mktemp('minimal')
    config = minimal.join('/cinefiles.ini')
    config.write('[cinefiles]\n searchfolder=none\n')
    return minimal
    
def test_no_args(min_ini,monkeypatch):
    monkeypatch.chdir(min_ini)
    tc = cf.Cinefiles()
    assert tc.configdict['searchfolder'] == 'none'

@pytest.fixture(scope='function')   
def blank_folder(tmpdir_factory):
    return tmpdir_factory.mktemp('blank')
    
def test_no_conf(blank_folder,monkeypatch):
    monkeypatch.chdir(blank_folder)
    with pytest.raises(IOError) as err:
        tc = cf.Cinefiles()
    
@pytest.fixture(scope='function')
def broken_ini(tmpdir_factory):
    broken = tmpdir_factory.mktemp('minimal')
    config = broken.join('/cinefiles.ini')
    config.write('\n')
    return broken
    
def test_broken_conf(broken_ini,monkeypatch):
    monkeypatch.chdir(broken_ini)
    with pytest.raises(ValueError) as err:
        tc = cf.Cinefiles()
    
def test_onwindows():
    assert not cf.running_on_windows()
    
def test_main(script_runner):
    ret = script_runner.run('./cinefiles')

def recurseprint(directoryobj,tabnum=0):
    for item in directoryobj.listdir():
        print('\t'*tabnum+item.basename, end='')
        if(item.isdir()):
            print('/')
            recurseprint(item,tabnum+1)
        else:
            print('')