"""Timezone conversion service."""

from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select

from vezbot.database import AsyncSessionLocal
from vezbot.models.users import UserProfile
from vezbot.repositories.guild_repo import GuildRepository
from vezbot.utils.logging import get_logger

logger = get_logger(__name__)


async def get_user_timezone(user_id: int, guild_id: int) -> str | None:
    """Get user's timezone preference."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(UserProfile).where(
                UserProfile.user_id == user_id, UserProfile.guild_id == guild_id
            )
        )
        profile = result.scalar_one_or_none()
        return profile.timezone if profile else None


async def get_guild_timezone(guild_id: int) -> str:
    """Get guild's default timezone."""
    async with AsyncSessionLocal() as session:
        guild_repo = GuildRepository(session)
        config = await guild_repo.get_by_guild_id(guild_id)
        if config and "default_timezone" in config.config_json:
            return config.config_json["default_timezone"]
    return "UTC"


def convert_to_timezone(dt: datetime, tz: str) -> datetime:
    """Convert datetime to timezone."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.astimezone(ZoneInfo(tz))


async def convert_to_user_tz(dt: datetime, user_id: int, guild_id: int) -> datetime:
    """Convert datetime to user's timezone."""
    tz = await get_user_timezone(user_id, guild_id)
    if not tz:
        tz = await get_guild_timezone(guild_id)
    return convert_to_timezone(dt, tz)


async def convert_to_guild_tz(dt: datetime, guild_id: int) -> datetime:
    """Convert datetime to guild's timezone."""
    tz = await get_guild_timezone(guild_id)
    return convert_to_timezone(dt, tz)
