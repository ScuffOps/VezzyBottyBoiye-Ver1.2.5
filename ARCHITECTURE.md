# Vezbot Architecture Plan

## Milestones

### M1: Foundation (Core Infrastructure)
- Monorepo structure
- Database models + migrations
- Bot core (discord.py 2.x setup, error handling, logging)
- Shared schemas package
- Multi-branding system foundation

### M2: Setup & Configuration
- Setup Wizard (Discord interactive)
- GuildConfig + GuildBrand persistence
- Permission validation
- Private thread capability detection + fallback logic

### M3: Core Modules (MVP)
- Tickets (threads, forms, transcripts)
- Embeds/Webhooks (templates, builder)
- Polls (single/multi, scheduled, timezone-aware)
- Reminders (per-user, timezone conversion)

### M4: Integrations (MVP)
- Twitch EventSub (full end-to-end)
- Integration framework for future additions

### M5: Dashboard
- Discord OAuth2 authentication
- Guild selector + permission gating
- Module configuration pages
- Branding editor with live preview
- Audit logs + error logs viewer
- Config import/export

### M6: Deployment
- Deployment configs (Procfile, healthchecks, systemd, Docker, etc.)
- Migration automation
- Environment variable templates
- Documentation (README, deploy guide)

---

## Bot Architecture

### Directory Structure
```
apps/bot/
├── vezbot/
│   ├── __init__.py
│   ├── main.py                 # Entry point, bot initialization
│   ├── config.py               # Settings from env vars
│   ├── bot.py                  # Bot instance + setup
│   │
│   ├── cogs/                   # Discord.py cogs (feature modules)
│   │   ├── __init__.py
│   │   ├── setup.py            # Setup wizard
│   │   ├── tickets.py          # Ticket commands + handlers
│   │   ├── embeds.py           # Embed/webhook commands
│   │   ├── polls.py            # Poll commands
│   │   ├── reminders.py        # Reminder commands
│   │   └── admin.py            # Admin utilities
│   │
│   ├── services/               # Business logic layer
│   │   ├── __init__.py
│   │   ├── ticket_service.py   # Ticket creation, state management
│   │   ├── embed_service.py    # Embed building, webhook posting
│   │   ├── poll_service.py     # Poll creation, voting logic
│   │   ├── reminder_service.py # Reminder scheduling
│   │   ├── timezone_service.py # Timezone conversion utilities
│   │   └── branding_service.py # Brand-aware embed building
│   │
│   ├── repositories/           # Data access layer
│   │   ├── __init__.py
│   │   ├── base.py             # Base repository pattern
│   │   ├── guild_repo.py       # GuildConfig, GuildBrand
│   │   ├── ticket_repo.py      # Tickets, transcripts
│   │   ├── poll_repo.py        # Polls, votes
│   │   └── user_repo.py        # UserProfile (timezone, etc.)
│   │
│   ├── models/                 # SQLAlchemy models (or import from packages/db)
│   │   └── (see DB schema section)
│   │
│   ├── schemas/                # Pydantic models (validation)
│   │   ├── config.py           # GuildConfig, GuildBrand schemas
│   │   ├── ticket.py           # Ticket creation, state schemas
│   │   ├── embed.py            # Embed template schemas
│   │   └── poll.py             # Poll schemas
│   │
│   ├── integrations/           # External integrations
│   │   ├── __init__.py
│   │   ├── base.py             # Integration base class
│   │   ├── twitch.py           # Twitch EventSub handler
│   │   └── webhook_handler.py  # Generic webhook receiver
│   │
│   ├── workers/                # Background jobs (ARQ)
│   │   ├── __init__.py
│   │   ├── scheduler.py        # Reminder/poll close jobs
│   │   └── tasks.py             # Job definitions
│   │
│   ├── utils/                  # Utilities
│   │   ├── permissions.py     # Permission checks
│   │   ├── threads.py          # Thread creation helpers (private/public fallback)
│   │   ├── embeds.py           # Embed builders
│   │   └── logging.py           # structlog setup
│   │
│   └── api/                    # Optional FastAPI for bot HTTP API
│       ├── __init__.py
│       ├── main.py             # FastAPI app
│       └── routes.py            # API endpoints
│
├── alembic/                    # Migrations
│   ├── versions/
│   └── env.py
│
├── alembic.ini
├── pyproject.toml
└── requirements.txt
```

