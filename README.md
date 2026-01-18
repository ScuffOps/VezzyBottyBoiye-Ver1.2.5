# Vezbot

Premium, lore-themed all-in-one Discord bot + web dashboard with multi-branding support.

- [Vezbot](#vezbot)
  - [Features](#features)
  - [Tech Stack](#tech-stack)
  - [Local Development](#local-development)
    - [Prerequisites](#prerequisites)
    - [Setup](#setup)
  - [Discord App Setup](#discord-app-setup)
  - [Deployment](#deployment)
    - [Prerequisites for Backend](#prerequisites-for-backend)
    - [General Steps](#general-steps)
  - [Project Structure](#project-structure)
  - [Commands](#commands)
    - [Bot Commands](#bot-commands)
  - [Configuration](#configuration)
    - [Multi-Branding](#multi-branding)
    - [Module Configuration](#module-configuration)
  - [License](#license)

## Features

- **Multi-Branding**: Each server can define custom brand tokens (name, logo, colors, microcopy)
- **Tickets**: Thread-based ticket system with private thread support and automatic fallback
- **Embeds/Webhooks**: Saved embed templates with rich builder
- **Polls**: Single/multi-select polls with scheduled closing and timezone support
- **Reminders**: Per-user and per-channel reminders with timezone conversion
- **Integrations**: Twitch EventSub alerts (MVP), extensible framework for more
- **Web Dashboard**: Full-featured configuration interface with Discord OAuth2

## Tech Stack

- **Bot**: Python 3.12+, discord.py 2.x, SQLAlchemy 2.0, Alembic, Redis + ARQ, Pydantic v2
- **Dashboard**: Next.js (App Router), TailwindCSS, shadcn/ui, Discord OAuth2
- **Database**: PostgreSQL
- **Deployment**: [Your Host/VPS]

## Local Development

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL 14+
- Redis (optional, for background jobs)

### Setup

1. **Clone and install dependencies**

```bash
# Install bot dependencies
cd apps/bot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Install dashboard dependencies
cd ../../apps/dashboard
npm install
```

1. **Environment Variables**

Create `.env` files:

**apps/bot/.env**:

```env
DISCORD_TOKEN=your_bot_token
DISCORD_CLIENT_ID=your_client_id
DISCORD_CLIENT_SECRET=your_client_secret
DISCORD_REDIRECT_URI=http://localhost:3000/api/auth/callback/discord

DATABASE_URL=postgresql://user:pass@localhost:5432/vezbot
REDIS_URL=redis://localhost:6379

TWITCH_CLIENT_ID=your_twitch_client_id
TWITCH_CLIENT_SECRET=your_twitch_client_secret

LOG_LEVEL=INFO
```

**apps/dashboard/.env.local**:

```env
NEXT_PUBLIC_DISCORD_CLIENT_ID=your_client_id
DISCORD_CLIENT_SECRET=your_client_secret
NEXT_PUBLIC_DISCORD_REDIRECT_URI=http://localhost:3000/api/auth/callback/discord
NEXT_PUBLIC_DASHBOARD_URL=http://localhost:3000

DATABASE_URL=postgresql://user:pass@localhost:5432/vezbot

NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=generate_with_openssl_rand_hex_32
```

1. **Database Setup**

```bash
cd apps/bot
alembic upgrade head
```

1. **Run Services**

```bash
# Terminal 1: Bot
cd apps/bot
python -m vezbot.main

# Terminal 2: Dashboard
cd apps/dashboard
npm run dev

# Terminal 3: ARQ Worker (if using Redis)
cd apps/bot
arq vezbot.workers.tasks.WorkerSettings
```

## Discord App Setup

1. Go to <https://discord.com/developers/applications>
2. Create a new application
3. **Bot Tab**:
   - Enable "Message Content Intent" (if using prefix commands)
   - Enable "Server Members Intent"
   - Copy bot token
4. **OAuth2 Tab**:
   - Add redirect URI: `http://localhost:3000/api/auth/callback/discord` (dev)
   - Copy Client ID and Client Secret
5. **Install Bot**:
   - OAuth2 → URL Generator → Select `bot` and `applications.commands` scopes
   - Select permissions: Manage Channels, Manage Threads, Send Messages, Embed Links, Use External Emojis, Read Message History
   - Use generated URL to invite bot

## Deployment

### Prerequisites for Backend

- Hosting provider (VPS, Cloud, etc.)
- PostgreSQL Database
- Redis (Optional)

### General Steps

1. **Deploy Services**
   - **Postgres**: Set up PostgreSQL database
   - **Redis** (optional): Set up Redis
   - **Bot Service**: Deploy code from `apps/bot`
   - **Dashboard Service**: Deploy code from `apps/dashboard`

2. **Environment Variables**

Set in your hosting environment for each service:

**Bot Service**:

- `DISCORD_TOKEN`
- `DISCORD_CLIENT_ID`
- `DISCORD_CLIENT_SECRET`
- `DISCORD_REDIRECT_URI` (your dashboard URL + `/api/auth/callback/discord`)
- `DATABASE_URL` (connection string)
- `REDIS_URL` (connection string, if used)
- `TWITCH_CLIENT_ID`, `TWITCH_CLIENT_SECRET`
- `BASE_URL` (your bot's public URL for webhooks)
- `LOG_LEVEL=INFO`

**Dashboard Service**:

- `NEXT_PUBLIC_DISCORD_CLIENT_ID`
- `DISCORD_CLIENT_SECRET`
- `NEXT_PUBLIC_DISCORD_REDIRECT_URI`
- `NEXT_PUBLIC_DASHBOARD_URL`
- `DATABASE_URL`
- `NEXTAUTH_URL`
- `NEXTAUTH_SECRET`

1. **Deploy**
   - Run migrations on bot service startup (`alembic upgrade head`)
   - Build and start both services

## Project Structure

```text
.
├── apps/
│   ├── bot/              # Discord bot (Python)
│   └── dashboard/        # Web dashboard (Next.js)
├── packages/
│   ├── shared/          # Shared schemas/constants
│   └── db/              # Database models (optional, can be in bot)
└── README.md
```

## Commands

### Bot Commands

- `/setup` - Interactive setup wizard
- `/ticket create` - Create a ticket
- `/embed create` - Create an embed
- `/poll create` - Create a poll
- `/reminder set` - Set a reminder
- `/timezone set` - Set your timezone

See `COMMANDS.md` for full command list and permissions.

## Configuration

### Multi-Branding

Each guild can configure:

- Display name, short name, icon URL
- Primary, accent, neutral colors
- Footer text, tagline
- Microcopy voice (formal, casual, mystic)
- Embed tone presets (scroll, codex, dispatch, decree)

Configure via dashboard or `/setup` wizard.

### Module Configuration

Enable/disable modules per guild:

- Tickets
- Embeds/Webhooks
- Polls
- Reminders
- Integrations

## License

MIT
