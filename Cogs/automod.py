from typing import Optional
from discord.ext import commands
from discord.interactions import Interaction
from discord.ui import Button, View



import asyncio, os, random, sys, io, textwrap, traceback, discord, datetime, aiohttp, psutil

from Extra import config



class AutoModeration(commands.Cog, name="Auto Moderation"):
    def __init__(self, bot):
        self.bot = bot





async def setup(bot):
    await bot.add_cog(AutoModeration(bot))