### Service Layer Pattern
- **Cogs**: Handle Discord interactions (commands, buttons, modals)
- **Services**: Business logic, orchestration, validation
- **Repositories**: Database access, queries
- **Schemas**: Pydantic validation at boundaries

### Key Services

**TicketService**
- `create_ticket(guild_id, user_id, form_data, channel_id) -> Ticket`
  - Attempts private thread first
  - Falls back to restricted public thread if needed
  - Creates transcript record
- `update_ticket_state(ticket_id, state, staff_id) -> Ticket`
- `add_transcript_entry(ticket_id, content, author_id) -> None`

**BrandingService**
- `get_guild_brand(guild_id) -> GuildBrand`
- `build_lore_embed(brand, tone, title, sections, ...) -> Embed`
- `get_microcopy(brand, key, context) -> str`

**TimezoneService**
- `convert_to_user_tz(dt, user_id) -> datetime`
- `convert_to_guild_tz(dt, guild_id) -> datetime`
- `parse_timezone_input(input_str) -> timezone`

---

## Database Schema

### Core Tables

**guilds**
- `id` (BIGINT, PK) - Discord guild ID
- `config_json` (JSONB) - Module settings, feature flags
- `created_at`, `updated_at` (TIMESTAMP)

**guild_brands**
- `id` (SERIAL, PK)
- `guild_id` (BIGINT, FK → guilds.id, UNIQUE)
- `display_name` (VARCHAR)
- `short_name` (VARCHAR)
- `icon_url` (VARCHAR, nullable)
- `primary_color` (INTEGER) - Decimal color
- `accent_color` (INTEGER)
- `neutral_color` (INTEGER)
- `footer_text` (VARCHAR, nullable)
- `tagline` (VARCHAR, nullable)
- `microcopy_voice` (VARCHAR) - 'formal', 'casual', 'mystic', etc.
- `embed_tone_preset` (VARCHAR) - 'scroll', 'codex', 'dispatch', 'decree'
- `created_at`, `updated_at`

**user_profiles**
- `id` (SERIAL, PK)
- `user_id` (BIGINT) - Discord user ID
- `guild_id` (BIGINT, FK → guilds.id)
- `timezone` (VARCHAR) - IANA timezone (e.g., 'America/New_York')
- `currency_balance` (INTEGER, default 0)
- `created_at`, `updated_at`
- UNIQUE(user_id, guild_id)

**tickets**
- `id` (SERIAL, PK)
- `guild_id` (BIGINT, FK → guilds.id)
- `channel_id` (BIGINT) - Discord channel/thread ID
- `thread_id` (BIGINT, nullable) - If different from channel_id
- `creator_id` (BIGINT) - Discord user ID
- `form_template_id` (INTEGER, FK → form_templates.id, nullable)
- `state` (VARCHAR) - 'open', 'pending', 'closed', 'archived'
- `claimed_by_id` (BIGINT, nullable)
- `tags` (VARCHAR[], nullable)
- `metadata_json` (JSONB) - Custom fields from form
- `created_at`, `updated_at`, `closed_at` (nullable)

**ticket_transcripts**
- `id` (SERIAL, PK)
- `ticket_id` (INTEGER, FK → tickets.id)
- `content_markdown` (TEXT)
- `content_html` (TEXT, nullable)
- `created_at`

**form_templates**
- `id` (SERIAL, PK)
- `guild_id` (BIGINT, FK → guilds.id)
- `name` (VARCHAR)
- `description` (VARCHAR, nullable)
- `fields_json` (JSONB) - Array of field definitions
- `created_at`, `updated_at`

