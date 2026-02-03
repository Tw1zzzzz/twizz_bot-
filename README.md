# Twizz Bot

Telegram bot for ScoutScope, PerformanceCoach CRM, and related products.

## Quick Start

1. Create a virtual environment:

```bash
python3 -m venv venv
```

2. Install dependencies:

```bash
./venv/bin/pip install -r requirements.txt
```

3. Create `.env` from `.env.example` and set values.

4. Run the bot:

```bash
./venv/bin/python main.py
```

## Environment Variables

- `BOT_TOKEN` – Telegram bot token
- `ADMIN_IDS` – comma-separated Telegram user IDs for admins

## Deploy (Linux)

1. Upload the project to `/opt/twizz_bot` (or any path you prefer).
2. Create `.env` in that folder.
3. Run:

```bash
./scripts/deploy.sh
```

4. Copy the systemd unit from `deploy/scoutscope-bot.service` and adjust paths, user, and group.
5. Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable scoutscope-bot
sudo systemctl start scoutscope-bot
```

## Update

```bash
./scripts/update.sh
```

Restart your service if needed:

```bash
sudo systemctl restart scoutscope-bot
```

## Security Notes

- Do not commit `.env`.
- Keep `.env` permissions restrictive (e.g. `chmod 600 .env`).
- Run the bot as a non-root user.
- Keep the OS and Python dependencies updated.
