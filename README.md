# Claude API

Scripts Python pour utiliser l'API Claude de manière autonome.

## Scripts disponibles

### 1. `claude_api.py` - Test de l'API Claude
Script simple pour tester l'API Claude.

### 2. `news_bot.py` - Bot Telegram News
Bot qui envoie automatiquement les dernières actualités (finance, trading, politique) toutes les 5 minutes via Telegram.

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

### Pour claude_api.py

1. Éditez `.env` et configurez:
```
ANTHROPIC_API_KEY=votre-clé-ici
```

2. Lancez:
```bash
python claude_api.py
```

### Pour news_bot.py

1. **Créez un bot Telegram:**
   - Cherchez @BotFather sur Telegram
   - Envoyez `/newbot` et suivez les instructions
   - Copiez le token du bot

2. **Obtenez votre Chat ID:**
   - Cherchez @userinfobot sur Telegram
   - Il vous donnera votre ID

3. **Obtenez une clé API Finnhub (gratuit):**
   - Allez sur https://finnhub.io/
   - Créez un compte gratuit
   - Copiez votre API key

4. **Configurez `.env`:**
```
ANTHROPIC_API_KEY=votre-clé-claude
TELEGRAM_BOT_TOKEN=votre-bot-token
TELEGRAM_CHAT_ID=votre-chat-id
FINNHUB_API_KEY=votre-finnhub-key
MARKETAUX_API_KEY=votre-marketaux-key (optionnel)
```

5. **Lancez le bot:**
```bash
python news_bot.py
```

Le bot enverra des news toutes les 5 minutes automatiquement!

## Déploiement sur Railway

1. Connectez ce repo à Railway
2. Ajoutez toutes les variables d'environnement dans Railway
3. Pour le news bot, utilisez: `python news_bot.py`
4. Railway exécutera le bot 24/7
