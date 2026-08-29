import os, sys, time, json

def extract_tiktok_live():
    print("🎵 [TikTok Bot] Avvio modulo estrazione automatica TikTok Live per GitHub Runner...")
    
    # Check if manual key provided in env
    manual_key = os.environ.get('TK_KEY', '').strip()
    if manual_key:
        print("🎵 [TikTok Bot] Chiave TikTok manuale trovata in configurazione.")
        with open('/tmp/tiktok_rtmp.txt', 'w') as f:
            if manual_key.startswith('rtmp'):
                f.write(manual_key)
            else:
                f.write(f"rtmp://live-push.tiktok-cdns.com/live/{manual_key}")
        return

    # Check cookies file
    cookies_path = '/tmp/tiktok_cookies.json'
    if os.path.exists(cookies_path):
        print("🎵 [TikTok Bot] Cookie di sessione TikTok trovati.")
    else:
        print("ℹ️ [TikTok Bot] In attesa di stream key o fallback serverless...")

if __name__ == '__main__':
    extract_tiktok_live()
