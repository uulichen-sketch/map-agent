import os
from typing import Optional

from .exceptions import ConfigurationError


def get_api_key() -> str:
    api_key = os.environ.get("HUAWEI_MAP_API_KEY", "")
    if not api_key:
        raise ConfigurationError(
            "HUAWEI_MAP_API_KEY environment variable is not set. "
            "Get your API key from AppGallery Connect."
        )
    return api_key


class TransportConfig:
    """Transport configuration for MCP server.

    Supports three transport modes:
    - stdio: Standard input/output (default)
    - sse: Server-Sent Events over HTTP
    - streamable-http: Streamable HTTP for long-running operations

    Configuration is loaded from environment variables:
    - MAP_AGENT_TRANSPORT: Transport mode (default: stdio)
    - MAP_AGENT_HOST: Host for SSE/streamable-http (default: 0.0.0.0)
    - MAP_AGENT_PORT: Port for SSE/streamable-http (default: 8000)
    """
    mode: str = os.getenv("MAP_AGENT_TRANSPORT", "stdio")
    host: str = os.getenv("MAP_AGENT_HOST", "0.0.0.0")
    port: int = int(os.getenv("MAP_AGENT_PORT", "8000"))

    def validate(self) -> None:
        """Validate transport configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        valid_modes = ["stdio", "sse", "streamable-http"]
        if self.mode not in valid_modes:
            raise ValueError(f"Invalid transport mode '{self.mode}'. Must be one of: {valid_modes}")

        if self.port < 1 or self.port > 65535:
            raise ValueError(f"Invalid port '{self.port}'. Must be between 1 and 65535")

    @classmethod
    def from_env(cls) -> "TransportConfig":
        """Create TransportConfig from environment variables.

        Returns:
            TransportConfig instance loaded from environment
        """
        config = cls()
        config.validate()
        return config
