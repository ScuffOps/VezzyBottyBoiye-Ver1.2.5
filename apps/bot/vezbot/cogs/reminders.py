"""Reminders cog."""

from datetime import datetime
from zoneinfo import ZoneInfo

import discord
from discord import app_commands
from discord.ext import commands

from vezbot.database import AsyncSessionLocal
from vezbot.models.reminders import Reminder
from vezbot.models.users import UserProfile
from vezbot.repositories.guild_repo import GuildBrandRepository
from vezbot.services.branding_service import build_lore_embed
from vezbot.services.timezone_service import convert_to_user_tz, get_user_timezone
from vezbot.utils.logging import get_logger

logger = get_logger(__name__)


class RemindersCog(commands.Cog):
    """Reminders cog."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="reminder-set", description="Set a reminder")
    @app_commands.describe(
        message="Reminder message",
        when="When to remind (ISO format or relative like 'in 1 hour')",
        channel="Channel to remind in (optional, defaults to DM)",
    )
    async def reminder_set(
        self,
        interaction: discord.Interaction,
        message: str,
        when: str,
        channel: discord.TextChannel | None = None,
    ) -> None:
        """Set a reminder."""
        if not interaction.guild:
            await interaction.response.send_message(
                "This command can only be used in a server.", ephemeral=True
            )
            return

        # Parse when
        try:
            # Try ISO format first
            remind_at = datetime.fromisoformat(when.replace("Z", "+00:00"))
        except ValueError:
            # Try relative time (simple parsing)
            # This is a simplified version; you might want to use dateutil.parser
            await interaction.response.send_message(
                "Please use ISO format (e.g., '2024-01-01T12:00:00Z')", ephemeral=True
            )
            return

        # Convert to user's timezone
        user_tz = await get_user_timezone(interaction.user.id, interaction.guild.id)
        if user_tz:
            remind_at = remind_at.astimezone(ZoneInfo(user_tz))

        async with AsyncSessionLocal() as session:
            reminder = Reminder(
                guild_id=interaction.guild.id,
                user_id=interaction.user.id,
                channel_id=channel.id if channel else None,
                message=message,
                remind_at=remind_at,
            )
            session.add(reminder)
            await session.commit()

            await interaction.response.send_message(
                f"Reminder set for {remind_at.strftime('%Y-%m-%d %H:%M')}", ephemeral=True
            )

    @app_commands.command(name="timezone-set", description="Set your timezone")
    @app_commands.describe(timezone="IANA timezone (e.g., 'America/New_York')")
    async def timezone_set(
        self, interaction: discord.Interaction, timezone: str
    ) -> None:
        """Set user timezone."""
        if not interaction.guild:
            await interaction.response.send_message(
                "This command can only be used in a server.", ephemeral=True
            )
            return

        # Validate timezone
        try:
            ZoneInfo(timezone)
        except Exception:
            await interaction.response.send_message(
                "Invalid timezone. Use IANA format (e.g., 'America/New_York').", ephemeral=True
            )
            return

        from vezbot.database import AsyncSessionLocal
        from vezbot.models.reminders import Reminder
        from sqlalchemy import select

        async with AsyncSessionLocal() as session:
            from vezbot.models.users import UserProfile

            result = await session.execute(
                select(UserProfile).where(
                    UserProfile.user_id == interaction.user.id,
                    UserProfile.guild_id == interaction.guild.id,
                )
            )
            profile = result.scalar_one_or_none()

            if profile:
                profile.timezone = timezone
            else:
                profile = UserProfile(
                    user_id=interaction.user.id,
                    guild_id=interaction.guild.id,
                    timezone=timezone,
                )
                session.add(profile)

            await session.commit()

            await interaction.response.send_message(
                f"Timezone set to {timezone}", ephemeral=True
            )


async def setup(bot: commands.Bot) -> None:
    """Load the cog."""
    await bot.add_cog(RemindersCog(bot))
