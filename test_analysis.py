#!/usr/bin/env python3
"""Test du nouveau format avec analyse Claude"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv
import anthropic

load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY", "")
MARKETAUX_API_KEY = os.environ.get("MARKETAUX_API_KEY", "")

def get_news_finnhub():
    if not FINNHUB_API_KEY:
        return []
    url = f"https://finnhub.io/api/v1/news?category=general&token={FINNHUB_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()[:10]
    except Exception as e:
        print(f"Erreur Finnhub: {e}")
        return []

def get_news_marketaux():
    if not MARKETAUX_API_KEY:
        return []
    url = f"https://api.marketaux.com/v1/news/all?api_token={MARKETAUX_API_KEY}&limit=10"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json().get('data', [])
    except Exception as e:
        print(f"Erreur Marketaux: {e}")
        return []

def analyze_news_with_claude(news_articles):
    if not ANTHROPIC_API_KEY or not news_articles:
        return None

    news_text = "\n\n".join([
        f"Titre: {article.get('headline', article.get('title', 'Sans titre'))}\n"
        f"Source: {article.get('source', 'Inconnue')}\n"
        f"Résumé: {article.get('summary', article.get('description', 'N/A'))[:200]}"
        for article in news_articles[:5]
    ])

    prompt = f"""Tu es un analyste expert en finance, trading et politique mondiale. Voici les dernières actualités majeures:

{news_text}

Ta mission:
1. Sélectionne les 3-4 événements MAJEURS mondiaux (finance, trading, politique)
2. Pour CHAQUE événement, donne:
   - Ce qui s'est passé (1 ligne)
   - TON ANALYSE et TON OPINION sur la situation (2-3 lignes)
   - Les implications possibles

Format (exemple):
📈 Bitcoin franchit 125K$ dans un contexte de crise politique américaine.

→ Mon analyse: Cette hausse reflète une perte de confiance dans les institutions traditionnelles. Les investisseurs cherchent des actifs décentralisés face à l'instabilité politique. Je pense que cette tendance va s'accélérer si le shutdown perdure, car les cryptos deviennent une vraie alternative refuge.

🛢️ L'OPEC+ augmente sa production malgré le surplus mondial.

→ Mon analyse: Décision surprenante qui montre des tensions internes à l'OPEC+. Certains membres ont besoin de revenus à court terme. Cela pourrait faire baisser les prix du pétrole et créer de nouvelles opportunités de trading sur les énergies.

IMPORTANT:
- Focus sur événements MONDIAUX majeurs
- Donne TON AVIS personnel et analyse
- Émojis pertinents
- SANS markdown (**, ##)
- Ton direct et expert
"""

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )

        text = message.content[0].text
        text = text.replace('# ', '').replace('## ', '').replace('### ', '')
        text = text.replace('**', '')
        while '\n\n\n' in text:
            text = text.replace('\n\n\n', '\n\n')
        lines = text.split('\n')
        filtered_lines = [line for line in lines if not ('Résumé' in line and len(line) < 50) and not ('Points clés' in line and len(line) < 30)]
        text = '\n'.join(filtered_lines).strip()
        return text
    except Exception as e:
        print(f"Erreur Claude API: {e}")
        return None

def send_telegram_message(text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Erreur Telegram: {e}")
        return False

# Test
print("🧪 Test du nouveau format avec analyse Claude...\n")

finnhub_news = get_news_finnhub()
marketaux_news = get_news_marketaux()
all_news = finnhub_news + marketaux_news

print(f"📰 {len(all_news)} articles récupérés\n")

if all_news:
    print("🤖 Analyse de Claude en cours...\n")
    analysis = analyze_news_with_claude(all_news)

    if analysis:
        print("="*60)
        print(analysis)
        print("="*60)

        today = datetime.now().strftime("%d/%m/%Y")
        message = f"🌍 <b>Actualités Mondiales - {today}</b>\n\n{analysis}\n\n━━━━━━━━━━━━━━━━"

        print("\n📤 Envoi sur Telegram...")
        if send_telegram_message(message):
            print("✅ Message envoyé! Vérifiez votre Telegram.")
        else:
            print("❌ Erreur envoi")
