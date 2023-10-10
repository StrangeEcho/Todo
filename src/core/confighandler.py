import tomllib
from typing import Any, Optional


class ConfigHandler:
    """Parses config from the config.toml file"""

    with open("./src/core/data/config.toml", "rb") as confile:
        config: dict[Any, Any] = tomllib.load(confile)

    def get(self, config_name: str, *, category: Optional[str] = None) -> Optional[Any]:
        """Fetch the specified config from the config.toml file"""
        if category:
            try:
                return self.config[category][config_name]
            except KeyError:
                return None
        return self.config.get(config_name)
