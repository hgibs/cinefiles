
============
cinefiles
============

.. image:: https://travis-ci.org/hgibs/cinefiles.svg?branch=master   :target: https://travis-ci.org/hgibs/cinefiles

.. image:: https://img.shields.io/codecov/c/github/hgibs/cinefiles/master.svg   :target: https://codecov.io/gh/hgibs/cinefiles/

Organizes, indexes, and pulls relevant info for your movie library presented in a clean, locally-resourced, set of webpages.

Installation
===============

1) Install `cinefiles`_
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    pip install cinefiles
    

Usage
=====

Downloading to appropriaatly named folders (each folder's name is the name of the movie it holds)
NOTE: Folders can contain subfolders with movies in them i.e. => "James Bond Movies/Goldeneye"

::

    import cinefiles.cinefiles as cf
    directory = "/Volumes/HDD/Movies"
    search = cf.Cinefiles(searchfolder=directory)
    search.run()


To rename folders automatically:
(this can't be undone automatically yet)

::

    import cinefiles.cinefiles as cf
    directory = "/Volumes/HDD/jumble_of_movies"
    organize = cf.Cinefolders(searchfolder=directory)
    organize.organizefolder()
    


To remove all the added files:
==============================

::

    import cinefiles.cinefiles as cf
    clear_run = cf.Cinefiles(configfile='cinefiles.ini')
    clear_run.clear_run.purgecinefiles()
    
    
