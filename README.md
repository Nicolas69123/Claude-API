# Claude API

Script Python pour utiliser l'API Claude de manière autonome.

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

1. Copiez `.env.example` vers `.env`
2. Ajoutez votre clé API Anthropic dans `.env`:
```
ANTHROPIC_API_KEY=votre-clé-ici
```

## Utilisation

```bash
python claude_api.py
```

## Déploiement sur Railway

1. Connectez ce repo à Railway
2. Ajoutez la variable d'environnement `ANTHROPIC_API_KEY` dans Railway
3. Railway exécutera automatiquement le script
