"""Embeds/Webhooks cog."""

import json
from typing import Any

import discord
from discord import app_commands
from discord.ext import commands

from vezbot.database import AsyncSessionLocal
from vezbot.models.embeds import EmbedTemplate
from vezbot.repositories.guild_repo import GuildBrandRepository
from vezbot.services.branding_service import build_lore_embed
from vezbot.utils.logging import get_logger
from vezbot.utils.permissions import has_manage_guild

logger = get_logger(__name__)


class EmbedsCog(commands.Cog):
    """Embeds/Webhooks cog."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="embed-create", description="Create and post an embed")
    @has_manage_guild()
    @app_commands.describe(
        title="Embed title",
        description="Embed description",
        channel="Channel to post in (defaults to current channel)",
    )
    async def embed_create(
        self,
        interaction: discord.Interaction,
        title: str,
        description: str,
        channel: discord.TextChannel | None = None,
    ) -> None:
        """Create and post an embed."""
        if not interaction.guild:
            await interaction.response.send_message(
                "This command can only be used in a server.", ephemeral=True
            )
            return

        target_channel = channel or interaction.channel
        if not isinstance(target_channel, discord.TextChannel):
            await interaction.response.send_message(
                "Invalid channel.", ephemeral=True
            )
            return

        from vezbot.database import AsyncSessionLocal

        async with AsyncSessionLocal() as session:
            brand_repo = GuildBrandRepository(session)
            brand = await brand_repo.get_or_create(interaction.guild.id)

        embed = build_lore_embed(
            brand,
            title=title,
            description=description,
        )

        await target_channel.send(embed=embed)
        await interaction.response.send_message(
            f"Embed posted in {target_channel.mention}", ephemeral=True
        )

    @app_commands.command(name="embed-save", description="Save an embed template")
    @has_manage_guild()
    @app_commands.describe(
        name="Template name",
        title="Embed title",
        description="Embed description",
    )
    async def embed_save(
        self,
        interaction: discord.Interaction,
        name: str,
        title: str,
        description: str,
    ) -> None:
        """Save an embed template."""
        if not interaction.guild:
            await interaction.response.send_message(
                "This command can only be used in a server.", ephemeral=True
            )
            return

        async with AsyncSessionLocal() as session:
            brand_repo = GuildBrandRepository(session)
            brand = await brand_repo.get_or_create(interaction.guild.id)

            # Build embed to get JSON structure
            embed = build_lore_embed(brand, title=title, description=description)
            embed_dict = embed.to_dict()

            from vezbot.models.embeds import EmbedTemplate

            template = EmbedTemplate(
                guild_id=interaction.guild.id,
                name=name,
                embed_json=embed_dict,
            )
            session.add(template)
            await session.commit()

            await interaction.response.send_message(
                f"Template '{name}' saved!", ephemeral=True
            )


async def setup(bot: commands.Bot) -> None:
    """Load the cog."""
    await bot.add_cog(EmbedsCog(bot))
