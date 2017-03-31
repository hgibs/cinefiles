import sys
import getopt

from cinefiles import cinefiles as cf

def main_cfiles(args=None):
    if args is None:
        args = sys.argv[1:]

    cinefilesHandler(args)
    
def cinefilesHandler(argv):
    import logging

    # defaultFolder = "/Volumes/Holland Gibson Ext HDD/Movies/Movies"
    defaultFolder = "~/Movies/"

    help_string = ( "cinefiles -f <folder to improve> [options]  \n"
                  "-h\t\tPrint this help menu\n-f <folder>\tWhich folder to search\n"
                  "-d\t\tDefault folder: "+defaultFolder+'\n'
                  "-t\t\tTest, don't download or modify anything just search TMDb\n"
                  "-g\t\tNon-interactive, make best guess and carry on\n"
                  "-s\t\tSkip questionable movies (don't guess either)\n"
                  "--force\t\tRe-download all files (but save old ones)\n"
                  "--force-destroy\tRe-download all files and DELETE old ones "
                  "(this overrides '--force')\n"
                  "\nNote: this only works when movies are in their own folders. "
                  "\nYou can run 'cinefolders' to do that for you.\n" )

    try:
        opts, args = getopt.getopt(argv,"hdf:tgs",["force", "force-destroy", "debug:"])
    except getopt.GetoptError:
        print(help_string)
        sys.exit(2)
  
    searchfolder = ''
    guess_flag=False
    skip_flag=False
    test_flag=False
    force_flag=False
    destroy_flag=False
    log=logging.INFO

    flags = ""

    for opt, arg in opts:
        if opt == '-h':
            print(help_string)
            sys.exit(2)
        elif opt == '-f':
            searchfolder = arg
            flags += " -f "+arg
        elif opt == '-t':
            test_flag = True
            flags += " -t"
        elif opt == '-s':
            skip_flag = True
            flags += " -s"
        elif opt == '-g':
            guess_flag = True
            flags += " -g"
        elif opt == '-d':
            searchfolder = defaultFolder
            flags += " -f "+defaultFolder
        elif opt == "force":
            force_flag = True
            flags += " --force"
        elif opt == "force-destroy":
            force_flag = True
            destroy_flag = True
            flags += " --force-destroy"
        elif opt == "debug":
            debug_num = int(arg)
            flags += " --debug "+arg
    
    if(searchfolder == ''):
        print("You must specify a folder! (-f <folder>) or (-d)\n-h for help")
        sys.exit(2)

    if(log > 0):
        print("Running with:" +flags)

    print('Search folder is: '+searchfolder)
    if(test_flag):
        print("TEST mode")
        force_flag = False
        destroy_flag = False
    if(skip_flag):
        print("Skipping questionable movies")
    if(not skip_flag and not guess_flag):
        print("DON'T QUESTION MY AUTHORITY!!")
    if(force_flag and not destroy_flag):
        print("Let's get new files this time, but I'm attached to the old ones")
    if(force_flag and destroy_flag):
        print("DELETE those old files, let's get new ones")

    print("")

    search = cf.Cinefiles(searchfolder, guess_flag, skip_flag, test_flag, 
                  force_flag, destroy_flag, log)
      
    search.run()
    
def main_cfolders(args=None):
    if args is None:
        args = sys.argv[1:]

    cinefoldersHandler(args)

def cinefoldersHandler(argv):
    import logging

    # defaultFolder = "/Volumes/Holland Gibson Ext HDD/Movies/Movies"
    defaultFolder = "~/Movies/"

    help_string = ( "cinefolders -f <folder to improve> [options]  \n"
                  "-h\t\tPrint this help menu\n-f <folder>\tWhich folder to organize\n"
                  "-c\t\tCopy files instead of moving them\n"
                  "-s <folder>\tSpecify different source folder to move files from\n" )

    try:
        opts, args = getopt.getopt(argv,"hdf:tgs",["force", "force-destroy", "debug:"])
    except getopt.GetoptError:
        print(help_string)
        sys.exit(2)
  
    searchfolder = ''
    guess_flag=False
    skip_flag=False
    test_flag=False
    force_flag=False
    destroy_flag=False
    log=logging.INFO

    flags = ""

    for opt, arg in opts:
        if opt == '-h':
            print(help_string)
            sys.exit(2)
        elif opt == '-f':
            searchfolder = arg
            flags += " -f "+arg
        elif opt == '-t':
            test_flag = True
            flags += " -t"
        elif opt == '-s':
            skip_flag = True
            flags += " -s"
        elif opt == '-g':
            guess_flag = True
            flags += " -g"
        elif opt == '-d':
            searchfolder = defaultFolder
            flags += " -f "+defaultFolder
        elif opt == "force":
            force_flag = True
            flags += " --force"
        elif opt == "force-destroy":
            force_flag = True
            destroy_flag = True
            flags += " --force-destroy"
        elif opt == "debug":
            debug_num = int(arg)
            flags += " --debug "+arg
    
    if(searchfolder == ''):
        print("You must specify a folder! (-f <folder>) or (-d)\n-h for help")
        sys.exit(2)

    if(log > 0):
        print("Running with:" +flags)

    print('Search folder is: '+searchfolder)
    if(test_flag):
        print("TEST mode")
        force_flag = False
        destroy_flag = False
    if(skip_flag):
        print("Skipping questionable movies")
    if(not skip_flag and not guess_flag):
        print("DON'T QUESTION MY AUTHORITY!!")
    if(force_flag and not destroy_flag):
        print("Let's get new files this time, but I'm attached to the old ones")
    if(force_flag and destroy_flag):
        print("DELETE those old files, let's get new ones")

    print("")

    search = imf.ImproveMoviesFolder(searchfolder, guess_flag, skip_flag, test_flag, 
                  force_flag, destroy_flag, log)
      
    clear_run.purgecinefiles()

if __name__ == "__main__":
    main_cfolders()