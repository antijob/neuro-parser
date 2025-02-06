import re
from dataclasses import dataclass
from typing import Optional, Union


@dataclass
class TelegramUrlInfo:
    base_url: str
    channel_id: Union[int, str]
    message_id: Optional[int] = None


def convert_id(channel: str) -> Union[int, str]:
    """
    Processes the channel value to handle negative numbers and convert to integer.
    If the channel is not a valid number, it returns it as a string.
    """
    try:
        # Convert to integer and handle negative numbers
        return int(channel)
    except ValueError:
        return channel


def get_telegram_ids(url: str) -> TelegramUrlInfo:
    pattern_message = (
        r"(?P<baseurl>https:\/\/[^\/]+\/(?:c\/)?)(?P<channel>\d+)\/(?P<message>\d+)"
    )
    pattern_channel = r"(?P<baseurl>https:\/\/[^\/]+\/(c\/)?)(?P<channel>[^\/]+)"
    pattern_hidden_channel = r"(?P<baseurl>https:\/\/[^\/]+\/a\/#)(?P<channel>[^\/]+)"

    # Match for URL with message ID
    match = re.match(pattern_message, url)
    if match:
        base_url = match.group("baseurl")
        channel = convert_id(match.group("channel"))
        message = convert_id(match.group("message"))

        return TelegramUrlInfo(
            base_url=base_url,
            channel_id=channel,
            message_id=message,
        )

    # Match for hidden channel (with '#' in the URL)
    match = re.match(pattern_hidden_channel, url)
    if match:
        base_url = match.group("baseurl")
        channel = convert_id(match.group("channel"))

        return TelegramUrlInfo(
            base_url=base_url,
            channel_id=channel,
        )

    # Match for URL without message ID
    match = re.match(pattern_channel, url)
    if match:
        base_url = match.group("baseurl")
        channel = convert_id(match.group("channel"))

        return TelegramUrlInfo(
            base_url=base_url,
            channel_id=channel,
        )

    raise Exception(f"get_telegram_ids: Can't parse telegram url: {url}")
