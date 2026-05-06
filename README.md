# train-delay-alert

Monitors TGV departures from Marne-la-Vallée, CDG, Lille Flandres, and Lille Europe. Sends a Telegram notification when a long-distance train is delayed 30+ minutes.

Runs automatically via GitHub Actions every 20 minutes between 5h and 22h (Paris time).

## Setup

**1. SNCF API key**

Register at [numerique.sncf.com/startup/api](https://numerique.sncf.com/startup/api) to get a free key.

**2. Telegram bot**

- Open Telegram → @BotFather → `/newbot` → save the token
- Send a message to your bot, then open `https://api.telegram.org/bot<TOKEN>/getUpdates` to get your `chat_id`

**3. GitHub Secrets**

Add these three secrets in `Settings → Secrets → Actions`:

| Secret | Value |
|--------|-------|
| `SNCF_API_KEY` | Your SNCF API key |
| `TELEGRAM_BOT_TOKEN` | Token from @BotFather |
| `TELEGRAM_CHAT_ID` | Your chat ID |

## Local dev

```bash
cp .env.example .env
# fill in .env with real keys
pip install -r requirements.txt
python monitor.py
```

To test the Telegram notification without waiting for a real delay:

```bash
TEST_MODE=true python monitor.py
```

## Configuration

Edit `monitor.py` to adjust:

- `DELAY_THRESHOLD_MINUTES` — default 30
- `MONITORED_STATIONS` — add/remove departure stations
- `LONG_DISTANCE_DESTINATIONS` — keywords to filter destination cities
