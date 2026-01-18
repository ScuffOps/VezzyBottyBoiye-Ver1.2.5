"""Base integration class."""

from abc import ABC, abstractmethod
from typing import Any

from vezbot.models.integrations import IntegrationConfig


class Integration(ABC):
    """Base class for integrations."""

    def __init__(self, config: IntegrationConfig) -> None:
        self.config = config

    @abstractmethod
    async def setup(self) -> None:
        """Set up integration (e.g., subscribe to webhooks)."""
        pass

    @abstractmethod
    async def handle_webhook(self, payload: dict[str, Any]) -> None:
        """Handle incoming webhook."""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up integration (e.g., unsubscribe)."""
        pass
