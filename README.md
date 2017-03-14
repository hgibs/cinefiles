```diff
- Still under development!
```


cinefiles
=========


[![Travis CI](https://travis-ci.org/hgibs/cinefiles.svg?branch=master)](https://travis-ci.org/hgibs/cinefiles)

[![pypi version](https://img.shields.io/pypi/v/cinefiles.svg)](https://pypi.python.org/pypi/cinefiles)
[![# of downloads](https://img.shields.io/pypi/dm/cinefiles.svg)](https://pypi.python.org/pypi/cinefiles)


Organizes, indexes, and pulls relevant info for your movie library presented in a clean, locally-resourced, set of webpages.

Installation
------------

### 1) Install [PhantomJS]

#### Mac OS X

    brew update
    brew install phantomjs

#### Linux

    sudo apt-get update
    sudo apt-get install phantomjs

### 2) Install cinefiles

    pip install cinefiles

Usage
-----

Downloading to appropriatly named folders (each folder’s name is the name of the movie it holds) NOTE: Folders can contain subfolders with movies in them i.e. =&gt; “James Bond Movies/Goldeneye”

    import cinefiles as cf
    directory = "/Volumes/HDD/Movies"
    search = cf.Cinefiles(searchfolder=directory)
    search.run()

To rename folders automatically: (this can’t be undone automatically yet)

    import cinefiles as cf
    directory = "/Volumes/HDD/jumble_of_movies"
    organize = cf.Cinefolders(searchfolder=directory)
    organize.organizefolder()

What does cinefiles actually do:
--------------------------------

cinefiles updates this folder…

-   Movies/  
    -   Down Periscope/  
        -   movie.mp4

    -   Grand Budapest Hotel (2014)/  
        -   somecrazyunrelatedname.mkv

    -   Mulan (1998)/  
        -   mulan.mp4

    -   Pirate Movies/  
        -   Pirates of the Caribbean At Worlds End/  
            -   worldsend.mov

        -   Pirates of the Caribbean The Curse of the Black Pearl/  
            -   blackpearl.mpv

… to have a structure like this:

-   Movies/  
    -   index.htm
    -   Down Periscope/  
        -   index.htm
        -   movie.mp4

    -   Grand Budapest Hotel (2014)/  
        -   index.htm
        -   somecrazyunrelatedname.mkv

    -   Mulan (1998)/  
        -   index.htm
        -   mulan.mp4

    -   Pirate Movies/  
        -   Pirates of the Caribbean At Worlds End/  
            -   index.htm
            -   worldsend.mov

        -   Pirates of the Caribbean The Curse of the Black Pearl/  
            -   index.htm
            -   blackpearl.mpv

To remove all the added files:
------------------------------

    import cinefiles as cf
    clear_run = cf.Cinefiles(configfile='cinefiles.ini')
    clear_run.clear_run.purgecinefiles()

What does cinefolders actually do: ================================

cinefiles updates this folder…

-   Movies/  
    -   Manchester.by.the.Sea.2016.DVDScr.XVID.AC3.HQ.Hive-CM8.mkv
    -   mulan.mp4
    -   men who stare at goats, the.mp4

… to this!

Movies/  
-   Manchester by the Sea (2016)/  
    -   Manchester.by.the.Sea.2016.DVDScr.XVID.AC3.HQ.Hive-CM8.mkv

-   Mulan (1984)/  
    -   mulan.mp4

-   Men who stare at goats, The/  
    -   the\_men\_who\_stare\_at\_goats.mp4

Which can conveniently then be properly parsed by cinefiles!

  [PhantomJS]: http://phantomjs.org/
