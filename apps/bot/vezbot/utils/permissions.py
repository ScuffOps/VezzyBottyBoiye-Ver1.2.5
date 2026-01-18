"""Permission checking utilities."""

from typing import TYPE_CHECKING

import discord
from discord import app_commands

if TYPE_CHECKING:
    from vezbot.bot import Vezbot


def is_admin() -> app_commands.check:
    """Check if user has administrator permission."""

    async def predicate(interaction: discord.Interaction) -> bool:
        if not interaction.guild:
            return False
        if interaction.user.guild_permissions.administrator:
            return True
        return False

    return app_commands.check(predicate)


def has_manage_guild() -> app_commands.check:
    """Check if user has manage guild permission."""

    async def predicate(interaction: discord.Interaction) -> bool:
        if not interaction.guild:
            return False
        if interaction.user.guild_permissions.manage_guild:
            return True
        return False

    return app_commands.check(predicate)


async def can_manage_threads(channel: discord.TextChannel, bot: "Vezbot") -> bool:
    """Check if bot can manage threads in channel."""
    if not channel:
        return False

    me = channel.guild.get_member(bot.user.id) if bot.user else None
    if not me:
        return False

    perms = channel.permissions_for(me)
    return perms.manage_threads and perms.send_messages


async def can_create_private_threads(channel: discord.TextChannel, bot: "Vezbot") -> bool:
    """Check if private threads are available in channel."""
    if not channel:
        return False

    # Check guild feature
    if not channel.guild.features.private_threads:
        return False

    # Check bot permissions
    me = channel.guild.get_member(bot.user.id) if bot.user else None
    if not me:
        return False

    perms = channel.permissions_for(me)
    return perms.manage_threads and perms.create_private_threads
