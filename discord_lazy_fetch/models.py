#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
models.py - Models for lazy members
"""

__author__ = "Grapphy"


class User(object):
    cdn = "https://cdn.discordapp.com"

    def __init__(self, data: dict):
        self.id = data.get("id")
        self.name = data.get("username")
        self._avatar = data.get("avatar")
        self.bot = data.get("bot") or False
        self.flags = data.get("public_flags")
        self.discriminator = data.get("discriminator")

    @property
    def avatar(self):
        return f"{self.cdn}/avatars/{self.id}/{self._avatar}.png"


class LazyMember(User):
    """LazyMember class is a model of a User object
    similar to discord.py's implementation.

    It does not include HTTP interactions (open_dm,
    send_friend_request, block, etc.) but can be given a
    aiohttp.ClientSession for it.

    Attributes:
        data (dict): Raw JSON data from websocket
        guild_id (guild_id): Guild where the user belongs to
        http (object): Any HTTP handler for API calls
    """

    def __init__(self, data: dict, guild_id: int = None, http: object = None):
        super().__init__(data=data.get("user"))
        self.data = data
        self.guild_id = guild_id
        self.http = http

        self.nick = data.get("nick")
        self.roles = data.get("roles")
        self.presence = data.get("presence")
        self.joined_at = data.get("joined_at")
        self.premium_since = data.get("premium_since")

    def __str__(self):
        return f"{self.name}#{self.discriminator}"

    def __repr__(self):
        return (
            f"<LazyMember id={self.id} name={self.name} "
            f"discriminator={self.discriminator} nick={self.nick} "
            f"guild={self.guild_id} status={self.status}"
        )

    @property
    def status(self):
        return self.presence["status"]

    @property
    def device(self):
        return [*self.presence["client_status"]][0]

    @property
    def on_mobile(self):
        return "mobile" in self.presence["client_status"]
