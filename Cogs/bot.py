from typing import Optional
import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
from discord import app_commands
import datetime, pytz, random, aiosqlite, time, typing, textwrap


from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

from Extra import config




class Bott(commands.Cog, name="Bot"):
    def __init__(self, bot):
        self.bot = bot
    def cog_load(self):
        self.PrefixRefresher.start()

        
    async def filter_badges(self, badges: typing.List[str]):
        txt = ""

        for b in badges:
            if b.lower().strip() == 'owner':
                txt += '<:owner:1117748748022456380> Owner\n'
            if b.lower().strip() == 'staff':
                txt += '<a:staff:1117748830226616330> Staff\n'
            if b.lower().strip() == 'friend':
                txt += '<:0f1cad44444e4e85b6c904753a86cbf5:1100122130672255066> Friend\n'
            if b.lower().strip() == 'vip':
                txt += '<:vip:1117749492062625833> VIP\n'
            if b.lower().strip() == 'premium':
                txt += '<a:diamond:1117749028457824278> Premium'

        return txt
        
        
        
        
        
        
        
        
        

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        cursor = await self.bot.db.cursor()
        sql = (f"INSERT INTO Prefix(guild_id, prefix) VALUES(?,?)")
        val = (guild.id, "$")
        await cursor.execute(sql, val)
        await self.bot.db.commit()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        cursor = await self.bot.db.cursor()
        await cursor.execute(f"DELETE FROM Prefix WHERE guild_id = ?", (guild.id,))
        await self.bot.db.commit()

    
    @tasks.loop(hours=60)
    async def PrefixRefresher(self):
        await self.bot.wait_until_ready()

        c = await self.bot.db.cursor()
        await c.execute("SELECT prefix, guild_id FROM Prefix")
        re = await c.fetchall()

        for i in re:
            g = self.bot.get_guild((int(i[1])))

            if g is None:
                await c.execute("DELETE FROM Prefix WHERE guild_id = ?", (i[1],))
        
        await self.bot.db.commit()





    @commands.hybrid_command(description="Change prefix of a server.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def prefix(self, ctx, prefix=None):
        cursor = await self.bot.db.cursor()
        await cursor.execute("SELECT prefix FROM Prefix WHERE guild_id = ?", (ctx.guild.id,))
        p = await cursor.fetchone()

        if prefix is None:
            await ctx.send(f"The prefix of this server is `{p[0]}`")
            return
        
        await cursor.execute(f"UPDATE Prefix SET prefix = ? WHERE guild_id = ?", (prefix, ctx.guild.id))
        await ctx.send(f"{config.Tick} | Sucessfully set prefix `{prefix}`")
        await self.bot.db.commit()
    

    @commands.hybrid_command(description="Shows bot's ping.")
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        
        st = time.time()
        c = await self.bot.db.cursor()
        await c.execute('SELECT * FROM Prefix')
        await c.fetchall()
        mt = time.time() - st
        db = round(mt * 1000)


        start_time = time.time()
        await ctx.typing()
        measured_time = time.time() - start_time
        final = round(measured_time * 1000)
 


        text = f":ping_pong: Pong! Websocket **{latency}ms** | API **{final}ms** | Database **{db}ms**"
            
        await ctx.send(text)


    @commands.hybrid_command(description="Shows bot's uptime.")
    async def uptime(self, ctx):
        delta_uptime = datetime.datetime.utcnow() - self.bot.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        
        await ctx.send(
        f"Uptime: {days} days, {hours} hours, {minutes} minutes and {seconds} seconds."
        )




    @commands.hybrid_command(aliases=['bi', 'stats'], description="Shows Bot's information")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def botinfo(self, ctx):
        await ctx.typing()
        cur = await self.bot.db.cursor()

        delta_uptime = datetime.datetime.utcnow() - self.bot.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        c = []
        for guild in self.bot.guilds:
            for ch in guild.voice_channels:
                c.append(ch)

        c2 = []
        for guild in self.bot.guilds:
            for ch2 in guild.text_channels:
                c2.append(ch2)

        c3 = []
        for guild in self.bot.guilds:
            for ch3 in guild.stage_channels:
                c3.append(ch3)



        embed = discord.Embed(title="Official Support Server", url=config.Support)
        embed.add_field(inline=False, name=f"__{self.bot.user.name} Information__",
        value=f"**Online Since:** {days} day(s), {hours} hour(s), {minutes} minute(s) and {seconds} second(s)\n**Servers:** {len(self.bot.guilds)}\n**Shards:** {len(self.bot.shards)}\n**Users** {len(self.bot.users)}\n**Commands:** Total {len(self.bot.commands)}\n**Total Channels** {len(list(self.bot.get_all_channels()))}\n**Version:** {self.bot.Version}")

        embed.add_field(name="__Channels__",
        value=f"{config.TextChannel} {int(len(c2))} | {config.VoiceChannel} {int(len(c))} | {config.StageChannel} {int(len(c3))}", inline=False)

        await cur.execute("SELECT user_id FROM Owner")
        re = await cur.fetchall()

        owners = None
        if re:
            owner_ids = [int(i[0]) for i in re]
            owners = []
            for i in owner_ids:
                u = await self.bot.fetch_user(i)
                owners.append(u)

        IDS = self.bot.owner_ids
        OWNERS = []
        for i in IDS:
            z = await self.bot.fetch_user(i)
            OWNERS.append(z)

        embed.add_field(
            name="Developers",
            value=f"[Krypton#0009](https://discord.com/users/1069332033928708206/)",
            inline=False
        )




        embed.color = config.color
        embed.set_footer(text="Powered by Lock N Loaded HQ", icon_url=self.bot.user.display_avatar.url)
        
        embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)











    @commands.hybrid_command(aliases=['inv'], description="Invite me.", hidden=True)
    async def invite(self, ctx):
        button = discord.ui.Button(label="Invite.",
         url=config.Invite,)
        button2 = discord.ui.Button(label="Support Server.",
        url=config.Support)
        button3 = discord.ui.Button(label="Vote me.",
        url=config.Vote)
        view = View().add_item(button)
        view.add_item(button2)
        view.add_item(button3)
        await ctx.send(view=view)


















    @commands.command(aliases=['pf', 'pr'])
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def profile(self, ctx: commands.Context, *, user: typing.Optional[discord.User]):
        user = user or ctx.author

        c = await self.bot.db.cursor()
        await c.execute("SELECT badge FROM badge where user_id = ?", (user.id,))
        re = await c.fetchall()

        await c.execute("select prime_count, tier, end_time from userpremium where user_id = ?", (user.id,))
        re2 = await c.fetchone()

        badges = "Looks like you don't have any badges!"

        if re is not None:
            badges = [i[0] for i in re]
            if re2:
                badges.append("premium")
            badges = await self.filter_badges(badges)
        
        prime_txt = "Oops! you have no premium!"
        if re2 is not None:
            end_time = f"<t:{re2[2]}:R>" if re2[2] != 'none' else "Lifetime."
            prime_count = re2[0]
            tier = re2[1] 

            prime_txt = f"**Ends:** {end_time}\n**Tier:** {tier}\n**Prime Count:** {prime_count}"
        

        embed = discord.Embed(color=config.color)
        embed.add_field(name="Badges", inline=False, value=badges)
        embed.add_field(name="Prime", inline=False, value=prime_txt)
        embed.set_author(name=user, icon_url=user.display_avatar.url)
        await ctx.send(embed=embed)










async def setup(bot):
    await bot.add_cog(Bott(bot)) 