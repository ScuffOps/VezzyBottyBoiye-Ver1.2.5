"""ARQ worker tasks."""

from datetime import datetime

import discord
from arq import create_pool
from arq.connections import RedisSettings

from vezbot.config import settings
from vezbot.database import AsyncSessionLocal
from vezbot.models.reminders import Reminder
from vezbot.models.polls import Poll
from vezbot.utils.logging import get_logger

logger = get_logger(__name__)


async def process_reminders(ctx: dict) -> None:
    """Process due reminders."""
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select

        now = datetime.now()
        result = await session.execute(
            select(Reminder).where(
                Reminder.remind_at <= now, Reminder.completed == False
            )
        )
        reminders = result.scalars().all()

        for reminder in reminders:
            try:
                from vezbot.bot import bot

                guild = bot.get_guild(reminder.guild_id)
                if not guild:
                    continue

                user = guild.get_member(reminder.user_id)
                if not user:
                    continue

                channel = (
                    guild.get_channel(reminder.channel_id)
                    if reminder.channel_id
                    else None
                )

                if channel and isinstance(channel, discord.TextChannel):
                    await channel.send(f"{user.mention} Reminder: {reminder.message}")
                else:
                    await user.send(f"Reminder: {reminder.message}")

                reminder.completed = True
                await session.commit()

                logger.info(f"Sent reminder {reminder.id}", reminder_id=reminder.id)
            except Exception as e:
                logger.error(f"Failed to send reminder {reminder.id}: {e}")

        await session.commit()


async def close_polls(ctx: dict) -> None:
    """Close expired polls."""
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select

        now = datetime.now()
        result = await session.execute(
            select(Poll).where(Poll.closes_at <= now, Poll.closed == False)
        )
        polls = result.scalars().all()

        for poll in polls:
            poll.closed = True
            # Update poll message (you can add logic here)
            await session.commit()
            logger.info(f"Closed poll {poll.id}", poll_id=poll.id)


class WorkerSettings:
    """ARQ worker settings."""

    redis_settings = RedisSettings.from_dsn(settings.redis_url) if settings.redis_url else None
    functions = [process_reminders, close_polls]
    cron_jobs = [
        # Run every minute
        {"function": process_reminders, "cron": "* * * * *"},
        {"function": close_polls, "cron": "* * * * *"},
    ]
