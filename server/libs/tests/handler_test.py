import pytest
from server.libs.handler import HandlerRegistry, Handler

# Example handler implementations for testing


class BaseHandler(Handler):
    """
    A simple base handler that always returns False for can_handle.
    This should be used as a base or fallback handler.
    """

    @classmethod
    def can_handle(cls, url: str) -> bool:
        return False


class UrlHandlerOne(Handler):
    """
    A handler that returns True if the URL contains 'one'.
    """

    @classmethod
    def can_handle(cls, url: str) -> bool:
        return "one" in url


class UrlHandlerTwo(Handler):
    """
    A handler that returns True if the URL contains 'two'.
    """

    @classmethod
    def can_handle(cls, url: str) -> bool:
        return "two" in url


@pytest.fixture
def registry() -> HandlerRegistry:
    """
    Fixture to provide a fresh HandlerRegistry instance for each test.
    """
    return HandlerRegistry()


def test_register_valid_handler_with_can_handle_method(registry: HandlerRegistry):
    registry.register(UrlHandlerOne)
    assert len(registry._handlers) == 1
    assert registry._handlers[0] == UrlHandlerOne


def test_register_non_handler_with_can_handle_method(registry: HandlerRegistry):
    class InvalidHandlerWithCanHandle:
        @classmethod
        def can_handle(cls, url: str) -> bool:
            return True

    with pytest.raises(TypeError):
        registry.register(InvalidHandlerWithCanHandle)


def test_choose_correct_handler_with_url(registry: HandlerRegistry):
    registry.register(UrlHandlerOne)
    registry.register(UrlHandlerTwo)

    chosen_handler_class = registry.choose("http://example.com/one")
    assert chosen_handler_class == UrlHandlerOne

    chosen_handler_class = registry.choose("http://example.com/two")
    assert chosen_handler_class == UrlHandlerTwo


def test_choose_no_suitable_handler_with_url(registry: HandlerRegistry):
    registry.register(BaseHandler)

    with pytest.raises(ValueError, match="No suitable handler found"):
        registry.choose("http://example.com/unknown")


def test_register_and_choose_with_multiple_url_handlers(registry: HandlerRegistry):
    registry.register(BaseHandler)
    registry.register(UrlHandlerOne)
    registry.register(UrlHandlerTwo)

    assert len(registry._handlers) == 3

    chosen_handler_class = registry.choose("http://example.com/one")
    assert chosen_handler_class == UrlHandlerOne

    chosen_handler_class = registry.choose("http://example.com/two")
    assert chosen_handler_class == UrlHandlerTwo

    with pytest.raises(ValueError, match="No suitable handler found"):
        registry.choose("http://example.com/unknown")
