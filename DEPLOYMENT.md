# Deployment Guide

- [Deployment Guide](#deployment-guide)
  - [Quick Start](#quick-start)
  - [Environment Variables](#environment-variables)
  - [Database Migrations](#database-migrations)
  - [Health Checks](#health-checks)
  - [Troubleshooting](#troubleshooting)

## Quick Start

1. **Set up Discord Application**
   - Create app at <https://discord.com/developers/applications>
   - Get bot token, client ID, and client secret
   - Set redirect URI: `https://yourdomain.com/api/auth/callback/discord`

2. **Local Development**

   ```bash
   # Bot
   cd apps/bot
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your credentials
   alembic upgrade head
   python -m vezbot.main

   # Dashboard
   cd apps/dashboard
   npm install
   cp .env.example .env.local
   # Edit .env.local with your credentials
   npm run dev
   ```

3. **Production Deployment**
   - Add services: Postgres, Redis (optional), Bot, Dashboard
   - Set environment variables
   - Deploy!

## Environment Variables

See `.env.example` files in each app directory for required variables.

## Database Migrations

Migrations should on deployment startup. For manual runs:

```bash
cd apps/bot
alembic upgrade head
```

## Health Checks

- Bot: `GET /health` → `{"status": "healthy"}`
- Dashboard: Next.js default health check

## Troubleshooting

- **Bot not responding**: Check `DISCORD_TOKEN` and bot permissions
- **OAuth not working**: Verify redirect URI matches Discord app settings
- **Database errors**: Ensure `DATABASE_URL` is correct and migrations ran
- **Webhooks failing**: Check `BASE_URL` is accessible and Twitch credentials are valid
