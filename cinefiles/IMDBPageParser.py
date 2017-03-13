####This class is deprecated#####


import html.parser

class IMDBPageParser(html.parser.HTMLParser):
  currenttag = ''
  magicid = 'tn15content' #from IMDB
  foundit = False
  movie_div = ''

  def handle_starttag(self, tag, attrs):
    currenttag = tag
    for attr in attrs:
      if(attr[0]=='id'):
        if(attr[1]==magicid):
          foundit = True
        else:
          foundit = False
      else:
        foundit = False
    
  def handle_endtag(self, tag):
    currenttag = ''
    foundit = False
  
  def handle_data(self, data):
    if(foundit):
      movie_div = "<div>"+data+"</div>"
  
  def getcontent(self):
    return movie_div