#!/usr/bin/env python3
"""
Configuration repository for abstracting configuration storage operations.

This module provides repository patterns for working with configuration data,
abstracting the underlying storage and access mechanisms.
"""

import abc
import yaml
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ConfigEntry:
    """Configuration entry with metadata."""

    key: str
    value: Any
    environment: Optional[str] = None
    component: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    source_file: Optional[str] = None


class ConfigRepository(abc.ABC):
    """
    Abstract repository for configuration storage operations.

    This interface defines the contract for configuration storage and retrieval
    operations, allowing different implementations for various storage backends.
    """

    @abc.abstractmethod
    def get_config(
        self,
        key: str,
        environment: Optional[str] = None,
        component: Optional[str] = None,
    ) -> Optional[Any]:
        """
        Get configuration value by key.

        Args:
            key: Configuration key
            environment: Optional environment filter
            component: Optional component filter

        Returns:
            Configuration value if found, None otherwise
        """
        pass

    @abc.abstractmethod
    def set_config(
        self,
        key: str,
        value: Any,
        environment: Optional[str] = None,
        component: Optional[str] = None,
    ) -> bool:
        """
        Set configuration value.

        Args:
            key: Configuration key
            value: Configuration value
            environment: Optional environment
            component: Optional component

        Returns:
            True if successful, False otherwise
        """
        pass

    @abc.abstractmethod
    def delete_config(
        self,
        key: str,
        environment: Optional[str] = None,
        component: Optional[str] = None,
    ) -> bool:
        """
        Delete configuration entry.

        Args:
            key: Configuration key to delete
            environment: Optional environment filter
            component: Optional component filter

        Returns:
            True if successful, False otherwise
        """
        pass

    @abc.abstractmethod
    def get_all_config(
        self, environment: Optional[str] = None, component: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get all configuration for environment/component.

        Args:
            environment: Optional environment filter
            component: Optional component filter

        Returns:
            Dictionary of configuration key-value pairs
        """
        pass

    @abc.abstractmethod
    def list_environments(self) -> List[str]:
        """
        Get list of available environments.

        Returns:
            List of environment names
        """
        pass

    @abc.abstractmethod
    def list_components(self, environment: Optional[str] = None) -> List[str]:
        """
        Get list of available components.

        Args:
            environment: Optional environment filter

        Returns:
            List of component names
        """
        pass

    @abc.abstractmethod
    def exists(
        self,
        key: str,
        environment: Optional[str] = None,
        component: Optional[str] = None,
    ) -> bool:
        """
        Check if configuration entry exists.

        Args:
            key: Configuration key
            environment: Optional environment filter
            component: Optional component filter

        Returns:
            True if entry exists, False otherwise
        """
        pass


class YamlConfigRepository(ConfigRepository):
    """
    YAML file-based implementation of the configuration repository.

    This implementation stores configuration in YAML files with support
    for environment-specific and component-specific configurations.
    """

    def __init__(self, config_directory: Union[str, Path]):
        """
        Initialize the YAML configuration repository.

        Args:
            config_directory: Directory containing configuration files
        """
        self.config_directory = Path(config_directory)
        self.config_directory.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

        # Cache for loaded configurations
        self._config_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamps: Dict[str, datetime] = {}

    def get_config(
        self,
        key: str,
        environment: Optional[str] = None,
        component: Optional[str] = None,
    ) -> Optional[Any]:
        """Get configuration value by key."""
        try:
            config_data = self._load_config(environment, component)

            # Support dot notation for nested keys
            keys = key.split(".")
            value = config_data

            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return None

            return value

        except Exception as e:
            self.logger.error(f"Error getting config {key}: {e}")
            return None

    def set_config(
        self,
        key: str,
        value: Any,
        environment: Optional[str] = None,
        component: Optional[str] = None,
    ) -> bool:
        """Set configuration value."""
        try:
            config_data = self._load_config(environment, component)

            # Support dot notation for nested keys
            keys = key.split(".")
            current = config_data

            # Navigate to the parent of the target key
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]

            # Set the value
            current[keys[-1]] = value

            # Save the configuration
            return self._save_config(config_data, environment, component)

        except Exception as e:
            self.logger.error(f"Error setting config {key}: {e}")
            return False

    def delete_config(
        self,
        key: str,
        environment: Optional[str] = None,
        component: Optional[str] = None,
    ) -> bool:
        """Delete configuration entry."""
        try:
            config_data = self._load_config(environment, component)

            # Support dot notation for nested keys
            keys = key.split(".")
            current = config_data

            # Navigate to the parent of the target key
            for k in keys[:-1]:
                if k not in current or not isinstance(current[k], dict):
                    return True  # Key doesn't exist, consider it deleted
                current = current[k]

            # Delete the key if it exists
            if keys[-1] in current:
                del current[keys[-1]]
                return self._save_config(config_data, environment, component)

            return True  # Key doesn't exist, consider it deleted

        except Exception as e:
            self.logger.error(f"Error deleting config {key}: {e}")
            return False

    def get_all_config(
        self, environment: Optional[str] = None, component: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get all configuration for environment/component."""
        try:
            return self._load_config(environment, component)
        except Exception as e:
            self.logger.error(f"Error getting all config: {e}")
            return {}

    def list_environments(self) -> List[str]:
        """Get list of available environments."""
        environments = set()

        try:
            for config_file in self.config_directory.glob("*.yaml"):
                filename = config_file.stem

                # Parse filename: {environment}.yaml or {component}_{environment}.yaml
                if "_" in filename:
                    parts = filename.split("_")
                    if len(parts) >= 2:
                        environments.add(parts[-1])  # Last part is environment
                else:
                    environments.add(filename)

        except Exception as e:
            self.logger.error(f"Error listing environments: {e}")

        return sorted(list(environments))

    def list_components(self, environment: Optional[str] = None) -> List[str]:
        """Get list of available components."""
        components = set()

        try:
            pattern = f"*_{environment}.yaml" if environment else "*.yaml"

            for config_file in self.config_directory.glob(pattern):
                filename = config_file.stem

                # Parse filename: {component}_{environment}.yaml
                if "_" in filename:
                    parts = filename.split("_")
                    if len(parts) >= 2:
                        component = "_".join(parts[:-1])  # All but last part
                        components.add(component)

        except Exception as e:
            self.logger.error(f"Error listing components: {e}")

        return sorted(list(components))

    def exists(
        self,
        key: str,
        environment: Optional[str] = None,
        component: Optional[str] = None,
    ) -> bool:
        """Check if configuration entry exists."""
        return self.get_config(key, environment, component) is not None

    def reload_config(
        self, environment: Optional[str] = None, component: Optional[str] = None
    ) -> bool:
        """
        Force reload configuration from disk.

        Args:
            environment: Optional environment to reload
            component: Optional component to reload

        Returns:
            True if successful, False otherwise
        """
        try:
            cache_key = self._get_cache_key(environment, component)

            # Remove from cache to force reload
            if cache_key in self._config_cache:
                del self._config_cache[cache_key]
            if cache_key in self._cache_timestamps:
                del self._cache_timestamps[cache_key]

            # Load fresh from disk
            self._load_config(environment, component)
            return True

        except Exception as e:
            self.logger.error(f"Error reloading config: {e}")
            return False

    def get_config_info(self) -> Dict[str, Any]:
        """
        Get information about the configuration repository.

        Returns:
            Dictionary with repository information
        """
        info = {
            "config_directory": str(self.config_directory),
            "total_files": 0,
            "environments": self.list_environments(),
            "components": self.list_components(),
            "cache_entries": len(self._config_cache),
        }

        try:
            config_files = list(self.config_directory.glob("*.yaml"))
            info["total_files"] = len(config_files)

            # File details
            info["files"] = []
            for config_file in config_files:
                file_info = {
                    "name": config_file.name,
                    "size": config_file.stat().st_size,
                    "modified": datetime.fromtimestamp(
                        config_file.stat().st_mtime
                    ).isoformat(),
                }
                info["files"].append(file_info)

        except Exception as e:
            self.logger.error(f"Error getting config info: {e}")

        return info

    def _load_config(
        self, environment: Optional[str] = None, component: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Load configuration from file with caching.

        Args:
            environment: Optional environment
            component: Optional component

        Returns:
            Configuration dictionary
        """
        cache_key = self._get_cache_key(environment, component)
        config_file = self._get_config_file_path(environment, component)

        # Check if file exists
        if not config_file.exists():
            return {}

        # Check cache validity
        file_mtime = datetime.fromtimestamp(config_file.stat().st_mtime)

        if (
            cache_key in self._config_cache
            and cache_key in self._cache_timestamps
            and self._cache_timestamps[cache_key] >= file_mtime
        ):
            return self._config_cache[cache_key]

        # Load from file
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f) or {}

            # Update cache
            self._config_cache[cache_key] = config_data
            self._cache_timestamps[cache_key] = file_mtime

            return config_data

        except Exception as e:
            self.logger.error(f"Error loading config file {config_file}: {e}")
            return {}

    def _save_config(
        self,
        config_data: Dict[str, Any],
        environment: Optional[str] = None,
        component: Optional[str] = None,
    ) -> bool:
        """
        Save configuration to file.

        Args:
            config_data: Configuration data to save
            environment: Optional environment
            component: Optional component

        Returns:
            True if successful, False otherwise
        """
        try:
            config_file = self._get_config_file_path(environment, component)
            config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(config_file, "w", encoding="utf-8") as f:
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)

            # Update cache
            cache_key = self._get_cache_key(environment, component)
            self._config_cache[cache_key] = config_data
            self._cache_timestamps[cache_key] = datetime.now()

            self.logger.info(f"Saved configuration to {config_file}")
            return True

        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
            return False

    def _get_config_file_path(
        self, environment: Optional[str] = None, component: Optional[str] = None
    ) -> Path:
        """
        Get the file path for configuration storage.

        Args:
            environment: Optional environment
            component: Optional component

        Returns:
            Path to configuration file
        """
        if component and environment:
            filename = f"{component}_{environment}.yaml"
        elif environment:
            filename = f"{environment}.yaml"
        elif component:
            filename = f"{component}.yaml"
        else:
            filename = "default.yaml"

        return self.config_directory / filename

    def _get_cache_key(
        self, environment: Optional[str] = None, component: Optional[str] = None
    ) -> str:
        """
        Get cache key for configuration.

        Args:
            environment: Optional environment
            component: Optional component

        Returns:
            Cache key string
        """
        parts = []
        if component:
            parts.append(component)
        if environment:
            parts.append(environment)

        return "_".join(parts) if parts else "default"
