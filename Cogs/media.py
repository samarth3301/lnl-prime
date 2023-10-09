import discord
from discord.ext import commands
import datetime
import aiosqlite, pytz
from discord.ui import Button, View


from Extra import config


class Media(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(description="Media setup commands.", invoke_without_command=True)
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def media(self, ctx):
        await ctx.send_help(ctx.command)
    
    @media.group(description="Media channel setup commands.", invoke_without_command=True)
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def channel(self, ctx):
        await ctx.send_help(ctx.command)

    @media.group(description="Ignores user if user is having the roles.", invoke_without_command=True)
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def ignore(self, ctx):
        await ctx.send_help(ctx.command)


    @channel.command(name="add", description="Sets a channel for media where people can only send pictures and videos")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def add1(self, ctx, channel : discord.TextChannel = None):
        channel = channel or ctx.channel
        cursor = await self.bot.db.cursor()
        await cursor.execute("SELECT channel_id FROM Media WHERE guild_id = ?", (ctx.guild.id,))
        channels = await cursor.fetchall()

        if channel.id not in [int(i[0]) for i in channels]:
            if len(channels) == 2:
                await ctx.send(f"{config.Cross} | This server has reached maximum limit of media channels")
                return
            await cursor.execute("INSERT INTO Media(guild_id, channel_id) VALUES(?, ?)", (ctx.guild.id, channel.id))
            await ctx.send(f"{config.Tick} | Successfully added {channel.mention} to media channels.")
        else:
            await ctx.send(f"{config.Cross} | That channel is already a media channel")
        await self.bot.db.commit()

    
    @channel.command(name="remove", aliases=['rmv'],description="Removes a channel from media channels.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def remove1(self, ctx, channel : discord.TextChannel = None):
        channel = channel or ctx.channel

        cursor = await self.bot.db.cursor()
        await cursor.execute("SELECT channel_id FROM Media WHERE guild_id = ?", (ctx.guild.id,))
        channels = await cursor.fetchall()

        ch_ = [int(i[0]) for i in channels]

        if channel.id in ch_:
            await cursor.execute("DELETE FROM Media WHERE guild_id = ? AND channel_id = ?", (ctx.guild.id, channel.id))
            await ctx.send(f"{config.Tick} | Successfully removed {channel.mention} removed media channels.")
        else:
            await ctx.send(f"{config.Cross} | This channel isn't in the list of media channels")
        await self.bot.db.commit()

    @media.command(name="config",description="Shows the configuration of media system.", invoke_without_command=True)
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def config1(self, ctx):
        cur = await self.bot.db.cursor()

        await cur.execute("SELECT channel_id FROM Media WHERE guild_id = ?", (ctx.guild.id,))
        channel_ids = await cur.fetchall()

        await cur.execute("SELECT role_id FROM MediaWhitelist WHERE guild_id = ?", (ctx.guild.id,))
        role_ids = await cur.fetchall()

        embed = discord.Embed(title=f"{ctx.guild.name} Media Settings <:BlueModeration:1089506519076311052>", color=config.color)
        embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
        embed.timestamp = datetime.datetime.utcnow()

        embed.add_field(name="__Channels__", value="".join([f"<#{i[0]}>\n" for i in channel_ids] if channel_ids else "Not Set"))
        embed.add_field(name="__Ignored Roles__", value="".join([f"<@&{i[0]}>\n" for i in role_ids] if role_ids else "Not Set"))

        await ctx.send(embed=embed)

    @channel.command(name="reset",description="Resets media channels.", invoke_without_command=True)
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def reset1(self, ctx):
        cur = await self.bot.db.cursor()
        await cur.execute("SELECT channel_id FROM Media WHERE guild_id = ?", (ctx.guild.id,))
        channels = await cur.fetchall()

        if channels == []:
            await ctx.send(f"{config.Cross} | There is nothing to reset.")
            return

        class ConfirmationView(discord.ui.View):
            def __init__(self):
                super().__init__()
            
            @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
            async def callback(self, interaction: discord.Interaction, button: Button):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message(f"{config.Cross} | Its not your interaction.")
                    return
                await cur.execute("DELETE FROM Media WHERE guild_id = ?", (ctx.guild.id,))
                await interaction.message.delete()
                await ctx.send(f"{config.Tick} | Successfully reset media channels.")
                await interaction.client.db.commit()

            @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
            async def callback2(self, interaction: discord.Interaction, button: Button):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message(f"{config.Cross} | Its not your interaction.")
                    return
                await interaction.message.delete()
                await ctx.send(f"{ctx.author.mention} command execution cancelled.")

            async def on_timeout(self):
                if self.message is not None:
                    for i in self.children:
                        i.disabled = True
                    await self.message.edit(view=self)

        
        view = ConfirmationView()
        embed = discord.Embed(description="**Are you sure you want to reset media channels?**", color=config.color)
        view.message = await ctx.send(embed=embed, view=view)
        

    @ignore.command(name="add", description="Adds the role to ignored roles of Media channels.", invoke_without_command=True)
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def add2(self, ctx, role: discord.Role):
        c = await self.bot.db.cursor()

        await c.execute("SELECT role_id FROM MediaWhitelist WHERE guild_id = ?", (ctx.guild.id,))
        re = await c.fetchall()
        role_ids = [int(i[0]) for i in re]

        if role.id not in role_ids:
            if len(role_ids) == 3:
                await ctx.send(f"{config.Cross} | This server has reached the maximum limit for media ignore.")
                return
            await c.execute("INSERT INTO MediaWhitelist(guild_id, role_id) VALUES(?, ?)", (ctx.guild.id, role.id))
            await ctx.send(f"{config.Tick} | Successfully added {role.mention} to ignored roles.", allowed_mentions=discord.AllowedMentions.none())
        else:
            await ctx.send(f"{config.Cross} | That role is already ignored.")
        await self.bot.db.commit()

    @ignore.command(name="remove", aliases=['rmv'], description="Removes the role from ignored roles of Media channels.", invoke_without_command=True)
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def remove2(self, ctx, role: discord.Role):
        c = await self.bot.db.cursor()

        await c.execute("SELECT role_id FROM MediaWhitelist WHERE guild_id = ?", (ctx.guild.id,))
        re = await c.fetchall()
        role_ids = [int(i[0]) for i in re]

        if role.id in role_ids:
            await c.execute("DELETE FROM MediaWhitelist WHERE guild_id = ? AND role_id = ?", (ctx.guild.id, role.id))
            await ctx.send(f"{config.Tick} | Successfully removed {role.mention} from ignored roles.", allowed_mentions=discord.AllowedMentions.none())
        else:
            await ctx.send(f"{config.Cross} | That role is not ignored.")
        await self.bot.db.commit()

    @ignore.command(name="config",description="Shows the configuration of ignored roles of media channels.", invoke_without_command=True)
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def config2(self, ctx):
        cur = await self.bot.db.cursor()

        await cur.execute("SELECT role_id FROM MediaWhitelist WHERE guild_id = ?", (ctx.guild.id,))
        role_ids = await cur.fetchall()

        embed = discord.Embed(title=f"{ctx.guild.name} Media Roles Settings <:BlueModeration:1089506519076311052>", color=config.color)
        embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
        embed.timestamp = datetime.datetime.utcnow()

        embed.add_field(name="__Ignored Roles__", value="".join([f"<@&{i[0]}>\n" for i in role_ids] if role_ids else "Not Set"))

        await ctx.send(embed=embed)

    @ignore.command(name="reset",description="Resets media channel ignore roles.", invoke_without_command=True)
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def reset2(self, ctx):
        cur = await self.bot.db.cursor()
        await cur.execute("SELECT role_id FROM MediaWhitelist WHERE guild_id = ?", (ctx.guild.id,))
        roles = await cur.fetchall()

        if roles == []:
            await ctx.send(f"{config.Cross} | There is nothing to reset.")
            return

        class ConfirmationView(discord.ui.View):
            def __init__(self):
                super().__init__()
            
            @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
            async def callback(self, interaction: discord.Interaction, button: Button):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message(f"{config.Cross} | Its not your interaction.")
                    return
                await cur.execute("DELETE FROM MediaWhitelist WHERE guild_id = ?", (ctx.guild.id,))
                await interaction.message.delete()
                await ctx.send(f"{config.Tick} | Successfully reset media ignore roles.")
                await interaction.client.db.commit()
                self.stop()

            @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
            async def callback2(self, interaction: discord.Interaction, button: Button):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message(f"{config.Cross} | Its not your interaction.")
                    return
                await interaction.message.delete()
                await ctx.send(f"{ctx.author.mention} command execution cancelled.")
                self.stop()

            async def on_timeout(self):
                if self.message is not None:
                    for i in self.children:
                        i.disabled = True
                    await self.message.edit(view=self)
                    self.stop()
                self.stop()

        
        view = ConfirmationView()
        embed = discord.Embed(description="**Are you sure you want to reset media channel ignore roles?**", color=config.color)
        view.message = await ctx.send(embed=embed, view=view)
        await view.wait()

        





    @commands.Cog.listener("on_guild_channel_delete")
    async def MediaChannelRevoke(self, channel: discord.TextChannel):
        c = await self.bot.db.cursor()
        await c.execute("SELECT channel_id FROM Media WHERE guild_id = ? AND channel_id = ?", (channel.guild.id, channel.id))
        channels_ = await c.fetchall()

        if channels_ == []:
            return
        else:
            await c.execute("DELETE FROM Media WHERE channel_id = ? AND guild_id = ?", (channel.id, channel.guild.id))
        
        await self.bot.db.commit()








   














async def setup(bot):
    await bot.add_cog(Media(bot))