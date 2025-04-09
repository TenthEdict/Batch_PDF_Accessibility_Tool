#!/usr/bin/env python3
"""
Service Container module for dependency injection.

This module implements a simple service container for managing
component dependencies and enabling proper dependency injection
throughout the application.
"""

import logging
from typing import Any, Dict, Optional, Type, TypeVar, cast

T = TypeVar('T')

logger = logging.getLogger(__name__)


class ServiceContainer:
    """
    Service container implementation for dependency injection.
    
    The service container manages component instances and their dependencies,
    enabling loose coupling between components and facilitating testing.
    """
    
    def __init__(self):
        """Initialize an empty service container."""
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, callable] = {}
        self._singletons: Dict[str, bool] = {}
        self._singleton_instances: Dict[str, Any] = {}
    
    def register(self, service_id: str, factory: callable, singleton: bool = True) -> None:
        """
        Register a service factory.
        
        Args:
            service_id: Unique identifier for the service
            factory: Factory function that creates the service
            singleton: Whether the service should be a singleton (default: True)
        """
        self._factories[service_id] = factory
        self._singletons[service_id] = singleton
        
        # Clear singleton instance if already exists
        if service_id in self._singleton_instances:
            del self._singleton_instances[service_id]
            
        logger.debug(f"Registered service: {service_id} (singleton={singleton})")
    
    def register_instance(self, service_id: str, instance: Any) -> None:
        """
        Register an existing instance as a service.
        
        Args:
            service_id: Unique identifier for the service
            instance: Service instance to register
        """
        self._services[service_id] = instance
        logger.debug(f"Registered service instance: {service_id}")
    
    def get(self, service_id: str) -> Any:
        """
        Get a service instance.
        
        Args:
            service_id: Identifier for the service to retrieve
            
        Returns:
            Any: Service instance
            
        Raises:
            KeyError: If the service is not registered
        """
        # Return existing instance if available
        if service_id in self._services:
            return self._services[service_id]
        
        # Check if we have a factory for this service
        if service_id not in self._factories:
            raise KeyError(f"Service not registered: {service_id}")
        
        # For singletons, check if we have an instance already
        if self._singletons.get(service_id, False):
            if service_id in self._singleton_instances:
                return self._singleton_instances[service_id]
            
            # Create singleton instance
            instance = self._factories[service_id](self)
            self._singleton_instances[service_id] = instance
            return instance
        
        # For non-singletons, create a new instance every time
        return self._factories[service_id](self)
    
    def get_typed(self, service_id: str, expected_type: Type[T]) -> T:
        """
        Get a service instance with type checking.
        
        Args:
            service_id: Identifier for the service to retrieve
            expected_type: Expected type of the service
            
        Returns:
            T: Service instance of the expected type
            
        Raises:
            KeyError: If the service is not registered
            TypeError: If the service is not of the expected type
        """
        service = self.get(service_id)
        
        if not isinstance(service, expected_type):
            raise TypeError(
                f"Service {service_id} is not of expected type {expected_type.__name__}"
            )
        
        return cast(T, service)
    
    def has(self, service_id: str) -> bool:
        """
        Check if a service is registered.
        
        Args:
            service_id: Identifier for the service to check
            
        Returns:
            bool: True if the service is registered, False otherwise
        """
        return service_id in self._services or service_id in self._factories
    
    def reset(self) -> None:
        """Reset the container, clearing all registered services and instances."""
        self._services = {}
        self._factories = {}
        self._singletons = {}
        self._singleton_instances = {}
        logger.debug("Service container reset")


# Global service container instance
container = ServiceContainer()


def get_container() -> ServiceContainer:
    """
    Get the global service container instance.
    
    Returns:
        ServiceContainer: Global service container instance
    """
    return container