#!/usr/bin/env python3
"""
Configuration loaders for different file formats.

This module provides abstract and concrete implementations of configuration
loaders that can read and write configuration files in various formats.
"""

import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Union

import yaml

logger = logging.getLogger(__name__)


class ConfigLoader(ABC):
    """Abstract base class for configuration loaders."""

    @abstractmethod
    def load_config(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load configuration from a file.

        Args:
            file_path: Path to configuration file

        Returns:
            Loaded configuration dictionary

        Raises:
            ConfigurationError: If file cannot be loaded
        """
        pass

    @abstractmethod
    def save_config(self, config: Dict[str, Any], file_path: Union[str, Path]) -> bool:
        """
        Save configuration to a file.

        Args:
            config: Configuration dictionary to save
            file_path: Path to save configuration

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def get_supported_extensions(self) -> list[str]:
        """
        Get list of supported file extensions.

        Returns:
            List of supported extensions (with dots)
        """
        pass


class YamlConfigLoader(ConfigLoader):
    """YAML configuration file loader."""

    def load_config(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        file_path = Path(file_path)

        try:
            if not file_path.exists():
                logger.warning(f"Configuration file not found: {file_path}")
                return {}

            with open(file_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            # Handle empty files
            if config is None:
                config = {}

            logger.debug(f"Loaded YAML configuration from {file_path}")
            return config

        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file {file_path}: {e}")
            raise ConfigurationError(f"Invalid YAML in {file_path}: {e}")

        except Exception as e:
            logger.error(f"Error loading configuration from {file_path}: {e}")
            raise ConfigurationError(f"Failed to load {file_path}: {e}")

    def save_config(self, config: Dict[str, Any], file_path: Union[str, Path]) -> bool:
        """Save configuration to YAML file."""
        file_path = Path(file_path)

        try:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    config,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=True,
                    indent=2,
                )

            logger.info(f"Saved YAML configuration to {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving configuration to {file_path}: {e}")
            return False

    def get_supported_extensions(self) -> list[str]:
        """Get supported YAML extensions."""
        return [".yaml", ".yml"]


class JsonConfigLoader(ConfigLoader):
    """JSON configuration file loader."""

    def __init__(self, indent: int = 2):
        """
        Initialize JSON loader.

        Args:
            indent: JSON indentation for pretty printing
        """
        self.indent = indent

    def load_config(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        file_path = Path(file_path)

        try:
            if not file_path.exists():
                logger.warning(f"Configuration file not found: {file_path}")
                return {}

            with open(file_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            logger.debug(f"Loaded JSON configuration from {file_path}")
            return config

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON file {file_path}: {e}")
            raise ConfigurationError(f"Invalid JSON in {file_path}: {e}")

        except Exception as e:
            logger.error(f"Error loading configuration from {file_path}: {e}")
            raise ConfigurationError(f"Failed to load {file_path}: {e}")

    def save_config(self, config: Dict[str, Any], file_path: Union[str, Path]) -> bool:
        """Save configuration to JSON file."""
        file_path = Path(file_path)

        try:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(
                    config, f, indent=self.indent, ensure_ascii=False, sort_keys=True
                )

            logger.info(f"Saved JSON configuration to {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving configuration to {file_path}: {e}")
            return False

    def get_supported_extensions(self) -> list[str]:
        """Get supported JSON extensions."""
        return [".json"]


class MultiFormatConfigLoader(ConfigLoader):
    """Configuration loader that supports multiple formats."""

    def __init__(self):
        """Initialize multi-format loader with default loaders."""
        self.loaders = {
            ".yaml": YamlConfigLoader(),
            ".yml": YamlConfigLoader(),
            ".json": JsonConfigLoader(),
        }

    def add_loader(self, extension: str, loader: ConfigLoader) -> None:
        """
        Add a custom loader for a file extension.

        Args:
            extension: File extension (with dot)
            loader: ConfigLoader instance
        """
        self.loaders[extension] = loader

    def load_config(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Load configuration using appropriate loader based on extension."""
        file_path = Path(file_path)
        extension = file_path.suffix.lower()

        if extension not in self.loaders:
            raise ConfigurationError(f"Unsupported file format: {extension}")

        return self.loaders[extension].load_config(file_path)

    def save_config(self, config: Dict[str, Any], file_path: Union[str, Path]) -> bool:
        """Save configuration using appropriate loader based on extension."""
        file_path = Path(file_path)
        extension = file_path.suffix.lower()

        if extension not in self.loaders:
            logger.error(f"Unsupported file format for saving: {extension}")
            return False

        return self.loaders[extension].save_config(config, file_path)

    def get_supported_extensions(self) -> list[str]:
        """Get all supported extensions."""
        return list(self.loaders.keys())


# Import ConfigurationError from config_manager to avoid circular import
try:
    from .config_manager import ConfigurationError
except ImportError:

    class ConfigurationError(Exception):
        """Fallback exception for configuration errors."""

        pass
