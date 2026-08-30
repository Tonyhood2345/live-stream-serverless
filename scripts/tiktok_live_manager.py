"""
═══════════════════════════════════════════════════════════════════════
📁 TIKTOK LIVE MANAGER (PYTHON RUNNER STANDALONE)
Esegue la gestione indipendente e parallela di TikTok LIVE per il cloud runner
═══════════════════════════════════════════════════════════════════════
"""

import os
import sys
import time
import subprocess

def run_tiktok_automation():
    print("🎵 [TikTok Live Manager] Avvio processo dedicato TikTok LIVE...")
    
    # 1. Verifica presenza chiave manuale o configurata
    tk_key = os.environ.get('TK_KEY', '').strip()
    if tk_key:
        print(f"🎵 [TikTok Live Manager] Chiave configurata trovata.")
        with open('/tmp/tiktok_rtmp.txt', 'w', encoding='utf-8') as f:
            if tk_key.startswith('rtmp'):
                f.write(tk_key)
            else:
                f.write(f"rtmp://live-push.tiktok-cdns.com/live/{tk_key}")
        print("✅ [TikTok Live Manager] Endpoint RTMP scritto con successo.")
        return True

    # 2. Se non presente chiave manuale, tenta avvio adapter Node.js
    adapter_path = os.path.join(os.path.dirname(__file__), 'tiktok_live_adapter.js')
    if os.path.exists(adapter_path):
        print("🎵 [TikTok Live Manager] Esecuzione adapter Node.js per estrazione automatica...")
        try:
            res = subprocess.run(['node', adapter_path], capture_output=True, text=True, timeout=45)
            print(res.stdout)
            if res.returncode == 0 and os.path.exists('/tmp/tiktok_rtmp.txt'):
                print("✅ [TikTok Live Manager] Adapter completato con successo.")
                return True
        except Exception as e:
            print(f"⚠️ [TikTok Live Manager] Avviso esecuzione adapter: {e}")

    print("ℹ️ [TikTok Live Manager] Nessuna chiave o sessione rilevata. Gli altri canali continuano regolarmente.")
    return False

if __name__ == '__main__':
    run_tiktok_automation()
