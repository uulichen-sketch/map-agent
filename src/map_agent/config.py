import os

from .exceptions import ConfigurationError


def get_api_key() -> str:
    api_key = os.environ.get("HUAWEI_MAP_API_KEY", "")
    if not api_key:
        raise ConfigurationError(
            "HUAWEI_MAP_API_KEY environment variable is not set. "
            "Get your API key from AppGallery Connect."
        )
    return api_key
