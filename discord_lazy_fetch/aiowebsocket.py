#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aiowebsocket.py - Proxied aiohttp websocket module
"""

__author__ = "Grapphy"


# Built-in libraries
import aiohttp
import random
import asyncio
import json

# Repository modules
from . import opcodes
from . import utils
from . import models

# Third party libraries
from .third_party.user_agents import parse

# Global variables
_GATEWAY = "wss://gateway.discord.gg/?v=8&encoding=json"
_DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) "
    "Gecko/20100101 Firefox/92.0"
)


class EventHandler(object):
    async def received_message(self, wsocket, msg: dict):
        if msg is None:
            return

        msg = json.loads(msg)

        op = msg.get("op")
        data = msg.get("d")
        seq = msg.get("s")

        if msg.get("t"):
            data = msg

        wsocket.sequence = seq
        handler = f"event_op_{op}"

        if hasattr(self, handler):
            return await getattr(self, handler)(wsocket, data)
        raise Exception(f"Unhandled response: {handler}")


class WSEvents(EventHandler):
    async def event_op_0(self, wsocket, data: dict):
        if data["t"] == "READY":
            wsocket.identified = True
            wsocket.is_ready.set()
        elif data["t"] == "GUILD_MEMBER_LIST_UPDATE":
            await wsocket.process_members(data["d"]["ops"])

    async def event_op_10(self, wsocket, data: dict):
        interval = data["heartbeat_interval"] / 1000.0
        wsocket.keep_alive = KeepConnectionAlive(wsocket, interval)
        await wsocket.keep_alive.send_heartbeat()
        asyncio.ensure_future(wsocket.keep_alive.start())

    async def event_op_11(self, wsocket, data: dict):
        if not wsocket.identified:
            await wsocket.identify()


class KeepConnectionAlive(object):
    def __init__(self, ws: aiohttp.ClientWebSocketResponse, heartbeat: int):
        self.ws = ws
        self.heartbeat = heartbeat
        self._is_running = asyncio.Event()

    async def send_heartbeat(self):
        await self.ws.ws.send_str(opcodes.get_heartbeat(self.ws.sequence))

    async def start(self):
        self._is_running.set()

        while self._is_running.is_set():
            await asyncio.sleep(self.heartbeat)
            await self.send_heartbeat()

    async def stop(self):
        self._is_running.clear()


class IDiscordWS(object):
    """
    IDiscordWS class is an Interface for a websocket
    handling connections to Discord's gateway in order
    to run specific commands such as OP 14 for fetching
    server members.

    Attributes:
        token (str): Discord account token
        proxy (str): Any given proxy
        proxy_auth (aiohttp.BasicAuth): Aiohttp Proxy Auth
        user_agent (str): Any User-Agent to use
    """

    token: str = None
    proxy: str = None
    sequence: int = None
    heartbeat: int = 30.0
    identified: bool = False
    user_agent: str = _DEFAULT_UA
    event_handler: WSEvents = WSEvents()
    proxy_auth: aiohttp.BasicAuth = None
    session: aiohttp.ClientSession = None
    keep_alive: KeepConnectionAlive = None
    is_ready: asyncio.Event = asyncio.Event()
    ws: aiohttp.ClientWebSocketResponse = None

    def __init__(
        self,
        token: str = None,
        proxy: str = None,
        proxy_auth: aiohttp.BasicAuth = None,
        user_agent: str = None,
    ):
        self.token = token
        self.proxy = proxy
        self.proxy_auth = proxy_auth
        self.user_agent = user_agent or _DEFAULT_UA

    async def recv(self, *args, **kwargs):
        return await self.ws.receive()

    async def send(self, data: str):
        try:
            await self.ws.send_str(data)
        except Exception as error:
            raise Exception(f"Websocket error: {error}")

    async def poll_events(self):
        while not self.ws.closed:
            try:
                msg = await asyncio.wait_for(
                    self.recv(), timeout=self.heartbeat
                )
                await self.event_handler.received_message(self, msg.data)
            except (asyncio.TimeoutError) as error:
                raise Exception("Websocket connection timeout!")
            except Exception as error:
                raise Exception(f"Unknown error: {error}")

    async def ws_connect(self, url):
        kwargs = {
            "proxy_auth": self.proxy_auth,
            "proxy": self.proxy,
            "max_msg_size": 0,
            "timeout": 30.0,
            "autoclose": False,
            "headers": {
                "User-Agent": self.user_agent,
            },
            "compress": 0,
        }

        return await self.session.ws_connect(url, **kwargs)

    async def identify(self):
        kwargs = {}

        if self.user_agent:
            user_agent_parser = parse(self.user_agent)

            kwargs["os"] = user_agent_parser.os.family
            kwargs["browser"] = user_agent_parser.browser.family
            kwargs["device"] = user_agent_parser.device.family

        payload = opcodes.get_identify(self.token, **kwargs)
        await self.send(payload)

    async def get_members(
        self, guild_id: int, channel_id: int, max_presences: int
    ) -> list:
        """Fetchs all memebers from a given Discord server.

        Args:
            guild_id (int): Server ID
            channel_id (int): Channel ID
            max_presences (int): Max number of members to load

        Returns:
            list: List of server members.
        """
        self.loaded_members = []
        ranges = utils.craft_ranges(max_presences)

        for _range in ranges:
            payload = opcodes.get_lazy_guild(guild_id, [channel_id], _range)
            await self.send(payload)
            await asyncio.sleep(1.5)

        await asyncio.sleep(random.uniform(2, 3))
        return self.loaded_members

    async def process_members(self, data: dict):
        for _range in data:
            if _range["op"] == "SYNC":
                for item in _range["items"]:
                    if "member" in item:
                        member = models.LazyMember(data=item["member"])
                        self.loaded_members.append(member)

    async def connect(self, verify_ssl: bool = True):
        self.session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(verify_ssl=verify_ssl)
        )

        self.ws = await self.ws_connect(_GATEWAY)
        asyncio.ensure_future(self.poll_events())
        await self.is_ready.wait()

    async def close(self):
        await self.keep_alive.stop()
        await self.ws.close()
