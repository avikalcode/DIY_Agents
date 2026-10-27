from pathlib import Path
import os
import tomllib
from typing import Any

from common.exceptions import ConfigError


_MISSING = object()
ROOT = Path(__file__).resolve().parents[2]  # Locally: <project root>\logs 
                                            # In Docker: /app/logs
RESOURCE_DIR = Path(__file__).resolve().parents[1] / "config"/"resource" # Parent[0]-> Utility : Parent[1]-> Common 
ENVIRONMENTS = ("dev", "test", "prod")

# ------------------------------------------------------------------------------------
# get environment
def _resolve_environment()->str:
    env = os.getenv("APP_ENV","dev").strip().lower()
    
    if env not in ENVIRONMENTS:
        raise ConfigError(f"APP_ENV={env!r} is invalid; expected one of {', '.join(ENVIRONMENTS)}")

    return env

# ------------------------------------------------------------------------------------
# get the env file config.{env}.toml
def _get_env_file(environment: str=None) -> Path:
    resource_file_path = RESOURCE_DIR / f"config.{environment}.toml"
    return resource_file_path

# ------------------------------------------------------------------------------------
# load setting from file
def _load_settings(path:str):
    try:
        with open(path,"rb") as f:
            setting_data:dict[str,any]=tomllib.load(f)
    
    except FileNotFoundError:
        raise ConfigError(f"Config file not found: {path}") from None # from None syntax at the end of the raise statement is used to clean up Python's error logs by hiding the underlying "traceback chain".
    
    except tomllib.TOMLDecodeError:
        # Catches cases where the file contains corrupted text or invalid TOML syntax
        raise ConfigError(f"Config file at '{path}' is corrupted or contains invalid TOML syntax.") from None

    # Check if the dictionary is completely empty (file had no data)
    if not setting_data: # setting_data = {}. In Python, an empty dictionary evaluates to False
        raise ConfigError(f"Config file at '{path}' is empty; expected configuration parameters.")

    return setting_data

# ------------------------------------------------------------------------------------
# get the data from dictionay for particular key i.e setting_data["common"]["app_name"]
def _get_key_data(
    setting_data,           # raw dictionary configuration loaded from the file
    sections: tuple[str, ...],  # (a tuple containing nested section names drilling down section wise)
    key: str,                   #  key that would belong to last section in the tuple 
    default: Any = None
    ) -> Any:

    # 1. Start at the top of the loaded configuration file
    node: Any = setting_data                                    

    # 2. Safely drill down through the nested sections ("common", "sub_section", "deep_folder")) simply by continually reassigning node to the next level down until it arrives at the final target section.
    for section in sections:                                            # The loop runs once if path has one item ("common",).
        node = node.get(section, {}) if isinstance(node, dict) else {}  
    
    # 3. Look for the target key inside that final section
    file_value = node.get(key, _MISSING) if isinstance(node, dict) else _MISSING # eg Python looks inside the [common] section for the key "app_name".
                                                                                    # - If found, file_value becomes that value (e.g., "My Great App").
                                                                                    # - If missing, it tags it with a special marker called _MISSING.

    # 4. If found, return it. If missing, return your fallback value.
    return default if file_value is _MISSING else file_value

# ------------------------------------------------------------------------------------
def _absolute(p: str) -> Path:
    path = Path(p)
    return path.resolve() if path.is_absolute() else (ROOT / path).resolve()

# ------------------------------------------------------------------------------------
def _require(setting_data,path: tuple[str, ...], key: str) -> Any:
    value = _get_key_data(setting_data,path, key, _MISSING)
    
    if value is _MISSING:
        raise ConfigError(f"Missing setting [{'.'.join(path)}] {key} in {path}")
    return value