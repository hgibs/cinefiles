import pytest, os, shutil

import glob
from pprint import pprint

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
                
#     recurseprint(directoryA)
    assert truthcheck
    
@pytest.mark.skipif(os.environ['LOGNAME'] == 'holland',
                    reason="Don't run on home computer")
def test_checkarchive(examples, monkeypatch):
    monkeypatch.chdir(examples)
    assert examples.join('/5th Element/index.htm').exists()
    
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
    
#codecov ignore start
def recurseprint(directoryobj,tabnum=0):
    for item in directoryobj.listdir():
        print('\t'*tabnum+item.basename, end='')
        if(item.isdir()):
            print('/')
            recurseprint(item,tabnum+1)
        else:
            print('')
#codecov ignore end