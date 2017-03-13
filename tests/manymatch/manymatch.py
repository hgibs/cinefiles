import logging, os
from imdbparser import IMDb
import tkinter as tk
# from guessit import guessit

class testmany:
  def __init__(self, entry):
    self.configdict = {'skip':False,'guess':False}
    self.imdb = IMDb()
    self.process_movie(entry)

  def process_movie(self,en):
#     title = guessit(en.name)['title']
    title = en.name
    print('"'+title+'" ', end='', flush=True)
    search = self.imdb.search_movie(title)
    search.fetch()
    if(len(search.results)==0):
      #couldn't find a match :(
      print('no match',end='')
    if(len(search.results)==1):
      #we got a direct match!
      print('one match',end='')
    if(len(search.results)>1):
      #uh oh, multiple found
      self.manymatch(en, search.results)
    print()
    
  def tkselect(self):
    self.popup.destroy()
#     print(dir(self.selvar))
    print("matched movie id "+self.selvar.get())
    self.tkcleanup()
    
  def tkskip(self):
    self.popup.destroy()
    print("Skipped!")
    self.tkcleanup()
    
  def tkskipall(self):
    self.popup.destroy()
    print("Skipped and supressing the GUI")
    self.configdict.update({'skip':True})
    self.tkcleanup()
    
  def tkcleanup(self):
    self.popup = None
    self.selvar = None

  def manymatch(self, file, results):
    # global log, skip_flag
  
    print("Multiple matches found ", end='', flush=True)
    
      
    if(self.configdict['skip']):
      print(" skipping this entry.")
      logging.info(file.name+" SKIPPED - too many results")
    elif(self.configdict['guess']):
      print(" making best guess ", end='', flush=True)
      #self.match(en, search.results[0])
      print('self.match(en, search.results[0])')
    else:
      self.popup = tk.Tk()
      #popup.geometry("100x200")
      self.selvar = tk.StringVar()
      label = tk.Label(self.popup, text = ( "More than one movie was found matching the "+ 
                                            "movie title in IMDb, please select the "+
                                            "correct one:"))
      label.pack()
      
      choosebtn = tk.Button(self.popup, text="Select", command=self.tkselect, width='70', bg='white', fg='black')
      skipbtn = tk.Button(self.popup, text="Skip", command=self.tkskip, bg='red', fg='white')
      skipallbtn = tk.Button(self.popup, text="Skip All", command=self.tkskipall, bg='gray', fg='black')
      radiolist = []
    
      first = True
      for movie in results:
#         movie.fetch()
#         radiotxt = movie.title+" ("+str(movie.year)+") "+movie.plot
        radiotxt = movie.title+" ("+str(movie.year)+")"
        radiobtn = tk.Radiobutton(self.popup, text=radiotxt, variable=self.selvar, 
                                  value=movie.imdb_id)
        radiobtn.pack()
        if(first):
          first=False
          radiobtn.select()
        
      choosebtn.pack(fill=tk.Y, side=tk.TOP, expand=1, padx=1, pady=1)
      skipbtn.pack(fill=tk.Y, side=tk.LEFT, expand=1, padx=1, pady=1)
      skipallbtn.pack(fill=tk.Y, side=tk.RIGHT, expand=1, padx=1, pady=1)
      self.popup.pack_propagate(1)
      self.popup.mainloop()
      
      #choosing/skipping is done by button call
      
      

it = os.scandir("/Volumes/Holland Gibson Ext HDD/Movies/testbed2/")
for en in it:
  if(en.name[0] != '.'):
    testmany(en)