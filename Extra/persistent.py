import discord
from discord.ext import commands
import datetime, pytz
from discord.ui import Button, Select, View
import aiosqlite, asyncio


from . import config


from Cogs.ticket import TicketView, ButtonView, ClosePanel









class PersistentView(commands.Cog):
    def __init__(self, bot):
        self.bot=bot


    @commands.Cog.listener("on_connect")
    async def BotSetup(self):
        await self.bot.wait_until_ready()
        self.bot.add_view(TicketView(bot=self.bot))
        self.bot.add_view(ButtonView(bot=self.bot))
        self.bot.add_view(ClosePanel(bot=self.bot))






async def setup(bot):
    await bot.add_cog(PersistentView(bot))