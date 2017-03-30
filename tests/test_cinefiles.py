import pytest, os, shutil

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

    truthcheck = True

    #check basic structure
    for item in directoryA.listdir():
        if(item.isdir()):
            if(not item.basename.startswith('cinefiles') or 
                        not item.basename.startswith('.cinefiles')):
                truthcheck = truthcheck and item.join('index.htm').exists()
    assert truthcheck