#!/usr/bin/env python3
"""
Test rapide du bot Telegram News
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv
import anthropic

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY", "")
MARKETAUX_API_KEY = os.environ.get("MARKETAUX_API_KEY", "")

def get_news_finnhub():
    """Récupère les news depuis Finnhub"""
    if not FINNHUB_API_KEY:
        return []

    url = f"https://finnhub.io/api/v1/news?category=general&token={FINNHUB_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        news = response.json()
        return news[:10]
    except Exception as e:
        print(f"Erreur Finnhub: {e}")
        return []


def get_news_marketaux():
    """Récupère les news depuis Marketaux"""
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
    """Utilise Claude pour analyser les news"""
    if not ANTHROPIC_API_KEY or not news_articles:
        return None

    news_text = "\n\n".join([
        f"Titre: {article.get('headline', article.get('title', 'Sans titre'))}\n"
        f"Source: {article.get('source', 'Inconnue')}\n"
        f"Résumé: {article.get('summary', article.get('description', 'N/A'))[:200]}"
        for article in news_articles[:5]
    ])

    prompt = f"""Analyse ces actualités et crée un résumé pour Telegram.

Actualités:
{news_text}

Format requis (exemple):
📈 Bitcoin atteint 125K$, porté par la recherche de valeurs refuges pendant la crise politique américaine.

🛢️ OPEC+ augmente sa production de 137K barils/jour malgré les craintes de surproduction mondiale.

💰 Les investisseurs se tournent vers l'or et le Bitcoin pour se protéger contre l'affaiblissement du dollar.

IMPORTANT:
- 3-5 points numérotés avec émoji
- 1-2 lignes par point
- Texte simple, SANS markdown (pas de **, ##, etc.)
- Direct et factuel
"""

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
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


# Test rapide
print("🧪 Test du bot Telegram News...")
print("\n1. Test configuration...")

if not all([TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, ANTHROPIC_API_KEY]):
    print("❌ Configuration manquante!")
    exit(1)

print("✅ Configuration OK")

print("\n2. Test récupération news...")
finnhub_news = get_news_finnhub()
marketaux_news = get_news_marketaux()
all_news = finnhub_news + marketaux_news

print(f"   Finnhub: {len(finnhub_news)} articles")
print(f"   Marketaux: {len(marketaux_news)} articles")
print(f"   Total: {len(all_news)} articles")

if not all_news:
    print("❌ Aucune news trouvée!")
    exit(1)

print("✅ News récupérées")

print("\n3. Test analyse Claude...")
summary = analyze_news_with_claude(all_news)

if summary:
    print("✅ Analyse Claude OK")
    print(f"\nRésumé:\n{summary}")
else:
    print("❌ Erreur analyse Claude")
    exit(1)

print("\n4. Test envoi Telegram...")
timestamp = datetime.now().strftime("%H:%M")
message = f"📰 <b>Test News Bot - {timestamp}</b>\n\n{summary}"

if send_telegram_message(message):
    print("✅ Message envoyé sur Telegram!")
    print("\n🎉 Tous les tests réussis! Vérifiez votre Telegram.")
else:
    print("❌ Échec envoi Telegram")
    exit(1)
