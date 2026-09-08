# -*- coding: utf-8 -*-
"""
Microservizio HTTP leggero per sintesi vocale neurale Microsoft Edge TTS.
Fornisce audio MP3 ad altissima fedeltà per i conduttori DarIA (it-IT-ElsaNeural) e DarIO (it-IT-DiegoNeural).
Include cache locale per azzerare la latenza e header CORS completi.
— Immobiliare Giancani
"""
import os, sys, hashlib, asyncio, urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import edge_tts

CACHE_DIR = "/tmp/edge_tts_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

class TTSHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b"OK")
            return

        if parsed.path == '/tts':
            params = urllib.parse.parse_qs(parsed.query)
            text = params.get('text', [''])[0].strip()
            voice = params.get('voice', ['it-IT-ElsaNeural'])[0].strip()

            if not text:
                self.send_response(400)
                self.end_headers()
                return

            h = hashlib.md5(f"{voice}_{text}".encode('utf-8')).hexdigest()
            cache_file = os.path.join(CACHE_DIR, f"{h}.mp3")

            if not os.path.exists(cache_file) or os.path.getsize(cache_file) == 0:
                try:
                    async def synthesize():
                        c = edge_tts.Communicate(text, voice)
                        await c.save(cache_file)
                    asyncio.run(synthesize())
                except Exception as e:
                    print(f"[TTS-SERVER] Errore sintesi per '{text[:30]}': {e}", file=sys.stderr)
                    self.send_response(500)
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    return

            try:
                with open(cache_file, 'rb') as f:
                    data = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'audio/mpeg')
                self.send_header('Content-Length', str(len(data)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cache-Control', 'public, max-age=86400')
                self.end_headers()
                self.wfile.write(data)
            except Exception as e:
                self.send_response(500)
                self.end_headers()
            return

        self.send_response(404)
        self.end_headers()

if __name__ == "__main__":
    port = 5050
    server = ThreadingHTTPServer(('0.0.0.0', port), TTSHandler)
    print(f"[OK] Microservizio Edge TTS avviato su http://127.0.0.1:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
