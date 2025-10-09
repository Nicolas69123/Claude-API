#!/usr/bin/env python3
"""
Telegram News Bot - Envoie les actualités mondiales tous les matins à 8h
Utilise Claude API pour analyser et donner son opinion sur les news
"""

import os
import time
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import anthropic
import schedule

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY", "")
MARKETAUX_API_KEY = os.environ.get("MARKETAUX_API_KEY", "")

def get_news_finnhub():
    """Récupère les news depuis Finnhub (finance/trading)"""
    if not FINNHUB_API_KEY:
        return []

    url = f"https://finnhub.io/api/v1/news?category=general&token={FINNHUB_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        news = response.json()
        return news[:10]  # Limite à 10 articles
    except Exception as e:
        print(f"Erreur Finnhub: {e}")
        return []


def get_news_marketaux():
    """Récupère les news depuis Marketaux (finance/politique/économie)"""
    if not MARKETAUX_API_KEY:
        return []

    url = f"https://api.marketaux.com/v1/news/all?api_token={MARKETAUX_API_KEY}&limit=10"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('data', [])
    except Exception as e:
        print(f"Erreur Marketaux: {e}")
        return []


def analyze_news_with_claude(news_articles):
    """Utilise Claude pour analyser et résumer les news"""
    if not ANTHROPIC_API_KEY or not news_articles:
        return None

    # Prépare le contexte des news
    news_text = "\n\n".join([
        f"Titre: {article.get('headline', article.get('title', 'Sans titre'))}\n"
        f"Source: {article.get('source', 'Inconnue')}\n"
        f"Résumé: {article.get('summary', article.get('description', 'N/A'))[:200]}"
        for article in news_articles[:15]  # Top 15 news pour couvrir tous les domaines
    ])

    prompt = f"""Tu es un analyste expert. Voici les dernières actualités:

{news_text}

Ta mission:
Sélectionne 1-2 événements MAJEURS dans CHACUN de ces 5 domaines:
🤖 IA (Intelligence Artificielle)
📊 Trading Algo
💰 Finance
🏛️ Politique
₿ Crypto

Pour CHAQUE événement, format COURT (6 lignes max):
- Le fait (1-2 lignes concises)
- Impact/Conséquence directe (2-3 lignes)
- Ton avis expert (1-2 lignes)

Exemple:
🤖 IA
OpenAI lance GPT-5 avec raisonnement quantique, performances 10x supérieures.
Impact: Révolution dans l'automatisation. Les entreprises sans IA avancée vont perdre en compétitivité. Microsoft et Google accélèrent leurs investissements.
Avis: Game changer absolu. Acheter NVIDIA/Microsoft maintenant avant l'explosion. Le marché sous-estime encore l'ampleur du changement.

₿ CRYPTO
Bitcoin dépasse 150K$ suite à l'adoption officielle par le Japon comme réserve nationale.
Impact: Validation institutionnelle massive. Les autres pays asiatiques vont suivre. Flux de plusieurs milliards vers les ETF Bitcoin spot. Volatilité court-terme attendue.
Avis: Consolidation probable à 145K avant continuation haussière. Opportunité d'achat sur correction. Target 200K d'ici 6 mois.

IMPORTANT:
- 1-2 news PAR domaine (5 domaines = 5-10 news total)
- Format COURT et percutant
- SANS markdown (**, ##)
- Émojis pour chaque domaine
- Avis tranché et actionnable
"""

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=3000,  # Plus de tokens pour couvrir les 5 domaines
            messages=[{"role": "user", "content": prompt}]
        )

        # Nettoie le markdown du résultat
        text = message.content[0].text
        # Enlève les titres markdown
        text = text.replace('# ', '').replace('## ', '').replace('### ', '')
        # Enlève le gras markdown
        text = text.replace('**', '')
        # Enlève les lignes vides multiples
        while '\n\n\n' in text:
            text = text.replace('\n\n\n', '\n\n')
        # Enlève les lignes de titre inutiles
        lines = text.split('\n')
        filtered_lines = [line for line in lines if not ('Résumé' in line and len(line) < 50) and not ('Points clés' in line and len(line) < 30)]
        text = '\n'.join(filtered_lines).strip()

        return text
    except Exception as e:
        print(f"Erreur Claude API: {e}")
        return None


def send_telegram_message(text):
    """Envoie un message via Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Configuration Telegram manquante!")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Erreur Telegram: {e}")
        return False


def send_daily_news():
    """Récupère et envoie les news du jour"""
    try:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Récupération des actualités mondiales...")

        # Récupère les news de différentes sources
        finnhub_news = get_news_finnhub()
        marketaux_news = get_news_marketaux()

        # Combine toutes les news
        all_news = finnhub_news + marketaux_news

        if all_news:
            print(f"✅ {len(all_news)} articles trouvés")

            # Analyse avec Claude
            analysis = analyze_news_with_claude(all_news)

            if analysis:
                # Prépare le message
                today = datetime.now().strftime("%d/%m/%Y")
                message = f"🌍 <b>Actualités Mondiales - {today}</b>\n\n{analysis}\n\n━━━━━━━━━━━━━━━━"

                # Envoie via Telegram
                if send_telegram_message(message):
                    print("✅ Message envoyé sur Telegram")
                else:
                    print("❌ Échec envoi Telegram")
            else:
                print("❌ Échec analyse Claude")
        else:
            print("⚠️ Aucune news trouvée")

    except Exception as e:
        print(f"❌ Erreur: {e}")


def main_loop():
    """Boucle principale - envoie des news tous les jours à 8h heure française"""
    print("🤖 Bot Telegram News démarré!")
    print(f"📅 Envoi quotidien programmé à 8h00 (heure française)")

    # Programme l'envoi quotidien à 6h UTC (8h heure française)
    schedule.every().day.at("06:00").do(send_daily_news)

    # Envoi immédiat pour test (optionnel - commenter après test)
    print("\n🧪 Envoi de test immédiat...")
    send_daily_news()

    print("\n⏰ En attente du prochain envoi à 8h00 (heure française)...")

    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Vérifie toutes les minutes
        except KeyboardInterrupt:
            print("\n\n🛑 Bot arrêté par l'utilisateur")
            break
        except Exception as e:
            print(f"❌ Erreur: {e}")
            time.sleep(60)


if __name__ == "__main__":
    # Vérification de la configuration
    if not all([TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, ANTHROPIC_API_KEY]):
        print("❌ Configuration manquante!")
        print("Vérifiez que ces variables sont définies dans .env:")
        print("- TELEGRAM_BOT_TOKEN")
        print("- TELEGRAM_CHAT_ID")
        print("- ANTHROPIC_API_KEY")
        print("- FINNHUB_API_KEY (optionnel)")
        print("- MARKETAUX_API_KEY (optionnel)")
    else:
        main_loop()