**form_submissions**
- `id` (SERIAL, PK)
- `form_template_id` (INTEGER, FK → form_templates.id)
- `user_id` (BIGINT)
- `ticket_id` (INTEGER, FK → tickets.id, nullable)
- `data_json` (JSONB)
- `status` (VARCHAR) - 'pending', 'approved', 'denied'
- `reviewer_id` (BIGINT, nullable)
- `review_notes` (TEXT, nullable)
- `created_at`, `updated_at`

**embed_templates**
- `id` (SERIAL, PK)
- `guild_id` (BIGINT, FK → guilds.id)
- `name` (VARCHAR)
- `embed_json` (JSONB) - Discord embed structure
- `components_json` (JSONB, nullable) - Buttons/selects
- `webhook_url` (VARCHAR, nullable)
- `created_at`, `updated_at`

**polls**
- `id` (SERIAL, PK)
- `guild_id` (BIGINT, FK → guilds.id)
- `channel_id` (BIGINT)
- `message_id` (BIGINT)
- `creator_id` (BIGINT)
- `question` (VARCHAR)
- `options_json` (JSONB) - Array of option objects
- `type` (VARCHAR) - 'single', 'multi'
- `closes_at` (TIMESTAMP, nullable)
- `closed` (BOOLEAN, default false)
- `created_at`

**poll_votes**
- `id` (SERIAL, PK)
- `poll_id` (INTEGER, FK → polls.id)
- `user_id` (BIGINT)
- `option_indices` (INTEGER[]) - For multi-select
- `created_at`
- UNIQUE(poll_id, user_id)

**reminders**
- `id` (SERIAL, PK)
- `guild_id` (BIGINT, FK → guilds.id)
- `user_id` (BIGINT)
- `channel_id` (BIGINT, nullable) - If channel reminder
- `message` (VARCHAR)
- `remind_at` (TIMESTAMP)
- `recurring_pattern` (VARCHAR, nullable) - 'daily', 'weekly', etc.
- `completed` (BOOLEAN, default false)
- `created_at`

**integration_configs**
- `id` (SERIAL, PK)
- `guild_id` (BIGINT, FK → guilds.id)
- `provider` (VARCHAR) - 'twitch', 'youtube', 'twitter', etc.
- `config_json` (JSONB) - Provider-specific config
- `enabled` (BOOLEAN, default false)
- `webhook_secret` (VARCHAR, nullable)
- `created_at`, `updated_at`

**audit_logs**
- `id` (SERIAL, PK)
- `guild_id` (BIGINT, FK → guilds.id)
- `user_id` (BIGINT, nullable)
- `action` (VARCHAR)
- `resource_type` (VARCHAR) - 'ticket', 'poll', 'config', etc.
- `resource_id` (VARCHAR, nullable)
- `details_json` (JSONB)
- `created_at`

**error_logs**
- `id` (SERIAL, PK)
- `guild_id` (BIGINT, FK → guilds.id, nullable)
- `correlation_id` (VARCHAR)
- `error_type` (VARCHAR)
- `message` (TEXT)
- `stack_trace` (TEXT, nullable)
- `context_json` (JSONB)
- `created_at`

---

## Interaction Flows

### Setup Wizard Flow

1. **Trigger**: `/setup` command (admin only)
2. **Step 1: Welcome**
   - Lore embed with brand placeholder
   - Button: "Begin Setup"
3. **Step 2: Channel Selection**
   - Modal: "Select Ticket Hub Channel" (channel select)
   - Validates: bot has View Channel + Manage Threads
4. **Step 3: Private Thread Test**
   - Attempts to create a test private thread
   - If fails: shows explanation + fallback option
   - Button: "Use Private Threads" or "Use Public Threads (Restricted)"
5. **Step 4: Role Selection**
   - Modal: "Select Staff Roles" (role select, multi)
   - Validates: bot has Manage Roles or role is below bot
