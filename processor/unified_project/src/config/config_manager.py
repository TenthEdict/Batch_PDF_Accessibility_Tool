#!/usr/bin/env python3
"""
Advanced configuration manager for the ePubs system.

This module provides a comprehensive configuration management system
with support for multiple environments, validation, and dynamic updates.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .config_schema import ConfigSchema
from .config_loader import ConfigLoader, YamlConfigLoader
from .environment_manager import EnvironmentManager

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Exception raised for configuration-related errors."""
    pass


class ConfigManager:
    """
    Advanced configuration manager with schema validation and environment support.
    
    This class provides a comprehensive configuration management system that
    supports multiple environments, configuration validation, and dynamic updates.
    """
    
    def __init__(self, 
                 config_directory: Union[str, Path],
                 schema: Optional[ConfigSchema] = None,
                 loader: Optional[ConfigLoader] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_directory: Directory containing configuration files
            schema: Optional configuration schema for validation
            loader: Optional configuration loader (defaults to YAML)
        """
        self.config_directory = Path(config_directory)
        self.schema = schema
        self.loader = loader or YamlConfigLoader()
        self.environment_manager = EnvironmentManager()
        
        # Configuration cache
        self._config_cache: Dict[str, Dict[str, Any]] = {}
        self._validation_cache: Dict[str, Dict[str, Any]] = {}
        
        # Ensure config directory exists
        self.config_directory.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized ConfigManager with directory: {self.config_directory}")
    
    def load_config(self, 
                   environment: Optional[str] = None,
                   component: Optional[str] = None,
                   validate: bool = True) -> Dict[str, Any]:
        """
        Load configuration for a specific environment and component.
        
        Args:
            environment: Environment name (uses current if None)
            component: Component name (loads all if None)
            validate: Whether to validate configuration
            
        Returns:
            Loaded and merged configuration
            
        Raises:
            ConfigurationError: If configuration is invalid or cannot be loaded
        """
        try:
            # Determine effective environment
            if environment is None:
                environment = self.environment_manager.get_current_environment()
            
            # Generate cache key
            cache_key = f"{environment}:{component or 'all'}"
            
            # Check cache
            if cache_key in self._config_cache:
                logger.debug(f"Using cached configuration for {cache_key}")
                return self._config_cache[cache_key]
            
            # Load base configuration
            config = self._load_base_config()
            
            # Load environment-specific configuration
            env_config = self._load_environment_config(environment)
            if env_config:
                config = self._deep_merge(config, env_config)
            
            # Load component-specific configuration
            if component:
                component_config = self._load_component_config(component, environment)
                if component_config:
                    config = self._deep_merge(config, component_config)
            
            # Apply environment variables
            config = self._apply_environment_variables(config)
            
            # Validate configuration
            if validate and self.schema:
                validation_result = self.validate_config(config, environment)
                if not validation_result['valid']:
                    errors = validation_result['errors']
                    raise ConfigurationError(f"Configuration validation failed: {errors}")
                
                # Use effective config from validation
                config = validation_result['effective_config']
            
            # Cache the result
            self._config_cache[cache_key] = config
            
            logger.info(f"Loaded configuration for environment '{environment}'" +
                       (f", component '{component}'" if component else ""))
            
            return config
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise ConfigurationError(f"Failed to load configuration: {e}")
    
    def get_config_value(self, 
                        key: str,
                        environment: Optional[str] = None,
                        component: Optional[str] = None,
                        default: Any = None) -> Any:
        """
        Get a specific configuration value using dot notation.
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'section.field')
            environment: Environment name
            component: Component name
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        try:
            config = self.load_config(environment, component)
            
            # Navigate using dot notation
            keys = key.split('.')
            value = config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
            
        except Exception as e:
            logger.warning(f"Error getting config value '{key}': {e}")
            return default
    
    def set_config_value(self, 
                        key: str,
                        value: Any,
                        environment: Optional[str] = None,
                        component: Optional[str] = None,
                        persist: bool = True) -> bool:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
            environment: Environment name
            component: Component name
            persist: Whether to persist changes to disk
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load current configuration
            config = self.load_config(environment, component, validate=False)
            
            # Set value using dot notation
            keys = key.split('.')
            current = config
            
            # Navigate to parent
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            
            # Set the value
            current[keys[-1]] = value
            
            # Validate if schema is available
            if self.schema:
                validation_result = self.validate_config(config, environment)
                if not validation_result['valid']:
                    logger.error(f"Configuration validation failed after setting '{key}'")
                    return False
            
            # Update cache
            cache_key = f"{environment or self.environment_manager.get_current_environment()}:{component or 'all'}"
            self._config_cache[cache_key] = config
            
            # Persist if requested
            if persist:
                return self._persist_config(config, environment, component)
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting config value '{key}': {e}")
            return False
    
    def validate_config(self, 
                       config: Optional[Dict[str, Any]] = None,
                       environment: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate configuration against the schema.
        
        Args:
            config: Configuration to validate (loads if None)
            environment: Environment name
            
        Returns:
            Validation result dictionary
        """
        if not self.schema:
            return {
                'valid': True,
                'errors': {},
                'warnings': {},
                'effective_config': config or {}
            }
        
        if config is None:
            config = self.load_config(environment, validate=False)
        
        # Check validation cache
        cache_key = f"{environment or 'default'}:{hash(str(config))}"
        if cache_key in self._validation_cache:
            return self._validation_cache[cache_key]
        
        # Perform validation
        env_vars = dict(os.environ)
        result = self.schema.validate_config(config, env_vars)
        
        # Cache result
        self._validation_cache[cache_key] = result
        
        return result
    
    def reload_config(self, 
                     environment: Optional[str] = None,
                     component: Optional[str] = None) -> Dict[str, Any]:
        """
        Reload configuration from disk, clearing cache.
        
        Args:
            environment: Environment name
            component: Component name
            
        Returns:
            Reloaded configuration
        """
        # Clear relevant cache entries
        cache_key = f"{environment or self.environment_manager.get_current_environment()}:{component or 'all'}"
        self._config_cache.pop(cache_key, None)
        self._validation_cache.clear()  # Clear all validation cache
        
        return self.load_config(environment, component)
    
    def get_available_environments(self) -> List[str]:
        """
        Get list of available environments.
        
        Returns:
            List of environment names
        """
        environments = set()
        
        # Scan for environment-specific config files
        for config_file in self.config_directory.glob('*.yaml'):
            filename = config_file.stem
            
            # Pattern: {environment}.yaml or {component}_{environment}.yaml
            if '_' in filename:
                parts = filename.split('_')
                if len(parts) >= 2:
                    environments.add(parts[-1])
            else:
                environments.add(filename)
        
        return sorted(list(environments))
    
    def get_available_components(self, environment: Optional[str] = None) -> List[str]:
        """
        Get list of available components.
        
        Args:
            environment: Optional environment filter
            
        Returns:
            List of component names
        """
        components = set()
        
        pattern = f"*_{environment}.yaml" if environment else "*_*.yaml"
        
        for config_file in self.config_directory.glob(pattern):
            filename = config_file.stem
            
            if '_' in filename:
                parts = filename.split('_')
                if len(parts) >= 2:
                    component = '_'.join(parts[:-1])
                    components.add(component)
        
        return sorted(list(components))
    
    def get_config_info(self) -> Dict[str, Any]:
        """
        Get information about the configuration system.
        
        Returns:
            Dictionary with configuration information
        """
        info = {
            'config_directory': str(self.config_directory),
            'current_environment': self.environment_manager.get_current_environment(),
            'available_environments': self.get_available_environments(),
            'available_components': self.get_available_components(),
            'schema_loaded': self.schema is not None,
            'cache_entries': len(self._config_cache),
            'validation_cache_entries': len(self._validation_cache)
        }
        
        if self.schema:
            info['schema_info'] = {
                'name': self.schema.name,
                'version': self.schema.version,
                'sections': list(self.schema.sections.keys())
            }
        
        return info
    
    def generate_example_config(self, environment: str = "example") -> Dict[str, Any]:
        """
        Generate an example configuration file.
        
        Args:
            environment: Environment name for the example
            
        Returns:
            Example configuration dictionary
        """
        if not self.schema:
            return {
                'example': {
                    'setting1': 'value1',
                    'setting2': 42,
                    'setting3': True
                }
            }
        
        return self.schema.generate_example_config()
    
    def export_config(self, 
                     output_path: Union[str, Path],
                     environment: Optional[str] = None,
                     component: Optional[str] = None) -> bool:
        """
        Export configuration to a file.
        
        Args:
            output_path: Path to write configuration
            environment: Environment name
            component: Component name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            config = self.load_config(environment, component)
            output_path = Path(output_path)
            
            return self.loader.save_config(config, output_path)
            
        except Exception as e:
            logger.error(f"Error exporting configuration: {e}")
            return False
    
    def _load_base_config(self) -> Dict[str, Any]:
        """Load base configuration."""
        base_file = self.config_directory / "default.yaml"
        
        if base_file.exists():
            return self.loader.load_config(base_file)
        
        return {}
    
    def _load_environment_config(self, environment: str) -> Optional[Dict[str, Any]]:
        """Load environment-specific configuration."""
        env_file = self.config_directory / f"{environment}.yaml"
        
        if env_file.exists():
            return self.loader.load_config(env_file)
        
        return None
    
    def _load_component_config(self, component: str, environment: str) -> Optional[Dict[str, Any]]:
        """Load component-specific configuration."""
        component_file = self.config_directory / f"{component}_{environment}.yaml"
        
        if component_file.exists():
            return self.loader.load_config(component_file)
        
        # Try component-only file
        component_only_file = self.config_directory / f"{component}.yaml"
        if component_only_file.exists():
            return self.loader.load_config(component_only_file)
        
        return None
    
    def _apply_environment_variables(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides."""
        if not self.schema:
            return config
        
        env_vars = dict(os.environ)
        
        # Apply environment variables based on schema
        for section_name, section in self.schema.sections.items():
            if section_name not in config:
                config[section_name] = {}
            
            for field_name, field in section.fields.items():
                if field.environment_variable and field.environment_variable in env_vars:
                    env_value = field._convert_env_value(env_vars[field.environment_variable])
                    config[section_name][field_name] = env_value
        
        return config
    
    def _deep_merge(self, base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two configuration dictionaries."""
        result = base.copy()
        
        for key, value in overlay.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _persist_config(self, 
                       config: Dict[str, Any],
                       environment: Optional[str] = None,
                       component: Optional[str] = None) -> bool:
        """Persist configuration to disk."""
        try:
            # Determine target file
            if component and environment:
                filename = f"{component}_{environment}.yaml"
            elif environment:
                filename = f"{environment}.yaml"
            elif component:
                filename = f"{component}.yaml"
            else:
                filename = "default.yaml"
            
            target_file = self.config_directory / filename
            
            return self.loader.save_config(config, target_file)
            
        except Exception as e:
            logger.error(f"Error persisting configuration: {e}")
            return False