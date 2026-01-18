"""Polls cog."""

from datetime import datetime
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands

from vezbot.database import AsyncSessionLocal
from vezbot.models.polls import Poll, PollVote
from vezbot.repositories.guild_repo import GuildBrandRepository
from vezbot.services.branding_service import build_lore_embed
from vezbot.services.timezone_service import convert_to_user_tz, get_user_timezone
from vezbot.utils.logging import get_logger
from vezbot.utils.permissions import has_manage_guild

logger = get_logger(__name__)


class PollView(discord.ui.View):
    """Poll voting view."""

    def __init__(self, poll_id: int, options: list[dict], poll_type: str, bot: commands.Bot) -> None:
        super().__init__(timeout=None)
        self.poll_id = poll_id
        self.options = options
        self.poll_type = poll_type
        self.bot = bot

        # Add buttons for each option (max 5 for buttons, use select menu if more)
        if len(options) <= 5:
            for i, option in enumerate(options):
                button = discord.ui.Button(
                    label=option.get("label", f"Option {i+1}"),
                    emoji=option.get("emoji"),
                    custom_id=f"poll:{poll_id}:{i}",
                )
                button.callback = self.create_vote_callback(i)
                self.add_item(button)
        else:
            # Use select menu for >5 options
            select = discord.ui.Select(
                placeholder="Select option(s)...",
                custom_id=f"poll:{poll_id}:select",
                min_values=1,
                max_values=1 if poll_type == "single" else len(options),
            )
            for i, option in enumerate(options):
                select.add_option(
                    label=option.get("label", f"Option {i+1}"),
                    value=str(i),
                    emoji=option.get("emoji"),
                )
            select.callback = self.select_callback
            self.add_item(select)

    def create_vote_callback(self, option_index: int):
        """Create vote callback for button."""

        async def callback(interaction: discord.Interaction) -> None:
            await self.handle_vote(interaction, [option_index])

        return callback

    async def select_callback(self, interaction: discord.Interaction) -> None:
        """Handle select menu vote."""
        select = interaction.data.get("values", [])
        option_indices = [int(v) for v in select]
        await self.handle_vote(interaction, option_indices)

    async def handle_vote(self, interaction: discord.Interaction, option_indices: list[int]) -> None:
        """Handle vote submission."""
        from vezbot.database import AsyncSessionLocal
        from vezbot.models.polls import PollVote

        await interaction.response.defer(ephemeral=True)

        async with AsyncSessionLocal() as session:
            # Check if already voted
            result = await session.execute(
                select(PollVote).where(
                    PollVote.poll_id == self.poll_id, PollVote.user_id == interaction.user.id
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                # Update vote
                existing.option_indices = option_indices
            else:
                # Create new vote
                vote = PollVote(
                    poll_id=self.poll_id,
                    user_id=interaction.user.id,
                    option_indices=option_indices,
                )
                session.add(vote)

            await session.commit()

            # Update poll message
            await self.update_poll_message(interaction)

            await interaction.followup.send("Vote recorded!", ephemeral=True)

    async def update_poll_message(self, interaction: discord.Interaction) -> None:
        """Update poll message with current results."""
        async with AsyncSessionLocal() as session:
            poll = await session.get(Poll, self.poll_id)
            if not poll:
                return

            # Get all votes
            result = await session.execute(
                select(PollVote).where(PollVote.poll_id == self.poll_id)
            )
            votes = result.scalars().all()

            # Count votes
            counts = [0] * len(self.options)
            for vote in votes:
                for idx in vote.option_indices:
                    if 0 <= idx < len(counts):
                        counts[idx] += 1

            total_votes = sum(counts)

            # Build results embed
            from vezbot.repositories.guild_repo import GuildBrandRepository

            brand_repo = GuildBrandRepository(session)
            brand = await brand_repo.get_or_create(interaction.guild.id)

            fields = []
            for i, option in enumerate(self.options):
                count = counts[i]
                percentage = (count / total_votes * 100) if total_votes > 0 else 0
                bar = "█" * int(percentage / 5)  # Simple bar
                fields.append(
                    {
                        "name": f"{option.get('emoji', '')} {option.get('label', f'Option {i+1}')}",
                        "value": f"{bar} {count} ({percentage:.1f}%)",
                        "inline": False,
                    }
                )

            embed = build_lore_embed(
                brand,
                title=poll.question,
                description=f"Total votes: {total_votes}",
                fields=fields,
            )

            if poll.closes_at:
                embed.set_footer(text=f"Closes at {poll.closes_at.strftime('%Y-%m-%d %H:%M UTC')}")

            try:
                channel = interaction.guild.get_channel(poll.channel_id)
                if channel:
                    message = await channel.fetch_message(poll.message_id)
                    await message.edit(embed=embed, view=self)
            except Exception as e:
                logger.error(f"Failed to update poll message: {e}")


class PollsCog(commands.Cog):
    """Polls cog."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="poll-create", description="Create a poll")
    @has_manage_guild()
    @app_commands.describe(
        question="Poll question",
        options="Options separated by | (e.g., 'Option 1|Option 2|Option 3')",
        type="Poll type",
        channel="Channel to post in (defaults to current channel)",
        closes_at="When to close (ISO format, optional)",
    )
    async def poll_create(
        self,
        interaction: discord.Interaction,
        question: str,
        options: str,
        type: Literal["single", "multi"] = "single",
        channel: discord.TextChannel | None = None,
        closes_at: str | None = None,
    ) -> None:
        """Create a poll."""
        if not interaction.guild:
            await interaction.response.send_message(
                "This command can only be used in a server.", ephemeral=True
            )
            return

        target_channel = channel or interaction.channel
        if not isinstance(target_channel, discord.TextChannel):
            await interaction.response.send_message("Invalid channel.", ephemeral=True)
            return

        # Parse options
        option_list = [opt.strip() for opt in options.split("|")]
        if len(option_list) < 2:
            await interaction.response.send_message(
                "Please provide at least 2 options.", ephemeral=True
            )
            return

        # Parse closes_at if provided
        closes_dt = None
        if closes_at:
            try:
                # Try parsing ISO format
                closes_dt = datetime.fromisoformat(closes_at.replace("Z", "+00:00"))
                # Convert to user's timezone for display
                closes_dt = await convert_to_user_tz(
                    closes_dt, interaction.user.id, interaction.guild.id
                )
            except Exception as e:
                await interaction.response.send_message(
                    f"Invalid date format: {str(e)}", ephemeral=True
                )
                return

        # Build options with emojis
        option_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        option_objs = [
            {"label": opt, "emoji": option_emojis[i] if i < len(option_emojis) else None, "index": i}
            for i, opt in enumerate(option_list)
        ]

        from vezbot.database import AsyncSessionLocal

        async with AsyncSessionLocal() as session:
            brand_repo = GuildBrandRepository(session)
            brand = await brand_repo.get_or_create(interaction.guild.id)

            # Create initial embed
            fields = [
                {
                    "name": f"{opt.get('emoji', '')} {opt.get('label', '')}",
                    "value": "0 votes (0%)",
                    "inline": False,
                }
                for opt in option_objs
            ]

            embed = build_lore_embed(
                brand,
                title=question,
                description="Click an option to vote!",
                fields=fields,
            )

            view = PollView(0, option_objs, type, self.bot)  # Will update poll_id after creation

            # Send message
            message = await target_channel.send(embed=embed, view=view)

            # Create poll record
            from vezbot.models.polls import Poll

            poll = Poll(
                guild_id=interaction.guild.id,
                channel_id=target_channel.id,
                message_id=message.id,
                creator_id=interaction.user.id,
                question=question,
                options_json=option_objs,
                type=type,
                closes_at=closes_dt,
            )
            session.add(poll)
            await session.flush()

            # Update view with poll_id
            view.poll_id = poll.id
            for item in view.children:
                if hasattr(item, "custom_id"):
                    item.custom_id = item.custom_id.replace("poll:0:", f"poll:{poll.id}:")

            await session.commit()

            # Update message with correct view
            await message.edit(view=view)

            await interaction.response.send_message(
                f"Poll created in {target_channel.mention}!", ephemeral=True
            )


async def setup(bot: commands.Bot) -> None:
    """Load the cog."""
    await bot.add_cog(PollsCog(bot))
