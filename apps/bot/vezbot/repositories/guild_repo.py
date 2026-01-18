"""Guild repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from vezbot.models.branding import GuildBrand
from vezbot.models.config import GuildConfig
from vezbot.repositories.base import BaseRepository


class GuildRepository(BaseRepository[GuildConfig]):
    """Repository for guild configuration."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, GuildConfig)

    async def get_by_guild_id(self, guild_id: int) -> GuildConfig | None:
        """Get guild config by Discord guild ID."""
        result = await self.session.execute(
            select(GuildConfig).where(GuildConfig.id == guild_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, guild_id: int) -> GuildConfig:
        """Get or create guild config."""
        config = await self.get_by_guild_id(guild_id)
        if not config:
            config = await self.create(id=guild_id, config_json={})
        return config


class GuildBrandRepository(BaseRepository[GuildBrand]):
    """Repository for guild branding."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, GuildBrand)

    async def get_by_guild_id(self, guild_id: int) -> GuildBrand | None:
        """Get brand by Discord guild ID."""
        result = await self.session.execute(
            select(GuildBrand).where(GuildBrand.guild_id == guild_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, guild_id: int) -> GuildBrand:
        """Get or create brand config."""
        brand = await self.get_by_guild_id(guild_id)
        if not brand:
            from vezbot.services.branding_service import get_default_brand

            default = get_default_brand(guild_id)
            brand = await self.create(
                guild_id=guild_id,
                display_name=default.display_name,
                short_name=default.short_name,
                icon_url=default.icon_url,
                primary_color=default.primary_color,
                accent_color=default.accent_color,
                neutral_color=default.neutral_color,
                footer_text=default.footer_text,
                tagline=default.tagline,
                microcopy_voice=default.microcopy_voice,
                embed_tone_preset=default.embed_tone_preset,
            )
        return brand
