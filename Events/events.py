import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
from discord import app_commands
import datetime, pytz, random, aiosqlite, time, aiohttp, logging

from Extra import config






   






class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embeds = []

    def cog_load(self):
        self.cd_mapping = commands.CooldownMapping.from_cooldown(1, 3, commands.BucketType.member)

        self.command_logger.start()







    @commands.Cog.listener("on_command")
    async def command_logger_embed(self, ctx):
        if self.bot.user.id != 1103964690498998274: return
        if ctx.interaction:
            ctx.message.content = '*Interaction Command*'

        embed = discord.Embed(
            description=f"**__Command:__** {ctx.command}\n\n**__Author:__** {ctx.message.author}\n**__Author ID:__** {ctx.message.author.id}\n\n**__Guild:__** {ctx.message.guild.name}\n**__Guild ID:__** {ctx.message.guild.id}\n\n**__Channel:__** {ctx.channel.mention}\n**__Channel ID:__** {ctx.channel.id}\n\n**__Message__**\n```\n{ctx.message.content}```\n\n**__Time:__** <t:{round(datetime.datetime.now().timestamp())}:R>\n**__Date__** {datetime.date}",
            color=config.color
        )
        self.embeds.append(embed)

    @tasks.loop(seconds=10)
    async def command_logger(self):
        if self.bot.user.id != 1103964690498998274: return
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(url="https://discord.com/api/webhooks/1117854939650216068/OLfVzH2l1NMpfUE6FbidKJjt2xtAW7cGys5YQn6WR6LZbaRwVqzfSJd4r82A6gDBMaBn", session=session)
            if len(self.embeds) == 0:
               return
            
            await webhook.send(embeds=self.embeds)

            self.embeds = []



    @commands.Cog.listener()
    async def on_message(self, message):
        bucket = self.cd_mapping.get_bucket(message)
        ratelimit = bucket.update_rate_limit()

        if ratelimit: return
        
        if message.content != self.bot.user.mention or message.author.bot: return
        
        cursor = await self.bot.db.execute(f"""SELECT prefix FROM Prefix WHERE guild_id = {message.guild.id}""")
        p = await cursor.fetchone()
        embed = discord.Embed(description=f"Hey!\nI am **{self.bot.user.name}**\nMy prefix for this server is `{p[0]}` Type `{p[0]}help` for information\n\nFacing issues? reach [Support Server]({config.Support})\nInvite me [here]({config.Invite}) ")

        button = discord.ui.Button(label="Invite Me.", url=config.Invite)
        button2 = discord.ui.Button(label="Support Server.", url=config.Support)

        embed.timestamp = datetime.datetime.utcnow()
        embed.color = config.color
        view = discord.ui.View().add_item(button).add_item(button2)
        embed.set_author(name=f"{message.author}", icon_url=message.author.display_avatar.url)
        await message.reply(embed=embed, view=view, mention_author=False)



















   
















    @commands.Cog.listener("on_guild_join")
    async def on_guild_join(self, guild :discord.Guild):
        c = await self.bot.db.cursor()
        await c.execute("SELECT guild_id FROM G_bl")
        re = await c.fetchall()

        guild_list = [int(i[0]) for i in re]

        if guild.id in guild_list:
            await guild.leave()




        embed = discord.Embed(title="Joined A Guild", description=f"**ID:** {guild.id}\n**Name:** {guild.name}\n**MemberCount:** {len(guild.members)}\n**Created:** <t:{int(guild.created_at.timestamp())}:R>")
        embed.add_field(name="Owner Information",
        value=f"**Name:** {guild.owner} ({guild.owner.id})\n**Created:** <t:{int(guild.owner.created_at.timestamp())}:R>", inline=False)
        embed.add_field(name=f"{self.bot.user.name} GuildCount",
        value=f"```fix\n{len(self.bot.guilds)}```", inline=False)
        embed.add_field(name=f"{self.bot.user.name} UserCount",
        value=f"```fix\n{len(self.bot.users)}```", inline=False)
        embed.add_field(name=f"Shard ID",
        value=f"```fix\n{guild.shard_id}```")
        embed.timestamp = datetime.datetime.utcnow()
        embed.color = config.color
        if guild.icon is not None:
            embed.set_thumbnail(url=guild.icon.url)
        if guild.banner is not None:
            embed.set_image(url=guild.banner.url)
        channel = self.bot.get_channel(1112015764350836786)
        await channel.send(embed=embed)



    



    @commands.Cog.listener("on_shard_connect")
    async def shard_connect(self, shard_id):
        print(f"Connected to Shard: {shard_id}")

    @commands.Cog.listener("on_shard_disconnect")
    async def shard_disconnect(self, shard_id):
        print(f"Disconnected from Shard: {shard_id}")



















async def setup(bot):
    await bot.add_cog(Events(bot))