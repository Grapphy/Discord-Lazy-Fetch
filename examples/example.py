#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
example.py - Example code
"""

__author__ = "Grapphy"


# Importing libraries
import os
import asyncio
from dotenv import load_dotenv

# Repository
from discord_lazy_fetch import IDiscordWS

# Load enviroment variables
load_dotenv()

# Global variables
CONFIG = {
    "token": os.getenv("TEST_TOKEN"),
    "guild_id": int(os.getenv("TEST_GUILD")),
    "channel_id": int(os.getenv("TEST_CHANNEL")),
    "max_presences": 10000,
}


async def main(config: dict):
    token = config.get("token")
    guild_id = config.get("guild_id")
    channel_id = config.get("channel_id")
    presences = config.get("max_presences")

    wsclient = IDiscordWS(token=token)

    await wsclient.connect()
    print("Client connected to the gateway")

    members_id = await wsclient.get_members(guild_id, channel_id, presences)
    print(f"Loaded: {len(members_id)} members!")

    for member in members_id:
        print(repr(member))

    print("Disconnected!")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(CONFIG))
