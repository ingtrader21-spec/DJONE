from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import socket,time,re,urllib.request,urllib.error,os

router=APIRouter(prefix="/v1/outputs",tags=["outputs"])
STREAM=os.getenv("SAMSUNG_STREAM_URL","http://10.0.0.73:18093/mix.mp3")

def discover():
    msg=('M-SEARCH * HTTP/1.1\r\nHOST:239.255.255.250:1900\r\nMAN:"ssdp:discover"\r\nMX:2\r\nST:urn:schemas-upnp-org:device:MediaRenderer:1\r\n\r\n').encode()
    s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM,socket.IPPROTO_UDP); s.settimeout(.3); s.sendto(msg,("239.255.255.250",1900))
    end=time.time()+2
    while time.time()<end:
        try:
            data,_=s.recvfrom(65535); m=re.search(r"(?im)^LOCATION:\s*(\S+)",data.decode(errors="ignore"))
            if not m: continue
            loc=m.group(1); desc=urllib.request.urlopen(loc,timeout=1).read().decode(errors="ignore")
            if "Samsung" in desc and "MediaRenderer" in desc:
                n=re.search(r"<friendlyName>(.*?)</friendlyName>",desc,re.S)
                return {"name":n.group(1) if n else "Samsung MediaRenderer","location":loc}
        except Exception: pass
    return None

def soap(loc,action,args):
    url=loc.rsplit("/",1)[0]+"/upnp/control/AVTransport1"
    body=('<?xml version="1.0"?><s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><u:'+action+' xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">'+args+'</u:'+action+'></s:Body></s:Envelope>').encode()
    req=urllib.request.Request(url,data=body,headers={"Content-Type":"text/xml","SOAPACTION":'"urn:schemas-upnp-org:service:AVTransport:1#'+action+'"'})
    return urllib.request.urlopen(req,timeout=3).read().decode()

@router.get("")
def outputs():
    d=discover()
    return {"items":[] if not d else [{"id":"samsung-dlna","type":"dlna","name":d["name"],"available":True}],"stream_url":STREAM}

@router.post("/samsung/connect")
def connect():
    d=discover()
    if not d: raise HTTPException(503,"Samsung MediaRenderer not found")
    soap(d["location"],"SetAVTransportURI","<InstanceID>0</InstanceID><CurrentURI>"+STREAM+"</CurrentURI><CurrentURIMetaData></CurrentURIMetaData>")
    soap(d["location"],"Play","<InstanceID>0</InstanceID><Speed>1</Speed>")
    return {"connected":True,"output":"samsung-dlna","name":d["name"],"stream_url":STREAM}

@router.post("/samsung/stop")
def stop():
    d=discover()
    if not d: raise HTTPException(503,"Samsung MediaRenderer not found")
    soap(d["location"],"Stop","<InstanceID>0</InstanceID>")
    return {"connected":False,"output":"samsung-dlna"}
