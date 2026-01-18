"""Branding service for lore-themed embeds."""

from typing import Any

import discord

from vezbot.models.branding import GuildBrand
from vezbot.utils.logging import get_logger

logger = get_logger(__name__)

# Tone presets mapping to icons and color adjustments
TONE_PRESETS = {
    "scroll": {"icon": "📜", "color_shift": 0},
    "codex": {"icon": "📖", "color_shift": -0.1},
    "dispatch": {"icon": "📬", "color_shift": 0.1},
    "decree": {"icon": "⚖️", "color_shift": -0.05},
}

# Microcopy templates by voice
MICROCOPY = {
    "formal": {
        "ticket_welcome": "Your inquiry has been received and will be addressed shortly.",
        "poll_closed": "This poll has concluded.",
        "setup_complete": "Configuration has been successfully applied.",
    },
    "casual": {
        "ticket_welcome": "Hey! We got your message and someone will help you soon.",
        "poll_closed": "Poll's done! Check out the results above.",
        "setup_complete": "All set! Your bot is ready to go.",
    },
    "mystic": {
        "ticket_welcome": "Your plea has been heard. The keepers shall respond in due time.",
        "poll_closed": "The oracle has spoken. The results are revealed.",
        "setup_complete": "The ancient rites are complete. The vessel is awakened.",
    },
}


def get_default_brand(guild_id: int) -> GuildBrand:
    """Get default brand configuration."""
    return GuildBrand(
        guild_id=guild_id,
        display_name="Vezbot",
        short_name="VZ",
        icon_url=None,
        primary_color=0x5865F2,
        accent_color=0x57F287,
        neutral_color=0x2F3136,
        footer_text=None,
        tagline=None,
        microcopy_voice="casual",
        embed_tone_preset="scroll",
    )


def build_lore_embed(
    brand: GuildBrand,
    tone: str | None = None,
    title: str | None = None,
    description: str | None = None,
    fields: list[dict[str, Any]] | None = None,
    footer: str | None = None,
    **kwargs: Any,
) -> discord.Embed:
    """
    Build a brand-aware lore embed.

    Args:
        brand: GuildBrand instance
        tone: Override tone preset (scroll, codex, dispatch, decree)
        title: Embed title
        description: Embed description
        fields: List of field dicts with 'name', 'value', 'inline' keys
        footer: Footer text (overrides brand.footer_text)
        **kwargs: Additional embed kwargs
    """
    tone = tone or brand.embed_tone_preset
    preset = TONE_PRESETS.get(tone, TONE_PRESETS["scroll"])

    # Adjust color based on tone
    base_color = brand.primary_color
    color_shift = preset["color_shift"]
    # Simple color adjustment (you can make this more sophisticated)
    adjusted_color = int(base_color * (1 + color_shift)) & 0xFFFFFF

    embed = discord.Embed(
        title=title,
        description=description,
        color=adjusted_color,
        **kwargs,
    )

    # Add icon to title if present
    if title and preset["icon"]:
        embed.title = f"{preset['icon']} {title}"

    # Add fields
    if fields:
        for field in fields:
            embed.add_field(
                name=field.get("name", ""),
                value=field.get("value", ""),
                inline=field.get("inline", False),
            )

    # Set footer
    footer_text = footer or brand.footer_text
    if footer_text:
        embed.set_footer(text=footer_text, icon_url=brand.icon_url)
    elif brand.icon_url:
        embed.set_footer(icon_url=brand.icon_url)

    return embed


def get_microcopy(brand: GuildBrand, key: str, context: dict[str, Any] | None = None) -> str:
    """
    Get brand-appropriate microcopy.

    Args:
        brand: GuildBrand instance
        key: Microcopy key (e.g., 'ticket_welcome')
        context: Optional context for templating
    """
    voice = brand.microcopy_voice
    templates = MICROCOPY.get(voice, MICROCOPY["casual"])
    text = templates.get(key, f"[{key}]")

    # Simple templating (you can enhance this)
    if context:
        for k, v in context.items():
            text = text.replace(f"{{{k}}}", str(v))

    return text
