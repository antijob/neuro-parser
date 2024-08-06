from abc import ABC, abstractmethod
from typing import TypeVar, Type, Generic

# Define a type variable constrained to Handler subclasses


class Handler(ABC):
    """
    Abstract base class that enforces the implementation of 'can_handle' method
    in subclasses.
    """

    @classmethod
    @abstractmethod
    def can_handle(self, *args, **kwargs) -> bool:
        """
        Determine if the handler can handle the given arguments.
        Should return True or False.
        """
        pass


T = TypeVar("T", bound=Handler)


class HandlerRegistry(Generic[T]):
    """
    A registry for managing and selecting handlers based on their 'can_handle' method.
    This version uses generics to enforce that registered classes are subclasses of Handler.
    """

    def __init__(self):
        self._handlers: list[Type[T]] = []

    def register(self, handler_class: Type[T]):
        """
        Registers a handler class. Ensures the class is a subclass of Handler.
        """
        if issubclass(handler_class, Handler):
            self._handlers.append(handler_class)
        else:
            raise TypeError(f"{handler_class.__name__} must be a subclass of 'Handler'")

    def choose(self, *args, **kwargs) -> T:
        """
        Chooses the appropriate handler by checking their 'can_handle' method.
        Returns an instance of the first handler class that can handle the given arguments.
        """
        for handler_class in self._handlers:
            if handler_class.can_handle(*args, **kwargs):
                return handler_class

        raise ValueError("No suitable handler found.")
