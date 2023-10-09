import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
from discord import app_commands
import datetime, pytz, random, aiosqlite, time, aiohttp

from Extra import config






   








class Events2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # def cog_load(self):
    #     self.command_logger.start()



    @commands.Cog.listener("on_message")
    async def MediaChannelMessageDelete(self, message: discord.Message):
        if str(message.channel.type) == 'private':
            return
        if type(message.author) == discord.User:
            return
        if message.author.bot:
            return
        
        cur = await self.bot.db.cursor()
        await cur.execute("SELECT channel_id FROM Media WHERE guild_id = ?", (message.guild.id,))
        channel_ids_raw = await cur.fetchall()

        await cur.execute("SELECT role_id FROM MediaWhitelist WHERE guild_id = ?", (message.guild.id,))
        role_ids_raw = await cur.fetchall()

        role_ids = [int(i[0]) for i in role_ids_raw]
        
        channel_ids = [int(i[0]) for i in channel_ids_raw]

        IDS = [int(i.id) for i in message.author.roles]
        
        for roleids in role_ids:
            if roleids in IDS:
                return
        if message.channel.id not in channel_ids:
            return
        if not message.attachments:
            await message.delete()





    @commands.Cog.listener("on_message")
    async def AFKMessage(self, message: discord.Message):
        if message.author.bot or str(message.channel.type) == 'private':
            return
        
        cur = await self.bot.db.cursor()
        await cur.execute("SELECT user_id, guild_id, reason FROM AFK")
        re = await cur.fetchall()

        if re == []:
            return
        
        for i in re:
            user = self.bot.get_user(int(i[0]))
            if user is None:
                await cur.execute("DELETE FROM AFK WHERE user_id = ? AND guild_id = ?", (i[0], i[1]))
                continue

            if message.guild.id == int(i[1]):
                if message.author.id == user.id:                
                    await cur.execute("DELETE FROM AFK WHERE guild_id = ? AND user_id = ?", (message.guild.id, user.id))
                    await message.channel.send(f"**{message.author}**, Your AFK has been removed.", delete_after=5)
                    print(f'AFK Removed - {user} ({user.id})')

                if user.mention in message.content or str(user.name).lower() in (message.content).lower():
                    await message.channel.send(f"**{user}** is AFK - {i[2]}", allowed_mentions=discord.AllowedMentions.none())

                if message.reference:
                    if message.reference.resolved.author.id == user.id:
                        await message.channel.send(f"**{user}** is AFK - {i[2]}", allowed_mentions=discord.AllowedMentions.none())
                
            

        await self.bot.db.commit()



    @commands.Cog.listener('on_message')
    async def AutoResponder(self, message: discord.Message):
        if message.author.bot or str(message.channel.type) == 'private': return

        c = await self.bot.db.cursor()
        await c.execute("SELECT name, content FROM auto_res WHERE guild_id = ?", (message.guild.id,))
        re = await c.fetchall()

        if re == []: return

        for m in re:
            if m[0].lower() == message.content.lower():
                await message.channel.send(m[1])

        await self.bot.db.commit()





























async def setup(bot):
    await bot.add_cog(Events2(bot))