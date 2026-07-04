"""Dependency injection container.

Provides a simple service registry for wiring interfaces to implementations.
"""

from typing import Any, TypeVar, Type

T = TypeVar("T")


class Container:
    """Lightweight dependency injection container."""

    def __init__(self):
        self._registry: dict[type, Any] = {}

    def register(self, interface: type, instance: Any) -> None:
        """Register a concrete instance for an interface."""
        self._registry[interface] = instance

    def resolve(self, interface: Type[T]) -> T:
        """Resolve an interface to its registered implementation."""
        instance = self._registry.get(interface)
        if instance is None:
            raise KeyError(f"No implementation registered for {interface.__name__}")
        return instance

    def is_registered(self, interface: type) -> bool:
        """Check whether an interface has a registered implementation."""
        return interface in self._registry


container = Container()
