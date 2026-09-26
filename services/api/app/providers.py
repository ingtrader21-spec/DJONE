import os,json,base64,urllib.parse,urllib.request,time
_cache={"token":None,"expires":0}
def status():
 return {"spotify":bool(os.getenv("SPOTIFY_CLIENT_ID") and os.getenv("SPOTIFY_CLIENT_SECRET")),"youtube_music":bool(os.getenv("YOUTUBE_API_KEY"))}
def spotify_token():
 if _cache["token"] and _cache["expires"]>time.time()+30:return _cache["token"]
 cid=os.getenv("SPOTIFY_CLIENT_ID"); sec=os.getenv("SPOTIFY_CLIENT_SECRET")
 if not cid or not sec: raise RuntimeError("spotify credentials not configured")
 body=urllib.parse.urlencode({"grant_type":"client_credentials"}).encode()
 auth=base64.b64encode((cid+":"+sec).encode()).decode()
 req=urllib.request.Request("https://accounts.spotify.com/api/token",data=body,headers={"Authorization":"Basic "+auth,"Content-Type":"application/x-www-form-urlencoded"})
 d=json.loads(urllib.request.urlopen(req,timeout=8).read()); _cache.update(token=d["access_token"],expires=time.time()+int(d["expires_in"])); return d["access_token"]
def spotify_search(q,limit):
 u="https://api.spotify.com/v1/search?"+urllib.parse.urlencode({"q":q,"type":"track","limit":limit})
 req=urllib.request.Request(u,headers={"Authorization":"Bearer "+spotify_token()}); d=json.loads(urllib.request.urlopen(req,timeout=8).read())
 return [{"kind":"streaming","provider":"spotify","external_id":x["id"],"title":x["name"],"artist":", ".join(a["name"] for a in x["artists"]),"album":x["album"]["name"],"url":x["external_urls"]["spotify"],"artwork_url":x["album"]["images"][0]["url"] if x["album"]["images"] else None,"downloadable":False} for x in d["tracks"]["items"]]
def youtube_search(q,limit):
 key=os.getenv("YOUTUBE_API_KEY")
 if not key: raise RuntimeError("youtube api key not configured")
 u="https://www.googleapis.com/youtube/v3/search?"+urllib.parse.urlencode({"part":"snippet","q":q,"type":"video","videoCategoryId":"10","maxResults":limit,"key":key})
 d=json.loads(urllib.request.urlopen(u,timeout=8).read())
 return [{"kind":"streaming","provider":"youtube_music","external_id":x["id"]["videoId"],"title":x["snippet"]["title"],"artist":x["snippet"]["channelTitle"],"album":None,"url":"https://music.youtube.com/watch?v="+x["id"]["videoId"],"artwork_url":x["snippet"]["thumbnails"]["high"]["url"],"downloadable":False} for x in d["items"]]
