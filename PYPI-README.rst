
============
cinefiles
============

.. image:: https://travis-ci.org/hgibs/cinefiles.svg?branch=master

Organizes, indexes, and pulls relevant info for your movie library presented in a clean, locally-resourced, set of webpages.

Installation
===============

1) Install `PhantomJS <http://phantomjs.org/>`_
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Mac OS X
--------

::

    brew update
    brew install phantomjs
    
    
Linux
-----

::

    sudo apt-get update
    sudo apt-get install phantomjs

2) Install cinefiles
^^^^^^^^^^^^^^^^^^^^

::

    pip install cinefiles
    

Usage
=====

Downloading to appropriaatly named folders (each folder's name is the name of the movie it holds)
NOTE: Folders can contain subfolders with movies in them i.e. => "James Bond Movies/Goldeneye"

::

    import cinefiles as cf
    directory = "/Volumes/HDD/Movies"
    search = cf.Cinefiles(searchfolder=directory)
    search.run()


To rename folders automatically:
(this can't be undone automatically yet)

::

    import cinefiles as cf
    directory = "/Volumes/HDD/jumble_of_movies"
    organize = cf.Cinefolders(searchfolder=directory)
    organize.organizefolder()
    


To remove all the added files:
==============================

::

    import cinefiles as cf
    clear_run = cf.Cinefiles(configfile='cinefiles.ini')
    clear_run.clear_run.purgecinefiles()
    
    