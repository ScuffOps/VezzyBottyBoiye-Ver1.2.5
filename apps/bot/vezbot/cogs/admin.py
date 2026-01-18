"""Admin utilities cog."""

import discord
from discord import app_commands
from discord.ext import commands

from vezbot.utils.logging import get_logger
from vezbot.utils.permissions import is_admin

logger = get_logger(__name__)


class AdminCog(commands.Cog):
    """Admin utilities cog."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction) -> None:
        """Check bot latency."""
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong! {latency}ms", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    """Load the cog."""
    await bot.add_cog(AdminCog(bot))
