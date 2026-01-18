"""Ticket service."""

from datetime import datetime
from typing import Any

import discord
from sqlalchemy.ext.asyncio import AsyncSession

from vezbot.models.tickets import Ticket, TicketTranscript
from vezbot.repositories.guild_repo import GuildRepository
from vezbot.utils.logging import get_logger
from vezbot.utils.threads import create_ticket_thread

logger = get_logger(__name__)


class TicketService:
    """Service for ticket operations."""

    def __init__(self, session: AsyncSession, bot: discord.Client) -> None:
        self.session = session
        self.bot = bot

    async def create_ticket(
        self,
        guild_id: int,
        creator_id: int,
        channel_id: int,
        form_data: dict[str, Any] | None = None,
        form_template_id: int | None = None,
    ) -> Ticket:
        """
        Create a new ticket thread.

        Args:
            guild_id: Discord guild ID
            creator_id: Discord user ID of ticket creator
            channel_id: Ticket hub channel ID
            form_data: Optional form submission data
            form_template_id: Optional form template ID

        Returns:
            Created Ticket instance
        """
        guild = self.bot.get_guild(guild_id)
        if not guild:
            raise ValueError(f"Guild {guild_id} not found")

        channel = guild.get_channel(channel_id)
        if not isinstance(channel, discord.TextChannel):
            raise ValueError(f"Channel {channel_id} is not a text channel")

        creator = guild.get_member(creator_id)
        if not creator:
            raise ValueError(f"Creator {creator_id} not found in guild")

        # Get config
        guild_repo = GuildRepository(self.session)
        config = await guild_repo.get_by_guild_id(guild_id)
        if not config:
            raise ValueError("Guild not configured. Run /setup first.")

        # Create thread
        ticket_name = f"ticket-{creator.display_name}-{datetime.now().strftime('%Y%m%d')}"
        thread, is_private = await create_ticket_thread(
            channel, ticket_name, creator, self.bot, reason="Ticket creation"
        )

        # Create ticket record
        ticket = Ticket(
            guild_id=guild_id,
            channel_id=thread.id,
            thread_id=thread.id if not is_private else None,
            creator_id=creator_id,
            form_template_id=form_template_id,
            state="open",
            metadata_json=form_data,
        )
        self.session.add(ticket)
        await self.session.flush()

        # Create welcome message
        from vezbot.services.branding_service import build_lore_embed, get_default_brand
        from vezbot.repositories.guild_repo import GuildBrandRepository

        brand_repo = GuildBrandRepository(self.session)
        brand = await brand_repo.get_or_create(guild_id)

        embed = build_lore_embed(
            brand,
            title="Ticket Created",
            description=f"Welcome, {creator.mention}! A staff member will assist you shortly.",
        )

        if form_data:
            fields = []
            for key, value in form_data.items():
                fields.append({"name": key, "value": str(value)[:1024], "inline": False})
            embed.fields = [
                discord.EmbedField(name=f["name"], value=f["value"], inline=f.get("inline", False))
                for f in fields
            ]

        view = TicketControlView(ticket.id, self.bot)
        await thread.send(embed=embed, view=view)

        logger.info(
            "Ticket created",
            ticket_id=ticket.id,
            guild_id=guild_id,
            thread_id=thread.id,
            is_private=is_private,
        )

        return ticket

    async def update_state(
        self, ticket_id: int, state: str, staff_id: int | None = None
    ) -> Ticket:
        """Update ticket state."""
        ticket = await self.session.get(Ticket, ticket_id)
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found")

        ticket.state = state
        if state == "closed":
            ticket.closed_at = datetime.now()
            ticket.claimed_by_id = staff_id

        await self.session.flush()
        return ticket

    async def claim_ticket(self, ticket_id: int, staff_id: int) -> Ticket:
        """Claim a ticket."""
        ticket = await self.session.get(Ticket, ticket_id)
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found")

        ticket.claimed_by_id = staff_id
        await self.session.flush()
        return ticket


class TicketControlView(discord.ui.View):
    """Ticket control buttons."""

    def __init__(self, ticket_id: int, bot: discord.Client) -> None:
        super().__init__(timeout=None)
        self.ticket_id = ticket_id
        self.bot = bot

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.primary, custom_id="ticket:claim")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """Claim ticket."""
        from vezbot.database import AsyncSessionLocal
        from vezbot.services.ticket_service import TicketService

        async with AsyncSessionLocal() as session:
            service = TicketService(session, self.bot)
            try:
                ticket = await service.claim_ticket(self.ticket_id, interaction.user.id)
                await interaction.response.send_message(
                    f"Ticket claimed by {interaction.user.mention}", ephemeral=False
                )
            except Exception as e:
                await interaction.response.send_message(
                    f"Failed to claim ticket: {str(e)}", ephemeral=True
                )

    @discord.ui.button(label="Close", style=discord.ButtonStyle.danger, custom_id="ticket:close")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        """Close ticket."""
        from vezbot.database import AsyncSessionLocal
        from vezbot.services.ticket_service import TicketService

        async with AsyncSessionLocal() as session:
            service = TicketService(session, self.bot)
            try:
                ticket = await service.update_state(self.ticket_id, "closed", interaction.user.id)
                if isinstance(interaction.channel, discord.Thread):
                    await interaction.channel.edit(archived=True, locked=True)
                await interaction.response.send_message(
                    "Ticket closed and archived.", ephemeral=False
                )
            except Exception as e:
                await interaction.response.send_message(
                    f"Failed to close ticket: {str(e)}", ephemeral=True
                )
