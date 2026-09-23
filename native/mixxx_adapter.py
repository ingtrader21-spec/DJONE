#!/usr/bin/env python3
"""DJONE native Mixxx adapter.

Uses ALSA sequencer MIDI as the supported native control transport. It exposes
only an allowlisted JSON protocol on loopback. Readback is based on MIDI output
feedback emitted by the Mixxx mapping; commands are not certified until matching
feedback is observed.
"""
import json, os, socketserver, subprocess, threading, time

HOST="127.0.0.1"; PORT=int(os.getenv("DJONE_NATIVE_PORT","18091"))
TOKEN=os.getenv("DJONE_NATIVE_TOKEN","")
ALLOWED={"play","pause","sync","stop"}
state={f"deck{i}":{"play":None,"sync":None,"observed_at":None} for i in range(1,5)}
lock=threading.Lock()

def midi_dest():
    out=subprocess.check_output(["aconnect","-l"],text=True)
    # Mapping expects a dedicated virtual/controller endpoint. Never guess one.
    for line in out.splitlines():
        if "DJONE-Mixxx" in line:
            return line.split(":")[0].split()[-1]+":0"
    return None

class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        raw=self.rfile.readline(65536)
        try:
            req=json.loads(raw)
            if not TOKEN or req.get("token")!=TOKEN: return self.reply({"ok":False,"error":"unauthorized"})
            if req.get("op")=="state": return self.reply({"ok":True,"state":state,"transport_ready":bool(midi_dest())})
            if req.get("op")!="command" or req.get("action") not in ALLOWED: return self.reply({"ok":False,"error":"unsupported"})
            deck=int(req.get("deck",0))
            if deck not in range(1,5): return self.reply({"ok":False,"error":"invalid_deck"})
            dest=midi_dest()
            if not dest: return self.reply({"ok":False,"executed":False,"error":"mixxx_mapping_not_connected"})
            # Actual MIDI notes are intentionally supplied by the certified mapping.
            return self.reply({"ok":False,"executed":False,"error":"mapping_not_certified","deck":deck,"action":req["action"]})
        except Exception as e: self.reply({"ok":False,"error":type(e).__name__})
    def reply(self,obj): self.wfile.write((json.dumps(obj)+"\n").encode())

if __name__=="__main__":
    with socketserver.ThreadingTCPServer((HOST,PORT),Handler) as s: s.serve_forever()
