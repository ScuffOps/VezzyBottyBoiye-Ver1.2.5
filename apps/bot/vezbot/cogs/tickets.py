"""Tickets cog."""

import discord
from discord import app_commands
from discord.ext import commands

from vezbot.database import AsyncSessionLocal
from vezbot.repositories.guild_repo import GuildRepository
from vezbot.services.branding_service import build_lore_embed, get_default_brand
from vezbot.services.ticket_service import TicketService
from vezbot.utils.logging import get_logger
from vezbot.utils.permissions import has_manage_guild

logger = get_logger(__name__)


class TicketPanelView(discord.ui.View):
    """Ticket panel with create buttons."""

    def __init__(self, cog: "TicketsCog") -> None:
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(
        label="Create Ticket", style=discord.ButtonStyle.primary, custom_id="ticket:create"
    )
    async def create_ticket(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        """Create a ticket."""
        if not interaction.guild:
            await interaction.response.send_message(
                "This can only be used in a server.", ephemeral=True
            )
            return

        # Open modal for basic ticket
        modal = TicketCreateModal(self.cog)
        await interaction.response.send_modal(modal)


class TicketCreateModal(discord.ui.Modal, title="Create Ticket"):
    """Modal for creating a ticket."""

    def __init__(self, cog: "TicketsCog") -> None:
        super().__init__()
        self.cog = cog

    subject = discord.ui.TextInput(
        label="Subject",
        placeholder="What do you need help with?",
        max_length=100,
        required=True,
    )

    description = discord.ui.TextInput(
        label="Description",
        placeholder="Please describe your issue or question...",
        style=discord.TextStyle.paragraph,
        max_length=1000,
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        """Handle modal submission."""
        await interaction.response.defer(ephemeral=True)

        if not interaction.guild:
            await interaction.followup.send(
                "This can only be used in a server.", ephemeral=True
            )
            return

        from vezbot.database import AsyncSessionLocal

        try:
            # Get config
            async with AsyncSessionLocal() as session:
                guild_repo = GuildRepository(session)
                config = await guild_repo.get_by_guild_id(interaction.guild.id)
                if not config or "ticket_hub_channel_id" not in config.config_json:
                    await interaction.followup.send(
                        "Server not configured. Please run `/setup` first.", ephemeral=True
                    )
                    return

                channel_id = config.config_json["ticket_hub_channel_id"]
                service = TicketService(session, interaction.client)
                ticket = await service.create_ticket(
                    guild_id=interaction.guild.id,
                    creator_id=interaction.user.id,
                    channel_id=channel_id,
                    form_data={
                        "subject": self.subject.value,
                        "description": self.description.value,
                    },
                )
                await session.commit()

                await interaction.followup.send(
                    f"Ticket created! Check your DMs or the ticket channel.", ephemeral=True
                )
        except Exception as e:
            logger.error(f"Failed to create ticket: {e}", guild_id=interaction.guild.id)
            await interaction.followup.send(
                f"Failed to create ticket: {str(e)}", ephemeral=True
            )


class TicketsCog(commands.Cog):
    """Tickets cog."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="ticket-panel", description="Create a ticket panel")
    @has_manage_guild()
    async def ticket_panel(self, interaction: discord.Interaction) -> None:
        """Create ticket panel message."""
        if not interaction.guild:
            await interaction.response.send_message(
                "This command can only be used in a server.", ephemeral=True
            )
            return

        from vezbot.repositories.guild_repo import GuildBrandRepository

        async with AsyncSessionLocal() as session:
            brand_repo = GuildBrandRepository(session)
            brand = await brand_repo.get_or_create(interaction.guild.id)

        embed = build_lore_embed(
            brand,
            title="Create a Ticket",
            description="Click the button below to create a support ticket.",
        )

        view = TicketPanelView(self)
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: commands.Bot) -> None:
    """Load the cog."""
    await bot.add_cog(TicketsCog(bot))
