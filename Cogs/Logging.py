import discord
from discord.ext import commands
import datetime
import aiosqlite
import pytz


from Extra import config






class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group(invoke_without_command=True, description="Logging commands.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def log(self, ctx):
        await ctx.send_help(ctx.command)

    @log.command(description="Set a channel for message logging", aliases=['msg'])
    async def message(self, ctx, channel: discord.TextChannel):
        cursor = await self.bot.db.cursor()
        await cursor.execute("select * from Log where guild_id = ?", (ctx.guild.id,))
        result = await cursor.fetchone()


        if result is not None:
            await cursor.execute(f"UPDATE Log SET log_msg = ? WHERE guild_id = ?", (channel.id, ctx.guild.id))
            await ctx.send(f"{config.Tick} | Successfully set {channel.mention} as Message Log.")
        else:
            await cursor.execute("INSERT INTO Log(log_msg, guild_id) VALUES(?, ?)", (channel.id, ctx.guild.id))
            await ctx.send(f"{config.Tick} | Successfully set {channel.mention} as Message Log.")
        await self.bot.db.commit()

    @log.command(description="Set a channel for moderation logging", aliases=['mod'])
    async def moderation(self, ctx, channel: discord.TextChannel):
        cursor = await self.bot.db.cursor()
        await cursor.execute("select * from Log where guild_id = ?", (ctx.guild.id,))
        result = await cursor.fetchone()


        if result is not None:
            await cursor.execute(f"UPDATE Log SET log_mod = ? WHERE guild_id = ?", (channel.id, ctx.guild.id))
            await ctx.send(f"{config.Tick} | Successfully set {channel.mention} as Moderation Log.")
        else:
            await cursor.execute("INSERT INTO Log(log_mod, guild_id) VALUES(?, ?)", (channel.id, ctx.guild.id))
            await ctx.send(f"{config.Tick} | Successfully set {channel.mention} as Moderation Log.")
        await self.bot.db.commit()

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        cursor = await self.bot.db.cursor()
        await cursor.execute(f"SELECT log_msg FROM Log WHERE guild_id = ?", (message.guild.id,))
        result = await cursor.fetchone()

        if result is None:
            return 
        elif message.author.bot:
            return 
        else:
            channel = self.bot.get_channel(int(result[0]))
            embed = discord.Embed(
                description=f"{config.Red} | **{message.author}** ({message.author.id}) Message Deleted.\n ```\n{message.content}```",
                color=config.color
            )
            embed.set_footer(
                text=self.bot.user.name,
                icon_url=self.bot.user.display_avatar.url
            )
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        cursor = await self.bot.db.cursor()
        await cursor.execute(f"SELECT log_msg FROM Log WHERE guild_id = ?", (before.guild.id,))
        result = await cursor.fetchone()

        if result is None:
            return 
        elif before.author.bot:
            return 
        else:
            embed = discord.Embed(
                description=f"{config.Red} | **{before.author}** ({before.author.id}) Message Edited.\nFrom ```\n{before.content}```\nTo\n```\n{after.content}```",
                color=config.color
            )
            embed.set_footer(
                text=self.bot.user.name,
                icon_url=self.bot.user.display_avatar.url
            )
            channel = self.bot.get_channel(int(result[0]))
            await channel.send(embed=embed)


    @commands.Cog.listener("on_audit_log_entry_create")
    async def ModLog(self, entry):
        c = await self.bot.db.cursor()
        
        if entry.action == discord.AuditLogAction.ban:
            time = f"<t:{round(entry.created_at.timestamp())}:R>"
            k = entry.target
            banned_user = await self.bot.fetch_user(k.id)
            guild = entry.guild
            author = entry.user
            reason = entry.reason

            await c.execute("SELECT log_mod FROM Log WHERE guild_id = ?", (guild.id,))
            channel_ = await c.fetchone()
            if channel_ is not None:
                channel = self.bot.get_channel(int(channel_[0]))
                await channel.send(f"{config.Red} | **{banned_user.name}#{banned_user.discriminator} ({banned_user.id})** was **Banned** by **{author} ({author.id})** {time}\n```\n{reason if reason is not None else 'No reason provided.'}```")

        if entry.action == discord.AuditLogAction.unban:
            time = f"<t:{round(entry.created_at.timestamp())}:R>"
            k = entry.target
            banned_user = await self.bot.fetch_user(k.id)
            guild = entry.guild
            author = entry.user
            reason = entry.reason

            await c.execute("SELECT log_mod FROM Log WHERE guild_id = ?", (guild.id,))
            channel_ = await c.fetchone()
            if channel_ is not None:
                channel = self.bot.get_channel(int(channel_[0]))
                await channel.send(f"{config.Red} | **{banned_user.name}#{banned_user.discriminator} ({banned_user.id})** was **Unbanned** by **{author} ({author.id})** {time}\n```\n{reason if reason is not None else 'No reason provided.'}```")
        
        if entry.action == discord.AuditLogAction.kick:
            time = f"<t:{round(entry.created_at.timestamp())}:R>"
            k = entry.target
            banned_user = await self.bot.fetch_user(k.id)
            guild = entry.guild
            author = entry.user
            reason = entry.reason

            await c.execute("SELECT log_mod FROM Log WHERE guild_id = ?", (guild.id,))
            channel_ = await c.fetchone()
            if channel_ is not None:
                channel = self.bot.get_channel(int(channel_[0]))
                await channel.send(f"{config.Red} | **{banned_user.name}#{banned_user.discriminator} ({banned_user.id})** was **Kicked** by **{author} ({author.id})** {time}\n```\n{reason if reason is not None else 'No reason provided.'}```")

        if entry.action == discord.AuditLogAction.member_update:
            if not entry.target.timed_out_until:

                time = f"<t:{round(entry.created_at.timestamp())}:R>"
                k = entry.target
                timed_out_user = await self.bot.fetch_user(k.id)
                guild = entry.guild
                author = entry.user
                reason = entry.reason

                await c.execute("SELECT log_mod FROM Log WHERE guild_id = ?", (guild.id,))
                channel_ = await c.fetchone()
                if channel_ is not None:
                    channel = self.bot.get_channel(int(channel_[0]))
                    await channel.send(f"{config.Red} | **{timed_out_user} ({timed_out_user.id})** was **Untimed Out** by **{author} ({author.id})** {time}\n```\n{reason if reason is not None else 'No reason provided.'}```")

            elif entry.target.timed_out_until:

                time = f"<t:{round(entry.created_at.timestamp())}:R>"
                k = entry.target
                timed_out_user = await self.bot.fetch_user(k.id)
                guild = entry.guild
                author = entry.user
                reason = entry.reason

                await c.execute("SELECT log_mod FROM Log WHERE guild_id = ?", (guild.id,))
                channel_ = await c.fetchone()
                if channel_ is not None:
                    channel = self.bot.get_channel(int(channel_[0]))
                    await channel.send(f"{config.Red} | **{timed_out_user} ({timed_out_user.id})** was **Timed Out** by **{author} ({author.id})** {time}\n```\n{reason if reason is not None else 'No reason provided.'}```")


                



































    @commands.Cog.listener("on_guild_channel_delete")
    async def LoggingChannelChecker(self, channel: discord.TextChannel):
        c = await self.bot.db.cursor()
        await c.execute("SELECT log_mod, log_msg FROM Log WHERE guild_id = ?", (channel.guild.id,))
        channel_DB = await c.fetchone()

        if channel_DB is not None:
            if channel.id in [int(i[0]) for i in channel_DB]:
                if channel.id == channel_DB[0]:
                    await c.execute("UPDATE Log SET log_mod = NULL WHERE guild_id = ?", (channel.guild.id,))
                else:
                    await c.execute("UPDATE Log SET log_msg = NULL WHERE guild_id = ?", (channel.guild.id,))

        await self.bot.db.commit()












async def setup(bot):
    await bot.add_cog(Logging(bot))