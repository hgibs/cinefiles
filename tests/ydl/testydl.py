import youtube_dl, os, logging

trailerfile = ""

def ydlhook(d):
		#only for filedownloader - youtube-dl constraint
		if(d['status'] == 'finished'):
			print(".", end='', flush=True)
		trailerfile = d['filename']
		
folderpath = os.getcwd()

ydl_opts = {
			'quiet'					:True,
			'ignoreerrors'	:True,
			'format'				:'best[ext=mp4]',
			'nooverwrites'	:False,
			###'logger'				 :ydlhs.loghandler(),
			'writethumbnail':'thumb.jpg',
			'skip_download' :False,
			'progress_hooks':[ydlhook],
			'writeinfojson' :True,
			'download_archive':folderpath+'/ydlarchive'
		}
		
		
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
			ydl.download(['eNxMkZcySKs'])
			
print("Done")