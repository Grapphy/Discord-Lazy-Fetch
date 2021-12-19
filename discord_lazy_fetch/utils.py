#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
utils.py - Keep doing this fucking lazy shit bro nothing changed
"""

__author__ = "Grapphy"

# Built-in libraries
import json
import base64


def craft_ranges(total_members: int) -> list:
    """Creates ranges based on the total members visibles
    in a guild channel.

    Args:
        total_members (int): Max number of members to fetch

    Returns:
        list[list[list[int, int], ...]]: List of ranges
    """
    _total_members = 0
    _member_ranges = []

    while _total_members <= total_members:
        ranges = []
        base = _total_members

        while len(ranges) < 3:
            ranges.append([base, base + 99])
            base += 100

        _total_members = base
        _member_ranges.append(ranges)

    return _member_ranges
