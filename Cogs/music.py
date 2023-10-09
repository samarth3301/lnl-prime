from discord.ext import commands, tasks

import datetime, typing, asyncio, os, wavelink, discord, re
from wavelink.ext import spotify


from Extra import config







class Music(commands.Cog):
    def __init__(self, bot):
      self.bot = bot






async def setup(bot):
  await bot.add_cog(Music(bot))