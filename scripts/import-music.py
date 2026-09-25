#!/usr/bin/env python3
import argparse,hashlib,json,os,shutil,subprocess,urllib.request
EXT={".mp3",".ogg",".wav",".flac",".m4a",".aac",".opus"}
ap=argparse.ArgumentParser(); ap.add_argument("source"); ap.add_argument("--root",default="/home/codestra/Music/DJONE/Import"); ap.add_argument("--api",default="http://127.0.0.1:8092"); ap.add_argument("--token",default=os.getenv("DJONE_API_TOKEN","")); a=ap.parse_args()
os.makedirs(a.root,exist_ok=True)
sources=[a.source] if os.path.isfile(a.source) else [os.path.join(dp,f) for dp,_,fs in os.walk(a.source) for f in fs]
for src in sources:
 if os.path.splitext(src)[1].lower() not in EXT: continue
 dst=os.path.join(a.root,os.path.basename(src))
 if os.path.realpath(src)!=os.path.realpath(dst) and not os.path.exists(dst): shutil.copy2(src,dst)
 api_path="/music/Import/"+os.path.basename(dst)
 body=json.dumps({"path":api_path,"source":"local-import","provenance":"user-owned-or-authorized-download"}).encode()
 req=urllib.request.Request(a.api+"/v1/library/tracks",data=body,headers={"Content-Type":"application/json","Authorization":"Bearer "+a.token},method="POST")
 try: print(json.loads(urllib.request.urlopen(req).read()))
 except Exception as e: print(src,"ERROR",e)
