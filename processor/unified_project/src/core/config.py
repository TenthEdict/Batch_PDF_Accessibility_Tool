#!/usr/bin/env python3
"""
Configuration management module.

This module provides a unified configuration system for the application,
supporting environment-specific settings, configuration overrides,
and configuration validation.
"""

import os
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from .interfaces import ConfigurationProvider

logger = logging.getLogger(__name__)


class YamlConfigurationProvider(ConfigurationProvider):
    """
    YAML-based configuration provider implementation.

    This provider loads configuration from YAML files and supports
    environment-specific overrides.
    """

    def __init__(self, config_dir: str = "config"):
        """
        Initialize the configuration provider.

        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self.configs: Dict[str, Dict[str, Any]] = {}
        self.env_configs: Dict[str, Dict[str, Dict[str, Any]]] = {}

        # Load default config
        self._load_default_config()

    def _load_default_config(self) -> None:
        """
        Load the default configuration.

        This method loads the default.yaml configuration file and any
        environment-specific configuration files.
        """
        default_config_path = self.config_dir / "default.yaml"

        if not default_config_path.exists():
            logger.warning(
                f"Default configuration file not found: {default_config_path}"
            )
            return

        try:
            with open(default_config_path, "r") as f:
                config = yaml.safe_load(f)

                if not isinstance(config, dict):
                    logger.error("Default configuration is not a dictionary")
                    return

                # Extract component configurations
                for component, settings in config.items():
                    if not isinstance(settings, dict):
                        continue

                    self.configs[component] = settings

            logger.info(f"Loaded default configuration from {default_config_path}")
        except Exception as e:
            logger.error(f"Error loading default configuration: {e}")

    def _load_environment_config(self, environment: str) -> None:
        """
        Load environment-specific configuration.

        Args:
            environment: Environment name
        """
        if environment in self.env_configs:
            # Already loaded
            return

        env_config_path = self.config_dir / f"{environment}.yaml"

        if not env_config_path.exists():
            logger.warning(
                f"Environment configuration file not found: {env_config_path}"
            )
            self.env_configs[environment] = {}
            return

        try:
            with open(env_config_path, "r") as f:
                config = yaml.safe_load(f)

                if not isinstance(config, dict):
                    logger.error(
                        f"Environment configuration is not a dictionary: {environment}"
                    )
                    self.env_configs[environment] = {}
                    return

                # Extract component configurations
                env_configs = {}
                for component, settings in config.items():
                    if not isinstance(settings, dict):
                        continue

                    env_configs[component] = settings

                self.env_configs[environment] = env_configs

            logger.info(f"Loaded {environment} configuration from {env_config_path}")
        except Exception as e:
            logger.error(f"Error loading {environment} configuration: {e}")
            self.env_configs[environment] = {}

    def get_config(
        self, component: str, environment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get configuration for a specific component.

        Args:
            component: Component identifier
            environment: Optional environment name

        Returns:
            Dict[str, Any]: Configuration settings
        """
        # Get default configuration
        config = self.configs.get(component, {}).copy()

        # Apply environment-specific overrides if specified
        if environment:
            # Load environment config if not already loaded
            if environment not in self.env_configs:
                self._load_environment_config(environment)

            # Apply environment overrides
            env_config = self.env_configs.get(environment, {}).get(component, {})
            config.update(env_config)

        return config

    def set_config(
        self,
        component: str,
        settings: Dict[str, Any],
        environment: Optional[str] = None,
    ) -> bool:
        """
        Set configuration for a specific component.

        Args:
            component: Component identifier
            settings: Configuration settings to set
            environment: Optional environment name

        Returns:
            bool: True if configuration was set successfully, False otherwise
        """
        if environment:
            # Load environment config if not already loaded
            if environment not in self.env_configs:
                self._load_environment_config(environment)

            # Set environment-specific configuration
            if environment not in self.env_configs:
                self.env_configs[environment] = {}

            if component not in self.env_configs[environment]:
                self.env_configs[environment][component] = {}

            self.env_configs[environment][component].update(settings)

            # Save environment configuration
            env_config_path = self.config_dir / f"{environment}.yaml"

            try:
                with open(env_config_path, "w") as f:
                    yaml.dump(
                        self.env_configs[environment], f, default_flow_style=False
                    )

                logger.info(f"Saved {environment} configuration to {env_config_path}")
                return True
            except Exception as e:
                logger.error(f"Error saving {environment} configuration: {e}")
                return False
        else:
            # Set default configuration
            if component not in self.configs:
                self.configs[component] = {}

            self.configs[component].update(settings)

            # Save default configuration
            default_config_path = self.config_dir / "default.yaml"

            try:
                with open(default_config_path, "w") as f:
                    yaml.dump(self.configs, f, default_flow_style=False)

                logger.info(f"Saved default configuration to {default_config_path}")
                return True
            except Exception as e:
                logger.error(f"Error saving default configuration: {e}")
                return False


# Create a singleton configuration provider
config_path = Path(__file__).parent.parent.parent / "config"
config_provider = YamlConfigurationProvider(config_dir=config_path.resolve())


def get_config_provider() -> ConfigurationProvider:
    """
    Get the global configuration provider instance.

    Returns:
        ConfigurationProvider: Global configuration provider instance
    """
    return config_provider
