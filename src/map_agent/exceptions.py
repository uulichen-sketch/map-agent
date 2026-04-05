class HMSMapError(Exception):
    """Base exception for HMS Map Kit operations."""


class ConfigurationError(HMSMapError):
    """Missing or invalid configuration."""


class HuaweiAPIError(HMSMapError):
    """Huawei API returned a non-zero returnCode."""

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"API error {code}: {message}")


class NetworkError(HMSMapError):
    """Network connectivity or timeout issue."""
