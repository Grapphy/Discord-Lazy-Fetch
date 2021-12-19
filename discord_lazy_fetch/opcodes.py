#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
opcodes.py- Contains opcodes to interact with
discord gateway
"""

__author__ = "Grapphy"

# Built-in libraries
import json
import time
import sys

# Typing
JSON = str  # JSON string

# Global variables
_DEFAULT_PROPS = "discord.py"


def get_identify(
    token: str,
    os: str = sys.platform,
    browser: str = _DEFAULT_PROPS,
    device: str = _DEFAULT_PROPS,
) -> JSON:
    """Returns JSON data to do a gateway identification.

    Args:
        token (str): Discord account token
        os (str): Operative system from client
        browser (str): Browser User-Agent
        device (str): Device information

    Returns:
        str: JSON string
    """
    identify = {
        "op": 2,
        "d": {
            "token": token,
            "properties": {
                "$os": os,
                "$browser": browser,
                "$device": device,
                "$referrer": "",
                "$referring_domain": "",
            },
            "compress": False,
            "large_threshold": 250,
            "v": 3,
        },
    }

    return json.dumps(identify)


def get_heartbeat(sequence: int) -> JSON:
    """Sends heartbeat to the gateway. Keeps connection
    alive.

    Args:
        interval (int): Last sequence from response

    Returns:
        str: JSON string
    """
    heartbeat = {"op": 1, "d": sequence}

    return json.dumps(heartbeat)


def get_lazy_guild(
    guild_id: int,
    channels_id: list,
    ranges: list,
    activities: bool = False,
    typing: bool = True,
) -> JSON:
    """Requests members from a guild channel. You can only requests
    3 ranges ([[0, 99], [100, 199], ...]) up to max members.

    Args:
        guild_id (int): Discord guild id
        channels_id (list): Channels id to get members from
        ranges (list): Ranges to request
        activites (bool): Fetch activities
        typing (bool): Fetch members typing in channel

    Returns:
        str: JSON string
    """

    _channels = {channel: ranges for channel in channels_id}

    lazy_guild = {
        "op": 14,
        "d": {
            "guild_id": guild_id,
            "channels": _channels,
            "activities": activities,
            "typing": typing,
        },
    }

    return json.dumps(lazy_guild)
