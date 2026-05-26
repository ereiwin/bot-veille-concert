import os
import time
import feedparser
import requests
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# =========================
# CONFIG (Sécurisée pour Render)
# =========================
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

ARTISTS = ["Angus & Julia Stone", "Archive", "Muse", "Arcade Fire", "Asian Dub Foundation", "Black Keys", "C2C", "DJ Krush", "Elastica", "Faithless", "Fat freddy's drop", "Godspeed you black emperor", "Hugo Kant", "Iron Maiden", "Justice", "K's Choice", "Lilly Wood and the prick", "Massive Attack", "Metallica", "Overwerk", "Portishead", "Radiohead", "Red Hot Chili Peppers", "Rudimental", "Senbei", "Smashing Pumpkins", "Soundagarden", "Stupeflip", "the heavy", "Tom McRae", "TTC", "Wax Tailor", "Woodkid", "Zero 7"]
KEYWORDS = ["presale", "pre-sale", "on sale", "tickets", "tour", "Paris", "France", "Accor Arena", "Stade de France", "Zénith", "Elysee Montmartre", "Le Trianon", "La Maroquinerie", "La Cigale", "Le Trabendo", "New Morning"]
RSS_FEEDS = ["https://www.ticketmaster.fr/rss", "https://www.livenation.fr/event/rss"]

# =========================
# FAUX SERVEUR WEB POUR RENDER
# =========================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot is alive and watching!")

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# =========================
# TELEGRAM SEND
# =========================
def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"Erreur d'envoi Telegram : {e}", flush=True)

def is_relevant(text):
    text_lower = text.lower()
    return any(a.lower() in text_lower for a in ARTISTS) and any(k.lower() in text_lower for k in KEYWORDS)

def format_alert(entry_title, entry_link):
    return f"🚨 <b>CONCERT ALERT</b>\n\n🎤 Match détecté !\n📌 <b>{entry_title}</b>\n\n🔗 <a href='{entry_link}'>Lien billetterie</a>"

# =========================
# BOUCLE DE VEILLE
# =========================
def bot_loop():
    print("Boucle de veille démarrée...", flush=True)
    seen = set()
    premiere_execution = True

    while True:
        print(f"Vérification des flux RSS... ({time.strftime('%H:%M:%S')})", flush=True)
        for feed_url in RSS_FEEDS:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries:
                    uid = entry.get("id", entry.link)
                    if uid in seen:
                        continue
                    seen.add(uid)

                    if premiere_execution:
                        continue

                    content = entry.title + " " + entry.get("summary", "")
                    if is_relevant(content):
                        msg = format_alert(entry.title, entry.link)
                        send_telegram(msg)
            except Exception as e:
                print(f"Erreur flux {feed_url} : {e}", flush=True)

        if premiere_execution:
            print("Initialisation terminée. Prêt à dégainer !", flush=True)
            premiere_execution = False

        time.sleep(300) # 5 minutes

# =========================
# LANCEMENT SIMULTANÉ
# =========================
if __name__ == "__main__":
    server_thread = threading.Thread(target=run_health_server, daemon=True)
    server_thread.start()

    bot_loop()
