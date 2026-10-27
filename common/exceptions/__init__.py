from .config_error import ConfigError

# Define what gets exported when someone writes "from common.exceptions import *"
__all__ = ["ConfigError"]