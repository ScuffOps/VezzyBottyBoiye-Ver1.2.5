"""Twitch EventSub integration."""

import hashlib
import hmac
import json
from typing import Any

import httpx

from vezbot.config import settings
from vezbot.database import AsyncSessionLocal
from vezbot.integrations.base import Integration
from vezbot.models.integrations import IntegrationConfig
from vezbot.repositories.guild_repo import GuildBrandRepository
from vezbot.services.branding_service import build_lore_embed
from vezbot.utils.logging import get_logger

logger = get_logger(__name__)


class TwitchIntegration(Integration):
    """Twitch EventSub integration."""

    def __init__(self, config: IntegrationConfig) -> None:
        super().__init__(config)
        self.client_id = settings.twitch_client_id
        self.client_secret = settings.twitch_client_secret
        self.app_token: str | None = None

    async def get_app_token(self) -> str:
        """Get Twitch app access token."""
        if self.app_token:
            return self.app_token

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://id.twitch.tv/oauth2/token",
                params={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "client_credentials",
                },
            )
            response.raise_for_status()
            data = response.json()
            self.app_token = data["access_token"]
            return self.app_token

    async def setup(self) -> None:
        """Subscribe to stream.online event."""
        if not self.client_id or not self.client_secret:
            logger.warning("Twitch credentials not configured")
            return

        token = await self.get_app_token()
        user_id = self.config.config_json.get("user_id")
        if not user_id:
            logger.warning("Twitch user_id not configured")
            return

        webhook_url = f"{settings.base_url}/webhooks/twitch"
        webhook_secret = self.config.webhook_secret or "default_secret"

        async with httpx.AsyncClient() as client:
            headers = {
                "Client-Id": self.client_id,
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
            payload = {
                "type": "stream.online",
                "version": "1",
                "condition": {"broadcaster_user_id": user_id},
                "transport": {
                    "method": "webhook",
                    "callback": webhook_url,
                    "secret": webhook_secret,
                },
            }

            try:
                response = await client.post(
                    "https://api.twitch.tv/helix/eventsub/subscriptions",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                subscription_id = data["data"][0]["id"]
                self.config.config_json["subscription_id"] = subscription_id
                logger.info(f"Twitch subscription created: {subscription_id}")
            except Exception as e:
                logger.error(f"Failed to create Twitch subscription: {e}")

    async def handle_webhook(self, payload: dict[str, Any]) -> None:
        """Handle Twitch webhook."""
        # Verify signature
        signature = payload.get("headers", {}).get("twitch-eventsub-message-signature")
        if not self.verify_signature(payload.get("body", ""), signature):
            logger.warning("Invalid Twitch webhook signature")
            return

        body = json.loads(payload.get("body", "{}"))
        notification = body.get("subscription", {})
        event = body.get("event", {})

        if notification.get("type") == "stream.online":
            await self.handle_stream_online(event)

    def verify_signature(self, body: str, signature: str | None) -> bool:
        """Verify Twitch webhook signature."""
        if not signature or not self.config.webhook_secret:
            return False

        expected = hmac.new(
            self.config.webhook_secret.encode(),
            body.encode(),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(f"sha256={expected}", signature)

    async def handle_stream_online(self, event: dict[str, Any]) -> None:
        """Handle stream.online event."""
        broadcaster_name = event.get("broadcaster_user_name", "Unknown")
        title = event.get("title", "Untitled Stream")
        game_name = event.get("game_name", "Just Chatting")

        # Get all guilds with Twitch enabled
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select

            result = await session.execute(
                select(IntegrationConfig).where(
                    IntegrationConfig.provider == "twitch",
                    IntegrationConfig.enabled == True,
                )
            )
            configs = result.scalars().all()

            for config in configs:
                channel_id = config.config_json.get("channel_id")
                if not channel_id:
                    continue

                # Get guild and channel
                import discord
                from vezbot.bot import bot

                guild = bot.get_guild(config.guild_id)
                if not guild:
                    continue

                channel = guild.get_channel(channel_id)
                if not isinstance(channel, discord.TextChannel):
                    continue

                # Build notification embed
                brand_repo = GuildBrandRepository(session)
                brand = await brand_repo.get_or_create(config.guild_id)

                embed = build_lore_embed(
                    brand,
                    title=f"{broadcaster_name} is now live!",
                    description=title,
                    fields=[
                        {"name": "Game", "value": game_name, "inline": True},
                        {
                            "name": "Watch",
                            "value": f"https://twitch.tv/{broadcaster_name}",
                            "inline": True,
                        },
                    ],
                )

                await channel.send(embed=embed)
                logger.info(
                    f"Sent Twitch notification to {channel.id}",
                    guild_id=config.guild_id,
                )

    async def cleanup(self) -> None:
        """Unsubscribe from events."""
        subscription_id = self.config.config_json.get("subscription_id")
        if not subscription_id:
            return

        token = await self.get_app_token()
        async with httpx.AsyncClient() as client:
            headers = {
                "Client-Id": self.client_id,
                "Authorization": f"Bearer {token}",
            }
            try:
                response = await client.delete(
                    f"https://api.twitch.tv/helix/eventsub/subscriptions?id={subscription_id}",
                    headers=headers,
                )
                response.raise_for_status()
                logger.info(f"Twitch subscription deleted: {subscription_id}")
            except Exception as e:
                logger.error(f"Failed to delete Twitch subscription: {e}")
