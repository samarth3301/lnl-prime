import discord
from discord.ext import commands
import datetime
import pytz
import aiosqlite
from discord.ui import Select, Button, View
import asyncio, json



from Extra import config
from Views.embed import EmbedBuilder





class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True, description="Welcome feature information.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def greet(self, ctx):
        await ctx.send_help(ctx.command)

    @greet.group(invoke_without_command=True, description="Welcome embed commands.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def embed(self, ctx):
        await ctx.send_help(ctx.command)

    @greet.group(description="Setups welcome channel.", invoke_without_command=True)
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild= True))
    async def channel(self, ctx):
        await ctx.send_help(ctx.command)

    @channel.command(name="add", description="Setup welcome channel.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild= True))
    async def ch_add(self, ctx, channel: discord.TextChannel):
        cursor = await self.bot.db.cursor()
        await cursor.execute(f"SELECT channel_id FROM wlc_ch WHERE guild_id = ?", (ctx.guild.id,))
        result = await cursor.fetchall()

        if result != []:
            ch_list = [int(i[0]) for i in result]
            if len(ch_list) == 3:
                return await ctx.send(f"{config.Cross} | This server has reached the maximum limit.")
            if channel.id in ch_list:
                return await ctx.send(f"{config.Cross} | This channel is already in the list of greet channels.")
            
        await cursor.execute("INSERT INTO wlc_ch(guild_id, channel_id) VALUES(?, ?)", (ctx.guild.id, channel.id))
        await ctx.send(f"{config.Tick} | Successfully added {channel.mention} to greet channels")

    @channel.command(name="remove", description="Setup welcome channel.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild= True))
    async def ch_rmv(self, ctx, channel: discord.TextChannel):
        cursor = await self.bot.db.cursor()
        await cursor.execute(f"SELECT channel_id FROM wlc_ch WHERE guild_id = ?", (ctx.guild.id,))
        result = await cursor.fetchall()

        if result != []:
            ch_list = [int(i[0]) for i in result]
            if channel.id not in ch_list:
                return await ctx.send(f"{config.Cross} | This channel is not in the list of greet channels.")
            
        await cursor.execute("DELETE FROM wlc_ch WHERE guild_id = ? AND channel_id = ?", (ctx.guild.id, channel.id))
        await ctx.send(f"{config.Tick} | Successfully removed {channel.mention} from greet channels")

    @greet.command(description="Setup welcome message.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def message(self, ctx, *, message):
        cursor = await self.bot.db.cursor()
        await cursor.execute(f"SELECT msg FROM Welcome WHERE guild_id = ?", (ctx.guild.id,))
        result = await cursor.fetchone()
        await cursor.execute("SELECT channel_id FROM wlc_ch WHERE guild_id = ?", (ctx.guild.id,))
        CDB = await cursor.fetchall()

        if CDB == []:
            await ctx.send(f"{config.Cross} | Oops, Kindly set your welcome channel first.")
            return
        if result is None:
            sql = ("INSERT INTO Welcome(guild_id, msg, delete_after) VALUES(?, ?, ?)")
            val = (ctx.guild.id, message, 0)
            await ctx.send(f"{config.Tick} | Successfully set welcome message to `{message}`")
        elif result is not None:
            sql = ("UPDATE Welcome SET msg = ? WHERE guild_id = ?")
            val = (message, ctx.guild.id)
            await ctx.send(f"{config.Tick} | Successfully set welcome message to `{message}`")
        await cursor.execute(sql, val)
        await self.bot.db.commit()

    @greet.command(description="Shows all the variables that can be used in the welcome message.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def variables(self, ctx):
        embed = discord.Embed(description="""
**Here are some keywords that you can use in your welcome message.**
```fix
User Mention = {UserMention}
User Name = {UserName}
User Id = {UserId}
User Discriminator = {UserDiscriminator}
Total Server Members = {UserCount}
Server Name = {GuildName}
User Created Timestamp = {UserCreatedAt}
User Joined Timestamp = {UserJoinedAt}```
""", color=config.color)    
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)
        embed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)


    @greet.command(name="config", description="View configuration of welcome system.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def configuration(self, ctx):
        cur = await self.bot.db.cursor()
        await cur.execute("SELECT msg, delete_after FROM Welcome WHERE guild_id = ?", (ctx.guild.id,))
        re = await cur.fetchone()

        await cur.execute("SELECT channel_id FROM wlc_ch WHERE guild_id = ?", (ctx.guild.id,))
        channels = await cur.fetchall()

        await cur.execute("Select embed, state, ping FROM Embed WHERE guild_id = ?", (ctx.guild.id,))
        embed_raw = await cur.fetchone()

        embed_ = None
        if embed_raw is not None:
           dict0 = json.loads(embed_raw[0])
           embed_ = discord.Embed.from_dict(dict0)


        if not re and not channels:
            mf = "Not Set"
            cf = "Not Set"
        else:
            cf = ", ".join([f"<#{i[0]}>" for i in channels if i is not None] if len(channels) != 0 else 'Not Set')
            mf = re[0] if re and re[0] else "Not Set"

        da = re[1] + " seconds" if re else 'Disabled'
        if da == '0 seconds':
            da = 'Disabled'

        if embed_:
            if not embed_.description:
                embed_.description = "Not Set"
            else:
                embed_.description = f"\n```\n{embed_.description}```"

        embed = discord.Embed(description=f"**__Greet Configuration__**\n\n**Channels:** {cf}\n**Message**\n```\n{mf}```\n**Auto Delete:** {da}", color=config.color)

        if embed_:
            embed.add_field(
                name="__Embed Configuration__",
                value=f"**Title:** {embed_.title if embed_.title is not None else 'Not Set'}\n**Description:** {embed_.description}\n**Image URL:** {embed_.image.url if embed_.image is not None else 'Not Set'}\n**Thumbnail URL:** {embed_.thumbnail.url if embed_.thumbnail is not None else 'Not Set'}\n**Color:** {embed_.color if embed_.color != config.color else 'Default Color'}\n\n**Embed Ping:** {'Enabled' if embed_raw[2] == 'enabled' else 'Disabled'}\n**Embed State:** {'Enabled' if embed_raw[1] == 'enabled' else 'Disabled'}",
                inline=False
            )

        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
        if ctx.guild.icon:
           embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url)
        else:
            embed.set_author(name=ctx.guild.name, icon_url=ctx.author.display_avatar.url)
        embed.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=embed)

    @greet.command(name="reset", description="View configuration of welcome system.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def reset(self, ctx):
        cur = await self.bot.db.cursor()
        await cur.execute("SELECT * FROM Welcome WHERE guild_id = ?", (ctx.guild.id,))
        data = await cur.fetchone()
        if data is None:
            await ctx.send(f"{config.Cross} | There is nothing to reset.")
            return
        
        class ButtonView(View):
            def __init__(self):
                super().__init__(timeout=30)

            @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
            async def callback1(self, interaction: discord.Interaction, button: Button):
                if ctx.author != interaction.user:
                    await interaction.response.send_message(f"{config.Cross} | Its not your interaction.", ephemeral=True)
                    return
                await cur.execute(f"DELETE FROM Welcome WHERE guild_id = ?", (ctx.guild.id,))
                await interaction.message.delete()
                await ctx.send(f"{config.Tick} | Successfully reset the welcome system.")
                self.stop()

            @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
            async def callback2(self, interaction: discord.Interaction, button: Button):
                if ctx.author != interaction.user:
                    await interaction.response.send_message(f"{config.Cross} | Its not your interaction.", ephemeral=True)
                    return
                await interaction.message.delete()
                await ctx.send(f"{ctx.author.mention} command execution cancelled.")
                self.stop()

            async def on_timeout(self):
                try:
                   await self.message.delete()
                except:
                    pass
                await ctx.send(f"{ctx.author.mention} Alright, I will not reset the welcome message")
                self.stop()

        embed = discord.Embed(description="**Are you sure you want to reset the welcome system?**", color=config.color)
        view = ButtonView()
        view.message = await ctx.send(embed=embed, view=view)
        await view.wait()
        await self.bot.db.commit()

    @greet.command(description="Test your welcome message.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild= True))
    async def test(self, ctx):
        cursor = await self.bot.db.cursor()
        await cursor.execute(f"SELECT channel_id FROM wlc_ch WHERE guild_id = ?", (ctx.guild.id,))
        result = await cursor.fetchall()

        await cursor.execute(f"SELECT msg, delete_after FROM Welcome WHERE guild_id = ?", (ctx.guild.id,))
        result2 = await cursor.fetchone()

        await cursor.execute("SELECT embed, state, ping FROM Embed WHERE guild_id = ?", (ctx.guild.id,))
        embed_ = await cursor.fetchone()

        if result == []:
            await ctx.send(f"{config.Cross} | Welcome has not been set in this server.")
            return
        
        elif result2 is None and embed_ is None:
            await ctx.send(f"{config.Cross} | Please setup your welcome message first.")
            return
        
        channels = [self.bot.get_channel(int(i[0])) for i in result]
        da = None

        if result2 is not None:
            da = int(result2[1]) if int(result2[1]) != 0 else None

        if embed_ is not None:
            if embed_[1] == 'enabled':
                em_dict = json.loads(embed_[0])
                embed = discord.Embed.from_dict(em_dict)
                embed.set_author(
                    name=ctx.author,
                    icon_url=ctx.author.display_avatar.url
                )
                embed.timestamp = datetime.datetime.now()
                try:
                    if embed.title is not None:
                        embed.title = embed.description.format(UserName=ctx.author.name, UserId=ctx.author.id, UserDiscriminator=ctx.author.discriminator, UserCount=len(ctx.author.guild.members), GuildName=ctx.author.guild.name, UserCreatedAt=f"<t:{round(ctx.author.created_at.timestamp())}:R>", UserJoinedAt=f"<t:{round(ctx.author.joined_at.timestamp())}:R>", UserMention=ctx.author.mention)

                    if embed.description is not None:
                        embed.description = embed.description.format(UserName=ctx.author.name, UserId=ctx.author.id, UserDiscriminator=ctx.author.discriminator, UserCount=len(ctx.author.guild.members), GuildName=ctx.author.guild.name, UserCreatedAt=f"<t:{round(ctx.author.created_at.timestamp())}:R>", UserJoinedAt=f"<t:{round(ctx.author.joined_at.timestamp())}:R>", UserMention=ctx.author.mention)

                except Exception as e:
                    embed = discord.Embed(description=f"Oops, looks like an error occured while sending the message. The reason maybe because you've put wrong variable in the message, please check once and try again.\nIf you are still facing issues please reach [Support Server]({config.Support}) with the following error.\n\n```py\n{e}```", color=config.color)
                    embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
                    await ctx.send(f"{ctx.author.mention}", embed=embed)
                    return
                if embed_[2] == 'enabled':
                    for channel in channels:
                        await channel.send(ctx.author.mention, embed=embed, delete_after=da)
                else:
                    for channel in channels:
                        await channel.send(embed=embed, delete_after=da)
                await ctx.send(f"{config.Tick} | Message has been sent.")
                return
                
            
        try:
            if result2 is not None:
                for channel in channels:
                    await channel.send(str(result2[0]).format(UserName=ctx.author.name, UserId=ctx.author.id, UserDiscriminator=ctx.author.discriminator, UserCount=len(ctx.author.guild.members), GuildName=ctx.author.guild.name, UserCreatedAt=f"<t:{int(ctx.author.created_at.timestamp())}:R>", UserJoinedAt=f"<t:{round(ctx.author.joined_at.timestamp())}:R>", UserMention=ctx.author.mention), delete_after=da)
            else:
                return await ctx.send(f"{config.Cross} | Please setup your welcome message/embed first.")
        except Exception as e:
            embed = discord.Embed(description=f"Oops, looks like an error occured while sending the message. The reason maybe because you've put wrong variable in the message, please check once and try again.\nIf you are still facing issues please reach [Support Server]({config.Support}) with the following error.\n\n```py\n{e}```", color=config.color)
            embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
            await ctx.send(f"{ctx.author.mention}", embed=embed)
            return
        await ctx.send(f"{config.Tick} | Messages has been sent.")

    @greet.command(description="Sets a time to delete the greet message. | Set `0` if you don't want to delete.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def autodel(self, ctx, seconds):
        c = await self.bot.db.cursor()
        await c.execute("SELECT delete_after FROM Welcome WHERE guild_id = ?", (ctx.guild.id,))
        al = await c.fetchone()

        try:
            int(seconds)
        except ValueError:
            return await ctx.send(f"{config.Cross} | Improper input. Ex - `greet autodel 3`")

        if int(seconds) > 10:
            return await ctx.send(f"{config.Cross} | Seconds must be less then 10 seconds.")
        if int(seconds) < 3 and int(seconds) != 0:
            return await ctx.send(f"{config.Cross} | Seconds must be `0` or minimum `3`.")
        
        if int(seconds) != 0:
            if al is not None:
                await c.execute("UPDATE Welcome SET delete_after = ? WHERE guild_id = ?", (int(seconds), ctx.guild.id))
                await ctx.send(f"{config.Tick} | Successfully set `{seconds}` seconds for greet auto deletion.")
            else:
                await c.execute("INSERT INTO Welcome(delete_after, guild_id) VALUES(?,?)", (int(seconds), ctx.guild.id))
                await ctx.send(f"{config.Tick} | Successfully set `{seconds}` seconds for greet auto deletion.")
        else:
            if al is not None:
                await c.execute("UPDATE Welcome SET delete_after = ? WHERE guild_id = ?", (int(seconds), ctx.guild.id))
                await ctx.send(f"{config.Tick} | Successfully disable greet auto deletion.")
            else:
                await c.execute("INSERT INTO Welcome(delete_after, guild_id) VALUES(?,?)", (int(seconds), ctx.guild.id))
                await ctx.send(f"{config.Tick} | Successfully disable greet auto deletion.")

        await self.bot.db.commit()

    @embed.command(description="Setups an embed for welcome message")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def setup(self, ctx):
        cur = await self.bot.db.cursor()
        await cur.execute("SELECT embed FROM Embed WHERE guild_id = ?", (ctx.guild.id,))
        re = await cur.fetchone()


        if re is not None:
            embed_dict = json.loads(re[0])
            embed = discord.Embed.from_dict(embed_dict)
        else:
            embed = discord.Embed(
                title="Title",
                description="Description",
                color=config.color
            )

        e = EmbedBuilder(
            bot=self.bot,
            embed=embed
            )
        e.author = ctx.author
        e.message = await ctx.send(embed=embed, view=e)
        await e.wait()

    @embed.command(description="Toggles embed of greet message.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def toggle(self, ctx):
        c = await self.bot.db.cursor()
        await c.execute("SELECT state FROM Embed WHERE guild_id = ?", (ctx.guild.id,))
        state = await c.fetchone()

        if state is None:
            return await ctx.send(f"{config.Cross} | Oops, Kindly setup your embed first.")
        
        if state[0] == "disabled":
            await c.execute("UPDATE Embed SET state = ? WHERE guild_id = ?", ("enabled", ctx.guild.id))
            await ctx.send(f"{config.Tick} | Alright, I've enabled the the embed. Now greet messages will be sent on embeds.")
        else: 
            await c.execute("UPDATE Embed SET state = ? WHERE guild_id = ?", ("disabled", ctx.guild.id))
            await ctx.send(f"{config.Tick} | Alright, I've disabled the the embed. Now greet messages will be sent normally.")
            
        await self.bot.db.commit()

    @embed.command(description="Toggles embed ping of greet message.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def ping(self, ctx):
        c = await self.bot.db.cursor()
        await c.execute("SELECT ping FROM Embed WHERE guild_id = ?", (ctx.guild.id,))
        ping = await c.fetchone()

        if ping is None:
            await ctx.send(f"{config.Cross} | Oops, Kindly setup your embed first.")
        if ping[0] == "disabled":
            await c.execute("UPDATE Embed SET ping = ? WHERE guild_id = ?", ("enabled", ctx.guild.id))
            await ctx.send(f"{config.Tick} | Alright, I've enabled the the embed ping. Now the users will get greet pings.")
        else: 
            await c.execute("UPDATE Embed SET ping = ? WHERE guild_id = ?", ("disabled", ctx.guild.id))
            await ctx.send(f"{config.Tick} | Alright, I've disabled the the embed ping. Now the users will not get pinged.")
            
        await self.bot.db.commit()

    @embed.command(name="reset", description="Resets embed of welcome message.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def reset2(self, ctx):
        c = await self.bot.db.cursor()
        await c.execute("SELECT embed FROM Embed WHERE guild_id = ?", (ctx.guild.id,))
        embed = await c.fetchone()

        if embed is None:
            await ctx.send(f"{config.Cross} | There is no embed to reset.")
            return
        
        class ConfirmationView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=30)

            @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
            async def ConfirmCallback(self, intr: discord.Interaction, btn: discord.Button):
                if intr.user != ctx.author:
                    await intr.response.send_message(f"{config.Cross} | Its not your interaction.", ephemeral=True)
                    return
                await intr.message.delete()
                await c.execute(f"DELETE FROM Embed WHERE guild_id = ?", (ctx.guild.id,))
                await ctx.send(f"{config.Tick} | Successfully reset the greet embed.")
                self.stop()

            @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
            async def CancelCallback(self, intr: discord.Interaction, btn: discord.Button):
                if intr.user != ctx.author:
                    await intr.response.send_message(f"{config.Cross} | Its not your interaction.", ephemeral=True)
                    return
                await intr.message.delete()
                await ctx.send(f"{ctx.author.mention} command execution cancelled.")

            async def on_timeout(self):
                if ctx.channel or self.message is None:
                    self.stop()
                    return

                await self.message.delete()
                await ctx.send(f"{ctx.author.mention} Alright, I will not reset the embed.")
                self.stop()
        
        embed = discord.Embed(description="**Are you sure you want to reset greet embed?**", color=config.color)
        view = ConfirmationView()
        view.message = await ctx.send(embed=embed, view=view)
        await view.wait()
        await self.bot.db.commit()











    @commands.group(description="Autorole commands.", invoke_without_command=True)
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def autorole(self, ctx):
        await ctx.send_help(ctx.command)
   
    @autorole.group(description="Set autorole for bots.", invoke_without_command=True)
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def bots(self, ctx):
        await ctx.send_help(ctx.command)

    @autorole.group(description="Set autorole for humans.", invoke_without_command=True)
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def humans(self, ctx):
        await ctx.send_help(ctx.command)

    @bots.command(name="add", description="Add role to list of autoroles for bot users.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def add1(self, ctx, role: discord.Role):
        cur = await self.bot.db.cursor()
        await cur.execute("SELECT role_id FROM Autorole WHERE guild_id = ?", (ctx.guild.id,))
        result = await cur.fetchall()
        await cur.execute("SELECT role_id FROM Autorole WHERE guild_id = ?", (ctx.guild.id,))
        roledb = await cur.fetchall()

        if roledb is not None:
            if len(result) == 2:
                await ctx.send(f"{config.Cross} | This server has reached maximum limit. No more autorole for bots can be added.", allowed_mentions=discord.AllowedMentions.none())
                return
            if str(role.id) in [str(i[0]) for i in roledb]:
                await ctx.send(f"{config.Cross} | That role is already in the list of autorole.", allowed_mentions=discord.AllowedMentions.none())
                return
            if len(result) == 0:
                await cur.execute(f"INSERT INTO Autorole(role_id, guild_id) VALUES(?, ?)", (role.id, ctx.guild.id))
                await ctx.send(f"{config.Tick} | Successfully added {role.mention} to bot autoroles.", allowed_mentions=discord.AllowedMentions.none())
            if len(result) == 1:
                await cur.execute(f"INSERT INTO Autorole(role_id, guild_id) VALUES(?, ?)", (role.id, ctx.guild.id))
                await ctx.send(f"{config.Tick} | Successfully added {role.mention} to bot autoroles.", allowed_mentions=discord.AllowedMentions.none())
        await self.bot.db.commit()

    @bots.command(name="remove", description="Remove a role from autoroles for bot users.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def remove1(self, ctx, role: discord.Role):
        cur = await self.bot.db.cursor()
        await cur.execute("SELECT * FROM Autorole WHERE guild_id = ?", (ctx.guild.id,))
        result = await cur.fetchall()
        await cur.execute("SELECT role_id FROM Autorole WHERE guild_id = ?", (ctx.guild.id,))
        roledb = await cur.fetchall()
        print(result)

        if str(role.id) in [i[0] for i in roledb]:
            if result[0][1] == str(role.id):
                await cur.execute(f"DELETE FROM Autorole WHERE guild_id = ? AND role_id = ?", (ctx.guild.id, role.id))
                await ctx.send(f"{config.Tick} | Successfully removed {role.mention} from bot autoroles.", allowed_mentions=discord.AllowedMentions.none())
            elif result[1][1] == str(role.id):
                await cur.execute(f"DELETE FROM Autorole WHERE guild_id = ? AND role_id = ?", (ctx.guild.id, role.id))
                await ctx.send(f"{config.Tick} | Successfully removed {role.mention} from bot autoroles.", allowed_mentions=discord.AllowedMentions.none())
        else:
            await ctx.send(f"{config.Cross} | {role.mention} is not in the list of bot autoroles.", allowed_mentions=discord.AllowedMentions.none())
        await self.bot.db.commit()

    @humans.command(name="add", description="Add role to list of autoroles for human users.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def add2(self, ctx, role: discord.Role):
        cur = await self.bot.db.cursor()
        await cur.execute("SELECT role_id FROM AutoroleHuman WHERE guild_id = ?", (ctx.guild.id,))
        result = await cur.fetchall()
        await cur.execute("SELECT role_id FROM AutoroleHuman WHERE guild_id = ?", (ctx.guild.id,))
        roledb = await cur.fetchall()

        if roledb is not None:
            if len(result) == 4:
                await ctx.send(f"{config.Cross} | This server has reached maximum limit. No more autorole for bots can be added.", allowed_mentions=discord.AllowedMentions.none())
                return
            if str(role.id) in [str(i[0]) for i in roledb]:
                await ctx.send(f"{config.Cross} | That role is already in the list of Human autoroles.", allowed_mentions=discord.AllowedMentions.none())
                return
            if len(result) == 0:
                await cur.execute(f"INSERT INTO AutoroleHuman(role_id, guild_id) VALUES(?, ?)", (role.id, ctx.guild.id))
                await ctx.send(f"{config.Tick} | Successfully added {role.mention} to human autoroles.", allowed_mentions=discord.AllowedMentions.none())
            if len(result) == 1:
                await cur.execute(f"INSERT INTO AutoroleHuman(role_id, guild_id) VALUES(?, ?)", (role.id, ctx.guild.id))
                await ctx.send(f"{config.Tick} | Successfully added {role.mention} to human autoroles.", allowed_mentions=discord.AllowedMentions.none())
            if len(result) == 2:
                await cur.execute(f"INSERT INTO AutoroleHuman(role_id, guild_id) VALUES(?, ?)", (role.id, ctx.guild.id))
                await ctx.send(f"{config.Tick} | Successfully added {role.mention} to human autoroles.", allowed_mentions=discord.AllowedMentions.none())
            if len(result) == 3:
                await cur.execute(f"INSERT INTO AutoroleHuman(role_id, guild_id) VALUES(?, ?)", (role.id, ctx.guild.id))
                await ctx.send(f"{config.Tick} | Successfully added {role.mention} to human autoroles.", allowed_mentions=discord.AllowedMentions.none())
        else:
            await ctx.send(f"{config.Cross} | That role is already in list of human autoroles.")
        await self.bot.db.commit()

    @humans.command(name="remove", description="Remove a role from autoroles for human users.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def remove2(self, ctx, role: discord.Role):
        cur = await self.bot.db.cursor()
        await cur.execute("SELECT * FROM AutoroleHuman WHERE guild_id = ?", (ctx.guild.id,))
        result = await cur.fetchall()
        await cur.execute("SELECT role_id FROM AutoroleHuman WHERE guild_id = ?", (ctx.guild.id,))
        roledb = await cur.fetchall()
        print(result)

        if str(role.id) in [i[0] for i in roledb]:
            if result[0][1] == str(role.id):
                await cur.execute(f"DELETE FROM AutoroleHuman WHERE guild_id = ? AND role_id = ?", (ctx.guild.id, role.id))
                await ctx.send(f"{config.Tick} | Successfully removed {role.mention} from human autoroles.", allowed_mentions=discord.AllowedMentions.none())
            elif result[1][1] == str(role.id):
                await cur.execute(f"DELETE FROM AutoroleHuman WHERE guild_id = ? AND role_id = ?", (ctx.guild.id, role.id))
                await ctx.send(f"{config.Tick} | Successfully removed {role.mention} from human autoroles.", allowed_mentions=discord.AllowedMentions.none())
            elif result[2][1] == str(role.id):
                await cur.execute(f"DELETE FROM AutoroleHuman WHERE guild_id = ? AND role_id = ?", (ctx.guild.id, role.id))
                await ctx.send(f"{config.Tick} | Successfully removed {role.mention} from human autoroles.", allowed_mentions=discord.AllowedMentions.none())
            elif result[3][1] == str(role.id):
                await cur.execute(f"DELETE FROM AutoroleHuman WHERE guild_id = ? AND role_id = ?", (ctx.guild.id, role.id))
                await ctx.send(f"{config.Tick} | Successfully removed {role.mention} from human autoroles.", allowed_mentions=discord.AllowedMentions.none())
            elif result[4][1] == str(role.id):
                await cur.execute(f"DELETE FROM AutoroleHuman WHERE guild_id = ? AND role_id = ?", (ctx.guild.id, role.id))
                await ctx.send(f"{config.Tick} | Successfully removed {role.mention} from human autoroles.", allowed_mentions=discord.AllowedMentions.none())
        else:
            await ctx.send(f"{config.Cross} | {role.mention} is not in the list of autoroles.", allowed_mentions=discord.AllowedMentions.none())
        await self.bot.db.commit()


    @autorole.command(name="config", description="View the configuration of autoroles in the server.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def autorole_config(self, ctx):
        cur = await self.bot.db.cursor()
        await cur.execute("SELECT role_id FROM AutoroleHuman WHERE guild_id = ?", (ctx.guild.id,))
        Hroles = await cur.fetchall()
        await cur.execute("SELECT role_id FROM Autorole WHERE guild_id = ?", (ctx.guild.id,))
        Broles = await cur.fetchall()

        embed = discord.Embed(title=f"{ctx.guild.name} Autorole Settings <:BlueModeration:1089506519076311052>", color=config.color)
        embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
        embed.timestamp = datetime.datetime.utcnow()

        embed.add_field(name="__Humans__", value="".join([f"<@&{i[0]}>\n" for i in Hroles] if Hroles else "Not Set"))
        embed.add_field(name="__Bots__", value="".join([f"<@&{i[0]}>\n" for i in Broles] if Broles else "Not Set"))

        await ctx.send(embed=embed)














    @commands.Cog.listener("on_guild_channel_delete")
    async def GreetChannelRevoke(self, channel: discord.TextChannel):
        c = await self.bot.db.cursor()
        await c.execute("SELECT channel_id FROM wlc_ch WHERE channel_id = ?", (channel.id,))
        channels__ = await c.fetchall()

        channels = [int(i[0]) for i in channels__]

        if channel.id in channels:
            await c.execute("DELETE FROM wlc_ch WHERE channel_id = ?", (channel.id,))
            print(f"Greet Channel Cleared - {channel.id}, Guild - {channel.guild.id}")

        await self.bot.db.commit()















    @commands.Cog.listener("on_member_join")
    async def member_join_message(self, member :discord.Member):
        cursor = await self.bot.db.cursor()
        await cursor.execute(f"SELECT channel_id FROM wlc_ch WHERE guild_id = ?", (member.guild.id,))
        result = await cursor.fetchall()

        await cursor.execute(f"SELECT msg, delete_after FROM Welcome WHERE guild_id = ?", (member.guild.id,))
        result2 = await cursor.fetchone()

        await cursor.execute("SELECT embed, state, ping FROM Embed WHERE guild_id = ?", (member.guild.id,))
        embed_ = await cursor.fetchone()

        if result == []:
            return
        elif result2 is None and embed_ is None:
            return
        
        channels = [self.bot.get_channel(int(i[0])) for i in result]

        da = None
        if result2 is not None:
            da = int(result2[1]) if int(result2[1]) != 0 else None

        if embed_ is not None:
            if embed_[1] == 'enabled':
                em_dict = json.loads(embed_[0])
                embed = discord.Embed.from_dict(em_dict)
                embed.set_author(
                    name=member,
                    icon_url=member.display_avatar.url
                )
                embed.timestamp = datetime.datetime.now()
                try:
                    if embed.title is not None:
                        embed.title = embed.title.format(UserName=member.name, UserId=member.id, UserDiscriminator=member.discriminator, UserCount=len(member.guild.members), GuildName=member.guild.name, UserCreatedAt=f"<t:{round(member.created_at.timestamp())}:R>", UserJoinedAt=f"<t:{round(member.joined_at.timestamp())}:R>", UserMention=member.mention)

                    if embed.description is not None:
                        embed.description = embed.description.format(UserName=member.name, UserId=member.id, UserDiscriminator=member.discriminator, UserCount=len(member.guild.members), GuildName=member.guild.name, UserCreatedAt=f"<t:{round(member.created_at.timestamp())}:R>", UserJoinedAt=f"<t:{round(member.joined_at.timestamp())}:R>", UserMention=member.mention)

                except KeyError:
                    return
                if embed_[2] == 'enabled':
                    for channel in channels:
                        await channel.send(member.mention, embed=embed, delete_after=da)
                else:
                    for channel in channels:
                        await channel.send(embed=embed, delete_after=da)
        else:     
            try:
                if result2 is not None:
                    for channel in channels:
                        await channel.send(str(result2[0]).format(UserName=member.name, UserId=member.id, UserDiscriminator=member.discriminator, UserCount=len(member.guild.members), GuildName=member.guild.name, UserCreatedAt=f"<t:{round(member.created_at.timestamp())}:R>", UserJoinedAt=f"<t:{round(member.joined_at.timestamp())}:R>", UserMention=member.mention), delete_after=da)
            except KeyError:
                return

    @commands.Cog.listener("on_member_join")
    async def member_join_autorole(self, member: discord.Member):
        cursor = await self.bot.db.cursor()
        await cursor.execute("SELECT role_id FROM Autorole WHERE guild_id = ?", (member.guild.id,))
        Brole = await cursor.fetchall()
        await cursor.execute("SELECT role_id FROM AutoroleHuman WHERE guild_id = ?", (member.guild.id,))
        Hrole = await cursor.fetchall()

        if member.bot == False:
            if Hrole == []:
                return
            rolehuman = [int(i[0]) for i in Hrole]
            for role in rolehuman:
                FRole = member.guild.get_role(role)
                if FRole is None:
                    await cursor.execute("DELETE FROM AutoroleHuman WHERE role_id = ?", (role,))
                try:
                    await member.add_roles(FRole, reason=f"{self.bot.user.name}: Human Autorole System")
                except discord.Forbidden: print("No Permission To Add Autorole Human")

        elif member.bot:
            if Brole == []:
                return
            rolebot = [int(i[0]) for i in Brole]
            for role2 in rolebot:
                FFRole = member.guild.get_role(role2)
                if FFRole is None:
                    await cursor.execute("DELETE FROM Autorole WHERE role_id = ?", (role2,))
                try:
                   await member.add_roles(FFRole, reason=f"{self.bot.user.name}: Bot Autorole System")
                except discord.Forbidden: print("No Permission To Add Autorole Bot")
        await self.bot.db.commit()




async def setup(bot):
    await bot.add_cog(Welcome(bot))