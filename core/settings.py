import json
import os
from pathlib import Path
from typing import Any
from dotenv import load_dotenv

class SettingsManager:
    def __init__(self, config_path: str = "config.json", env_path: str = ".env"):
        # Load environment variables from .env file
        load_dotenv(env_path)
        
        self.config_path = config_path
        self.settings = self._load_settings()

    def _load_settings(self) -> dict[str, Any]:
        settings = self._default_settings()
        
        # Override default with env vars if present
        if os.getenv("GOOGLE_API_KEY"):
            settings["api_key"] = os.getenv("GOOGLE_API_KEY")
            
        if os.getenv("MODELS"):
            models_str = os.getenv("MODELS")
            if models_str:
                settings["models"] = [m.strip() for m in models_str.split(",") if m.strip()]
            
        # Load config.json and merge/override
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    file_settings = json.load(f)
                    settings.update(file_settings)
            except Exception:
                pass # Just keep defaults/env
                
        return settings

    def _default_settings(self) -> dict[str, Any]:
        return {
            "api_key": "",
            "output_dir": "outputs",
            "models": [],
            "current_model": ""
        }

    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)

    def set(self, key: str, value: Any):
        self.settings[key] = value
        self.save()

    def save(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.settings, f, indent=4)
