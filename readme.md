# Discord Lazy Fetch
Discord lazy fetch is a script for getting all members from a Discord server. Currently only bot accounts with [privileged members intents](https://discord.com/developers/docs/topics/gateway#privileged-intents) can get the full list of server members but this script allows you to request _most_ members using a self-bot account.

## Table of contents
* [How does it works?](https://github.com/Grapphy/Discord-Lazy-Fetch/readme.md#how-does-it-works)
* [Examples](https://github.com/Grapphy/Discord-Lazy-Fetch/readme.md#examples)
* [Requirements](https://github.com/Grapphy/Discord-Lazy-Fetch/readme.md#requirements)
* [Credits](https://github.com/Grapphy/Discord-Lazy-Fetch/readme.md#credits)

## How does it works?
Discord uses websockets for fetching online users from the server members list (and offline users if the server has less than 1k members). This script replicates the communication between the client and Discord's gateway to send OP code 14 (undocumented) for loading a range of members from a server.

The result from the script includes all data from members (user id, status, presence, name, roles, etc.) and it will not return offline users if the server has more than 1k members.

## Examples
```python
# Import libraries.
import asyncio
from discord_lazy_fetch import IDiscordWS

# Some configurations. Be sure to use the correct data type.
_CONFIG = {
    "token": "Your user token (str)",
    "guild_id": "some guild id (int)",
    "channel_id": "some channel id (int)",
    "max_presences": "max members to fetch (int)"
}


async def main(config: dict):
    # Load configuration into local variables.
    token = config.get("token")
    guild_id = config.get("guild_id")
    channel_id = config.get("channel_id")
    presences = config.get("max_presences")

    # Set up the IDiscordWS object.
    wsclient = IDiscordWS(token=token)

    # Connects to Discord's gateway.
    await wsclient.connect()

    # Fetchs members from a guild and channel.
    members_id = await wsclient.get_members(guild_id, channel_id, presences)

    # Prints total amount of loaded members.
    print(f"Loaded {len(members_id)} members!")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(_CONFIG))
```

## Using proxies and changing User-Agent
Both of these options are available as an attribute for the `WebSocket` class.

```python
# Import libraries.
import aiohttp
from discord_lazy_fetch import IDiscordWS

# Settings.
token = "any.token.here"
proxy = "host:port"
auth = aiohttp.BasicAuth("proxy_user", "proxy_password")
user_agent = "python requests"

# Creating IDiscordWS object.
wsclient = IDiscordWS(token=token, proxy=proxy, proxy_auth=auth, user_agent=user_agent)
```

## Requirements
You might be required to have `aiohttp` and `ua_parser` installed.

```console
aiohttp==3.7.4.post0
ua_parser==0.10.0
```

## Installation
```console
pip install /path/to/repo
```

## Credits
Created and maintained by [@Grapphy](https://github.com/grapphy). Feel free to contribute to this repo in any form.