6. **Step 5: Module Selection**
   - Buttons: Enable/disable modules (Tickets, Embeds, Polls, etc.)
   - Shows dependencies
7. **Step 6: Branding (Optional)**
   - Modal: Brand name, colors (hex), footer text, voice preset
   - Preview embed
8. **Step 7: Review Summary**
   - Embed showing all selections
   - Button: "Save & Activate"
9. **Step 8: Save**
   - Writes to DB (GuildConfig, GuildBrand)
   - Shows success embed
   - Button: "Open Dashboard" (deep link)

### Ticket Creation Flow

1. **Panel Message** (in ticket hub channel)
   - Embed with buttons: "Create Ticket", "Report Issue", "Apply", etc.
   - Each button maps to a form template
2. **User Clicks Button**
   - Opens modal with form fields (from template)
   - User submits
3. **Thread Creation**
   - `TicketService.create_ticket()`:
     - Attempts `channel.create_thread(name=..., type=ThreadType.private_thread)`
     - On `Forbidden` or `HTTPException` with "private threads not available":
       - Falls back to public thread
       - Sets channel permissions: deny @everyone View Messages, allow creator + staff
     - Creates DB record
4. **Thread Message**
   - Welcome embed (branded)
   - Shows form submission data
   - Buttons: "Claim", "Close", "Add User"
5. **Staff Actions**
   - Claim: updates `claimed_by_id`
   - Close: updates state, archives thread
   - Add User: adds user to thread, updates permissions

### Poll Creation Flow

1. **Command**: `/poll create question:"..." options:"A|B|C" type:single closes:"2024-01-01 12:00"`
2. **Validation**:
   - Parses timezone (user preference or guild default)
   - Converts `closes` to UTC
3. **Message Creation**:
   - Embed with question + options
   - Buttons for each option (or select menu if >5 options)
4. **Voting**:
   - Button click → updates `poll_votes`
   - Updates embed with live results
5. **Scheduled Close**:
   - ARQ job scheduled for `closes_at`
   - Locks voting, shows final results

### Twitch EventSub Flow

1. **Dashboard Setup**:
   - Admin enters Twitch Client ID + Secret
   - Bot generates webhook secret
   - Stores in `integration_configs`
2. **Subscription Creation**:
   - Bot calls Twitch EventSub API to subscribe to stream.online
   - Stores subscription ID in config
3. **Webhook Reception**:
   - FastAPI endpoint: `POST /webhooks/twitch`
   - Verifies webhook signature
   - On `stream.online`:
     - Fetches guild configs with Twitch enabled
     - Posts notification embed to configured channel
4. **Renewal**:
   - Twitch sends challenge on subscription
   - Bot responds with challenge
   - Periodic job checks subscription status

---

## Multi-Branding System

### GuildBrand Model
- Stores visual tokens per guild
- Defaults provided if not set

### Brand-Aware Embed Builder
```python
def build_lore_embed(
    brand: GuildBrand,
    tone: str,  # 'scroll', 'codex', 'dispatch', 'decree'
    title: str,
    description: str = None,
    fields: List[Dict] = None,
    footer: str = None,
    **kwargs
) -> Embed:
    # Maps tone to icon + color palette
    # Applies brand colors
    # Sets footer with brand.footer_text
    # Returns discord.Embed
```

### Microcopy Helper
```python
def get_microcopy(brand: GuildBrand, key: str, context: Dict = None) -> str:
    # Returns brand-appropriate phrase
    # Voice presets: formal, casual, mystic
    # Keys: 'ticket_welcome', 'poll_closed', 'setup_complete', etc.
```

---

## Next Steps

1. Create monorepo structure
2. Set up database models (SQLAlchemy)
3. Create Alembic migrations
4. Build bot core + cogs
5. Implement services layer
6. Build dashboard (Next.js)
7. Create production configs
8. Write documentation
