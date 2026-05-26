import os
import time
import feedparser
import requests

# =========================
# CONFIG (Sécurisée pour Render)
# =========================

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

ARTISTS = ["Muse", "Radiohead"]

KEYWORDS = [
    "presale",
    "pre-sale",
    "on sale",
    "tickets",
    "tour",
    "Paris",
    "France",
    "Accor Arena",
    "Stade de France",
    "Zénith",
]

RSS_FEEDS = [
    "https://www.ticketmaster.fr/rss",
    "https://www.livenation.fr/event/rss",
]


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
        print(f"Erreur d'envoi Telegram : {e}")


# =========================
# CHECK ITEM
# =========================


def is_relevant(text):
    text_lower = text.lower()
    artist_match = any(a.lower() in text_lower for a in ARTISTS)
    keyword_match = any(k.lower() in text_lower for k in KEYWORDS)
    return artist_match and keyword_match


# =========================
# FORMAT MESSAGE
# =========================


def format_alert(entry_title, entry_link):
    return f"""🚨 <b>CONCERT ALERT</b>

🎤 Match détecté pour vos artistes !
📌 <b>{entry_title}</b>

⚡ Nouvelle annonce ou prévente détectée.

🔗 <a href="{entry_link}">Cliquez ici pour voir l'événement</a>
"""


# =========================
# MAIN LOOP
# =========================

if __name__ == "__main__":
    print("Démarrage du bot de veille...")

    seen = set()
    premiere_execution = True

    while True:
        print(f"Vérification des flux RSS... ({time.strftime('%H:%M:%S')})")

        for feed_url in RSS_FEEDS:
            try:
                feed = feedparser.parse(feed_url)

                for entry in feed.entries:
                    uid = entry.get("id", entry.link)

                    if uid in seen:
                        continue

                    seen.add(uid)

                    # Si c'est le tout premier lancement du bot, on enregistre juste l'existant sans spammer
                    if premiere_execution:
                        continue

                    content = entry.title + " " + entry.get("summary", "")

                    if is_relevant(content):
                        msg = format_alert(entry.title, entry.link)
                        send_telegram(msg)

            except Exception as e:
                print(f"Erreur lors de la lecture du flux {feed_url} : {e}")

        # Une fois le premier tour fini, le bot est "armé" pour les prochaines nouveautés
        if premiere_execution:
            print("Initialisation terminée. Le bot est aux aguets !")
            premiere_execution = False

        time.sleep(300)  # Check toutes les 5 minutes
