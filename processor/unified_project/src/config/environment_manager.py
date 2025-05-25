#!/usr/bin/env python3
"""
Environment management for configuration system.

This module provides environment detection and management capabilities
for the configuration system.
"""

import os
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class EnvironmentManager:
    """
    Environment manager for configuration system.
    
    This class handles environment detection, switching, and management
    for the configuration system.
    """
    
    def __init__(self, 
                 env_var_name: str = "EPUBS_ENV",
                 default_environment: str = "development"):
        """
        Initialize environment manager.
        
        Args:
            env_var_name: Environment variable name to check
            default_environment: Default environment if none specified
        """
        self.env_var_name = env_var_name
        self.default_environment = default_environment
        
        # Environment hierarchy (for inheritance)
        self.environment_hierarchy = {
            'production': ['production', 'staging', 'development'],
            'staging': ['staging', 'development'],
            'testing': ['testing', 'development'],
            'development': ['development']
        }
        
        # Environment characteristics
        self.environment_info = {
            'production': {
                'name': 'Production',
                'description': 'Live production environment',
                'debug': False,
                'strict_validation': True,
                'log_level': 'WARNING'
            },
            'staging': {
                'name': 'Staging',
                'description': 'Pre-production staging environment',
                'debug': False,
                'strict_validation': True,
                'log_level': 'INFO'
            },
            'testing': {
                'name': 'Testing',
                'description': 'Automated testing environment',
                'debug': True,
                'strict_validation': True,
                'log_level': 'DEBUG'
            },
            'development': {
                'name': 'Development',
                'description': 'Local development environment',
                'debug': True,
                'strict_validation': False,
                'log_level': 'DEBUG'
            }
        }
    
    def get_current_environment(self) -> str:
        """
        Get the current environment name.
        
        Returns:
            Current environment name
        """
        # Check environment variable
        env = os.environ.get(self.env_var_name)
        if env:
            env = env.lower().strip()
            if self.is_valid_environment(env):
                return env
            else:
                logger.warning(f"Invalid environment '{env}' in {self.env_var_name}, using default")
        
        # Check for common environment indicators
        detected_env = self._detect_environment()
        if detected_env:
            return detected_env
        
        return self.default_environment
    
    def set_current_environment(self, environment: str) -> bool:
        """
        Set the current environment.
        
        Args:
            environment: Environment name to set
            
        Returns:
            True if successful, False if invalid environment
        """
        if not self.is_valid_environment(environment):
            logger.error(f"Invalid environment: {environment}")
            return False
        
        os.environ[self.env_var_name] = environment
        logger.info(f"Set environment to: {environment}")
        return True
    
    def is_valid_environment(self, environment: str) -> bool:
        """
        Check if an environment name is valid.
        
        Args:
            environment: Environment name to check
            
        Returns:
            True if valid, False otherwise
        """
        return environment.lower() in self.environment_info
    
    def get_available_environments(self) -> List[str]:
        """
        Get list of available environments.
        
        Returns:
            List of environment names
        """
        return list(self.environment_info.keys())
    
    def get_environment_info(self, environment: Optional[str] = None) -> Dict[str, any]:
        """
        Get information about an environment.
        
        Args:
            environment: Environment name (uses current if None)
            
        Returns:
            Environment information dictionary
        """
        if environment is None:
            environment = self.get_current_environment()
        
        if environment not in self.environment_info:
            return {}
        
        info = self.environment_info[environment].copy()
        info['current'] = environment == self.get_current_environment()
        info['hierarchy'] = self.environment_hierarchy.get(environment, [environment])
        
        return info
    
    def get_environment_hierarchy(self, environment: Optional[str] = None) -> List[str]:
        """
        Get environment hierarchy for configuration inheritance.
        
        Args:
            environment: Environment name (uses current if None)
            
        Returns:
            List of environments in inheritance order
        """
        if environment is None:
            environment = self.get_current_environment()
        
        return self.environment_hierarchy.get(environment, [environment])
    
    def is_production(self, environment: Optional[str] = None) -> bool:
        """
        Check if environment is production.
        
        Args:
            environment: Environment name (uses current if None)
            
        Returns:
            True if production environment
        """
        if environment is None:
            environment = self.get_current_environment()
        
        return environment == 'production'
    
    def is_development(self, environment: Optional[str] = None) -> bool:
        """
        Check if environment is development.
        
        Args:
            environment: Environment name (uses current if None)
            
        Returns:
            True if development environment
        """
        if environment is None:
            environment = self.get_current_environment()
        
        return environment == 'development'
    
    def is_testing(self, environment: Optional[str] = None) -> bool:
        """
        Check if environment is testing.
        
        Args:
            environment: Environment name (uses current if None)
            
        Returns:
            True if testing environment
        """
        if environment is None:
            environment = self.get_current_environment()
        
        return environment == 'testing'
    
    def should_debug(self, environment: Optional[str] = None) -> bool:
        """
        Check if debug mode should be enabled.
        
        Args:
            environment: Environment name (uses current if None)
            
        Returns:
            True if debug should be enabled
        """
        info = self.get_environment_info(environment)
        return info.get('debug', False)
    
    def should_strict_validate(self, environment: Optional[str] = None) -> bool:
        """
        Check if strict validation should be enabled.
        
        Args:
            environment: Environment name (uses current if None)
            
        Returns:
            True if strict validation should be enabled
        """
        info = self.get_environment_info(environment)
        return info.get('strict_validation', True)
    
    def get_log_level(self, environment: Optional[str] = None) -> str:
        """
        Get recommended log level for environment.
        
        Args:
            environment: Environment name (uses current if None)
            
        Returns:
            Log level string
        """
        info = self.get_environment_info(environment)
        return info.get('log_level', 'INFO')
    
    def get_environment_variables(self, environment: Optional[str] = None) -> Dict[str, str]:
        """
        Get environment-specific environment variables.
        
        Args:
            environment: Environment name (uses current if None)
            
        Returns:
            Dictionary of environment variables
        """
        if environment is None:
            environment = self.get_current_environment()
        
        # Base environment variables
        env_vars = {
            self.env_var_name: environment
        }
        
        # Environment-specific variables
        info = self.get_environment_info(environment)
        
        if 'debug' in info:
            env_vars['DEBUG'] = str(info['debug']).lower()
        
        if 'log_level' in info:
            env_vars['LOG_LEVEL'] = info['log_level']
        
        return env_vars
    
    def setup_environment(self, environment: Optional[str] = None) -> bool:
        """
        Setup environment by setting appropriate environment variables.
        
        Args:
            environment: Environment name (uses current if None)
            
        Returns:
            True if successful
        """
        if environment is None:
            environment = self.get_current_environment()
        
        if not self.is_valid_environment(environment):
            logger.error(f"Cannot setup invalid environment: {environment}")
            return False
        
        try:
            # Set environment variables
            env_vars = self.get_environment_variables(environment)
            for key, value in env_vars.items():
                os.environ[key] = value
            
            # Configure logging if needed
            log_level = self.get_log_level(environment)
            numeric_level = getattr(logging, log_level.upper(), logging.INFO)
            logging.getLogger().setLevel(numeric_level)
            
            logger.info(f"Environment setup completed: {environment}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up environment {environment}: {e}")
            return False
    
    def _detect_environment(self) -> Optional[str]:
        """
        Detect environment based on various indicators.
        
        Returns:
            Detected environment name or None
        """
        # Check common environment variables
        common_env_vars = [
            'NODE_ENV',
            'ENVIRONMENT',
            'ENV',
            'STAGE'
        ]
        
        for var in common_env_vars:
            value = os.environ.get(var, '').lower()
            if value in ['prod', 'production']:
                return 'production'
            elif value in ['stage', 'staging']:
                return 'staging'
            elif value in ['test', 'testing']:
                return 'testing'
            elif value in ['dev', 'development']:
                return 'development'
        
        # Check for CI/CD environment
        ci_indicators = [
            'CI',
            'CONTINUOUS_INTEGRATION',
            'JENKINS_URL',
            'GITHUB_ACTIONS',
            'GITLAB_CI',
            'TRAVIS'
        ]
        
        if any(os.environ.get(var) for var in ci_indicators):
            return 'testing'
        
        # Check for Docker environment
        if os.path.exists('/.dockerenv'):
            return 'staging'  # Assume Docker means staging unless specified
        
        return None
    
    def add_environment(self, 
                       name: str, 
                       info: Dict[str, any],
                       hierarchy: Optional[List[str]] = None) -> bool:
        """
        Add a custom environment.
        
        Args:
            name: Environment name
            info: Environment information dictionary
            hierarchy: Optional inheritance hierarchy
            
        Returns:
            True if successful
        """
        try:
            name = name.lower()
            
            # Validate required fields
            required_fields = ['name', 'description']
            for field in required_fields:
                if field not in info:
                    logger.error(f"Missing required field '{field}' for environment {name}")
                    return False
            
            # Add default values
            defaults = {
                'debug': False,
                'strict_validation': True,
                'log_level': 'INFO'
            }
            
            for key, default_value in defaults.items():
                if key not in info:
                    info[key] = default_value
            
            # Add to environments
            self.environment_info[name] = info
            
            # Add hierarchy
            if hierarchy:
                self.environment_hierarchy[name] = hierarchy
            else:
                self.environment_hierarchy[name] = [name, 'development']
            
            logger.info(f"Added custom environment: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding environment {name}: {e}")
            return False