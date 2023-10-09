from typing import Optional
from discord.ext import commands
from discord.interactions import Interaction
from discord.ui import Button, View
from aioconsole import aexec
from contextlib import redirect_stdout


import asyncio, os, random, sys, io, textwrap, traceback, discord, datetime, aiohttp, psutil

from prettytable import PrettyTable



from Views.paginator import PaginatorView
from Extra import config










class BadgeView(discord.ui.View):
    def __init__(self, author: discord.Member, user: discord.Member):
        self.author = author
        self.user = user
        super().__init__(timeout=30)

    @discord.ui.select(placeholder="Select Badge", 
                       options=[
                           discord.SelectOption(label="Owner"),
                           discord.SelectOption(label="Friend"),
                           discord.SelectOption(label="VIP"),
                           discord.SelectOption(label="Staff")
                       ])
    async def callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user != self.author:
            return await interaction.response.send_message(f"This cannot be done by you", ephemeral=True)
        
        c = await interaction.client.db.cursor()
        await c.execute("select badge from badge where user_id = ?", (self.user.id,))
        re = await c.fetchall()

        anno = [i[0].lower() for i in re]



        if select.values[0] == "Owner":
            if 'owner' in anno:
                return await interaction.response.edit_message(content=f"The user is already having that badge")
            
            await c.execute("insert into badge(user_id, badge) values(?,?)", (self.user.id, 'owner'))
            await interaction.client.db.commit()
            await interaction.response.edit_message(content=f"Added the badge", embed=None, view=None)
            self.stop()

        if select.values[0] == "Friend":
            if 'friend' in anno:
                return await interaction.response.edit_message(content=f"The user is already having that badge")
            
            await c.execute("insert into badge(user_id, badge) values(?,?)", (self.user.id, 'friend'))
            await interaction.client.db.commit()
            await interaction.response.edit_message(content=f"Added the badge", embed=None, view=None)
            self.stop()

        if select.values[0] == "Staff":
            if 'staff' in anno:
                return await interaction.response.edit_message(content=f"The user is already having that badge")
            
            await c.execute("insert into badge(user_id, badge) values(?,?)", (self.user.id, 'staff'))
            await interaction.client.db.commit()
            await interaction.response.edit_message(content=f"Added the badge", embed=None, view=None)
            self.stop()

        if select.values[0] == "VIP":
            if 'vip' in anno:
                return await interaction.response.edit_message(content=f"The user is already having that badge")
            
            await c.execute("insert into badge(user_id, badge) values(?,?)", (self.user.id, 'vip'))
            await interaction.client.db.commit()
            await interaction.response.edit_message(content=f"Added the badge", embed=None, view=None)
            self.stop()


    async def on_timeout(self):
        if self.msg:
            await self.msg.delete()




class BadgeViewRemover(discord.ui.View):
    def __init__(self, author: discord.Member, user: discord.Member):
        self.author = author
        self.user = user
        super().__init__(timeout=30)



    @discord.ui.select(placeholder="Select Badge", 
                       options=[
                           discord.SelectOption(label="Owner"),
                           discord.SelectOption(label="Friend"),
                           discord.SelectOption(label="VIP"),
                           discord.SelectOption(label="Staff")
                       ])
    async def callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user != self.author:
            return await interaction.response.send_message(f"This cannot be done by you", ephemeral=True)
        
        c = await interaction.client.db.cursor()
        await c.execute("select badge from badge where user_id = ?", (self.user.id,))
        re = await c.fetchall()

        anno = [i[0].lower() for i in re]



        if select.values[0] == "Owner":
            if 'owner' not in anno:
                return await interaction.response.edit_message(content=f"The user is already having that badge")
            
            await c.execute("delete from badge where user_id = ? AND badge = ?", (self.user.id, 'owner'))
            await interaction.client.db.commit()
            await interaction.response.edit_message(content=f"Removed the badge", embed=None, view=None)
            self.stop()

        if select.values[0] == "Friend":
            if 'friend' not in anno:
                return await interaction.response.edit_message(content=f"The user is already having that badge")
            
            await c.execute("delete from badge where user_id = ? AND badge = ?", (self.user.id, 'friend'))
            await interaction.client.db.commit()
            await interaction.response.edit_message(content=f"Removed the badge", embed=None, view=None)
            self.stop()

        if select.values[0] == "Staff":
            if 'staff' not in anno:
                return await interaction.response.edit_message(content=f"The user is already having that badge")
            
            await c.execute("delete from badge where user_id = ? AND badge = ?", (self.user.id, 'staff'))
            await interaction.client.db.commit()
            await interaction.response.edit_message(content=f"Removed the badge", embed=None, view=None)
            self.stop()

        if select.values[0] == "VIP":
            if 'vip' not in anno:
                return await interaction.response.edit_message(content=f"The user is already having that badge")
            
            await c.execute("delete from badge where user_id = ? AND badge = ?", (self.user.id, 'vip'))
            await interaction.client.db.commit()
            await interaction.response.edit_message(content=f"Removed the badge", embed=None, view=None)
            self.stop()


    async def on_timeout(self):
        if self.msg:
            await self.msg.delete()












class PanelView(View):
    def __init__(self, bot, author):
        self.bot = bot
        self.author = author

        super().__init__(timeout=180)

    @discord.ui.button(label="Bot Info")
    async def callback1(self, interaction: discord.Interaction, btn: discord.ui.Button):
        if self.author != interaction.user:
            return await interaction.response.send_message(f"{config.Cross} | Its not your interation.", ephemeral=True)
        
        mem = psutil.virtual_memory()
        total_mem = round(mem.total / (1024 ** 3), 1)
        used_mem = round(mem.used / (1024 ** 3), 1)
        available_mem = round(mem.available / (1024 ** 3), 1)

        dis = psutil.disk_usage('/')
        total_dis = round(dis.total / (1024**3), 1)
        used_dis = round(dis.used / (1024**3), 1)
        avail_dis = round(dis.free / (1024**3), 1)
        per_dis = dis.percent

        embed = discord.Embed(
            color=config.color
        )
        embed.add_field(
            name="Core Statics",
            value=f"```ahk\nCores: {psutil.cpu_count()}\nCPU Usage: {psutil.cpu_percent()}%\nMemory: {used_mem}/{total_mem} GB\nMemory Available: {available_mem} GB\nDisk: {used_dis}/{total_dis} GB ({per_dis} %)\nDisk Available: {avail_dis} GB```",
            inline=False
        )
        embed.add_field(
            name="Bot Cache Info",
            value=f"```ahk\nGuilds: {len(self.bot.guilds)}\nUsers: {len(self.bot.users)}\nLatency: {round(self.bot.latency*1000)} MS\nChannels: {len(list(self.bot.get_all_channels()))}```",
            inline=False
        )
        embed.set_author(
            name=self.bot.user.name,
            icon_url=self.bot.user.display_avatar.url
        )
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="Get User")
    async def UserPanel(self, interaction: discord.Interaction, btn: discord.ui.Button):
        if self.author != interaction.user:
            return await interaction.response.send_message(f"{config.Cross} | Its not your interation.", ephemeral=True)

        await interaction.response.send_modal(
            UserInfoModal(message=self.message, author=self.author)
        )

    
    async def on_timeout(self):
        if self.message is None: return
        for i in self.children:
            i.disabled=True
        await self.message.edit(view=self)






class UserInfoPanel(discord.ui.View):
    def __init__(self, author, msg):
        self.author = author
        self.msg = msg
        super().__init__(timeout=180)

    @discord.ui.button(label="Main Menu", style=discord.ButtonStyle.primary)
    async def MainMenuCall(self, interaction: discord.Interaction, btn: discord.ui.Button):
        if self.author != interaction.user:
            return await interaction.response.send_message(f"{config.Cross} | Its not your interation.", ephemeral=True)
        
        await interaction.response.edit_message(embed=self.msg.embeds[0], view=PanelView(bot=interaction.client, author=self.author))
    
    @discord.ui.button(label="Add No Prefix", style=discord.ButtonStyle.green)
    async def NpAdd(self, interaction: discord.Interaction, btn: discord.ui.Button):
        ...

    @discord.ui.button(label="Remove No Prefix", style=discord.ButtonStyle.red)
    async def NpRemove(self, interaction: discord.Interaction, btn: discord.ui.Button):
        ...


    async def on_timeout(self):
        if self.message is None: return

        for i in self.children:
            i.disabled = True
        await self.msg.edit(view=self)

class UserInfoModal(discord.ui.Modal):
    def __init__(self, message, author):
        self.message = message
        self.author = author
        super().__init__(title="User")

        self.name = discord.ui.TextInput(label="Please Enter ID")
        self.add_item(self.name)



    async def on_submit(self, interaction: discord.Interaction):
        if self.author != interaction.user:
            return await interaction.response.send_message(f"{config.Cross} | Its not your interation.", ephemeral=True)
        try:
            user = await interaction.client.fetch_user(int(self.name.value))
        except discord.NotFound:
            return await interaction.response.send_message("Not Found", ephemeral=True)

        cached = interaction.client.get_user(int(self.name.value))

        c = await interaction.client.db.cursor()
        await c.execute("SELECT user_id FROM Blacklisted WHERE user_id = ?", (user.id,))
        bl = await c.fetchone()
        await c.execute("SELECT users FROM Np WHERE users = ?", (user.id,))
        np = await c.fetchone()

        embed = discord.Embed(
            color=config.color
        )
        embed.add_field(
            name="User Info",
            value=f">>> Mention: <@{user.id}>\nName: {user}\nID: {user.id}\nCached?: {config.Tick if cached is not None else config.Cross}\nAccount Created: <t:{round(user.created_at.timestamp())}:R>\n\n",
            inline=True
        )
        embed.add_field(
            name="Statics",
            value=f">>> Blacklisted: {config.Tick if bl is not None else config.Cross}\nNo Prefix: {config.Tick if np is not None else config.Cross}\n",
            inline=False
        )
        embed.set_thumbnail(
            url=user.display_avatar.url
        )
        if user.banner:
            embed.set_image(
                url=user.banner.url
            )
        view = UserInfoPanel(author=self.author, msg=self.message)
        await interaction.response.edit_message(embed=embed, view=view)






















class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @commands.is_owner()
    async def panel(self, ctx):
        embed = discord.Embed(
            description="Krypton Control Panel",
            color=config.color
        )

        view = PanelView(bot=self.bot, author=ctx.author)
        view.message = await ctx.send(embed=embed, view=view)









    @commands.group(aliases=['nopre', 'np'], description="No prefix commands.", invoke_without_command=True)
    @commands.check_any(config.owner(), commands.is_owner())
    async def noprefix(self, ctx):
        await ctx.send_help(ctx.command)


    @noprefix.command(name="add", description="Adds user to no prefix.")
    @commands.check_any(config.owner(), commands.is_owner())
    async def _add(self, ctx, user: discord.User):
        cursor = await self.bot.db.cursor()

        await cursor.execute("SELECT users FROM Np")
        result = await cursor.fetchall()

        if user.id not in [int(i[0]) for i in result]:
            await ctx.typing()
            await cursor.execute(f"INSERT INTO Np(users) VALUES(?)", (user.id,))
            await ctx.send(f"{config.Tick} | Successfully added {user} to no prefix.")
        else:
            await ctx.send(f"{config.Cross} | That user is already in no prefix.")

        await self.bot.db.commit()


    @noprefix.command(name="remove", description="Removes no prefix from a user.", aliases=['rmv'])
    @commands.check_any(config.owner(), commands.is_owner())
    async def _remove(self, ctx, user: discord.User):
        cursor = await self.bot.db.cursor()

        await cursor.execute("SELECT users FROM Np")
        result = await cursor.fetchall()

        if user.id in [int(i[0]) for i in result]:
            await ctx.typing()
            await cursor.execute(f"DELETE FROM Np WHERE users = ?", (user.id,))
            await ctx.send(f"{config.Tick} | Successfully removed {user} from no prefix.")
        else:
            await ctx.send(f"{config.Cross} | That user isn't in no prefix.")

        await self.bot.db.commit()

    @noprefix.command(name="list", description="Shows the list of no prefix users.", aliases=['show'])
    @commands.check_any(config.owner(), commands.is_owner())
    async def _list(self, ctx):
        await ctx.typing()
        cursor = await self.bot.db.cursor()

        await cursor.execute("SELECT users FROM Np")
        result = await cursor.fetchall()

        embeds = []
        users_ = [int(i[0]) for i in result]
        
        users = []
        for i in users_:
            u = await self.bot.fetch_user(i)
            users.append(u)

        chunked = discord.utils.as_chunks(enumerate(users, start=1), 20)

        for chunk in chunked:
            embed = discord.Embed(description="```\n", color=config.color)
            embed.set_author(name=ctx.author,
                             icon_url=ctx.author.display_avatar.url)

            for i, user in chunk:
                if user is None: await cursor.execute("DELETE FROM Np WHERE users = ?", (int(user),))
            embed.description += "".join([f"[{i}]  {user}\t({user.id})\n"])
            embed.description += '```'
            embeds.append(embed)

        if len(embeds) > 1:
            view = PaginatorView(embeds, bot=self.bot, author=ctx.author)
            view.message = await ctx.send(embed=view.initial, view=view)
        else:
            view2 = PaginatorView(embeds, bot=self.bot, author=ctx.author)
            view2.message = await ctx.send(embed=view2.initial)
        await self.bot.db.commit()


    # @commands.command(name="eval", description="Evalutor", hidden=True)
    # @commands.is_owner()
    # async def _eval(self, ctx, *, code):
    #     def cleanup_code(content: str) -> str:
    #         # remove ```py\n```
    #         if content.startswith('```') and content.endswith('```'):
    #             return '\n'.join(content.split('\n')[1:-1])

    #         # remove `foo`
    #         return content.strip('` \n')
    #     env = {
    #             'message': ctx.message,
    #         }

    #     env.update(globals())

    #     body = cleanup_code(content=code)
    #     stdout = io.StringIO()

    #     to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

    #     try:
    #         exec(to_compile, env)
    #     except Exception as e:
    #         return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

    #     func = env['func']
    #     try:
    #         with redirect_stdout(stdout):
    #             ret = await func()
    #     except Exception as e:
    #         value = stdout.getvalue()
    #         await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
    #     else:
    #         value = stdout.getvalue()


    #     button = Button(style=discord.ButtonStyle.red, label="Delete")
    #     async def button_callback(interaction: discord.Interaction):
    #         await interaction.response.defer()
    #         await interaction.message.delete()
    #     button.callback = button_callback
    #     view = View()
    #     view.add_item(button)
    #     embed = discord.Embed(title="Eval", color=config.color)
    #     embed.add_field(name="Input", value=f"```py\n{code}```", inline=False)


    #     embed.add_field(name="Output", value=f"```py\n{value}{ret}```")
    #     await ctx.send(embed=embed, view=view)


    @commands.command(description="Restarts the bot.", aliases=['rs'], hidden=True)
    @commands.is_owner()
    async def restart(self, ctx):
        button = Button(style=discord.ButtonStyle.green, label="Yes")
        button2 = Button(style=discord.ButtonStyle.red, label="No")

        async def callback(int: discord.Interaction):
            if int.user != ctx.author:
                await int.response.send_message(f"{config.Cross} | It's not your interaction.")
                return
            await int.response.edit_message(content="Restarting.", view=None)
            await self.bot.change_presence(status=discord.Status.dnd, activity=discord.Game(name="Loading."))

            await asyncio.sleep(1)
            os.execv(sys.executable, ['python'] + sys.argv)

        async def callback2(int: discord.Interaction):
            if int.user != ctx.author:
                await int.response.send_message(f"{config.Cross} | It's not your interaction.", ephemeral=True)
                return
            await int.response.edit_message(content="Cancelled.", view=None)

        button.callback = callback
        button2.callback = callback2
        view = discord.ui.View()
        view.add_item(button)
        view.add_item(button2)
        await ctx.send("Are you sure?", view=view)


    @commands.command(hidden=True)
    @commands.is_owner()
    async def gleave(self, ctx, guild: discord.Guild):
        button = discord.ui.Button(label="Yes", style=discord.ButtonStyle.green)
        button2 = discord.ui.Button(label="No", style = discord.ButtonStyle.danger)

        async def callback(interaction: discord.Interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message(f"{config.Cross} | It's not your interaction.", ephemeral=True)
                return
            try:
                await guild.leave()
                await interaction.response.edit_message(content=f"Successfully left {guild.name}", view=None)
            except Exception as e:
                await ctx.send(f"Error:```\n{e}```")
        async def callback2(interaction: discord.Interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message(f"{config.Cross} | It's not your interaction.", ephemeral=True)
                return
            await interaction.response.edit_message(content="Cancelled", view=None)

        button.callback = callback
        button2.callback = callback2
        view = discord.ui.View(timeout=None)
        view.add_item(button)
        view.add_item(button2)
        await ctx.send("Are you sure?", view=view)


    @commands.command()
    @commands.is_owner()
    async def sql(self, ctx, *, query: str):
        if not query.strip().lower().startswith("select"):
            try:
                await self.bot.db.execute(query)
                await self.bot.db.commit()
                await ctx.send("Database updated successfully.")
            except Exception as e:
                await ctx.send(f"An error occurred while updating the database: \n```sql\n{e}```")
            return

        try:
            cursor = await self.bot.db.execute(query)
            columns = [description[0] for description in cursor.description]
            rows = await cursor.fetchall()
        except Exception as e:
            await ctx.send(f"An error occurred while executing the query: \n```sql\n{e}```")
            return

        if not rows:
            await ctx.send('No results found.')
            return

        table = PrettyTable()
        table.field_names = columns
        table.align = "l"

        for row in rows:
            table.add_row(row)

        await ctx.send(f"```sql\n{table}\n```")











    @commands.group(aliases=['bl'], hidden=True, invoke_without_command=True)
    @commands.is_owner()
    async def blacklist(self, ctx):
      if ctx.subcommand_passed is None:
        await ctx.send_help(ctx.command)
        

    @blacklist.group(hidden=True, invoke_without_command=True)
    @commands.is_owner()
    async def guild(self, ctx):
        await ctx.send_help(ctx.command)

    @blacklist.group(hidden=True, invoke_without_command=True)
    @commands.is_owner()
    async def user(self, ctx):
        await ctx.send_help(ctx.command)

    @user.command(name="add", hidden=True)
    @commands.check_any(config.owner(), commands.is_owner())
    async def add2(self, ctx, user: discord.User, *, reason=None):
        reason = reason or 'None'
        c = await self.bot.db.cursor()
        await c.execute("SELECT user_id FROM Blacklisted")
        ids_raw = await c.fetchall()

        if ids_raw != []:
           ids = [int(i[0]) for i in ids_raw]
           if user.id in ids:
            await ctx.send("That user is already blacklisted.")
            return

        time = round(datetime.datetime.now().timestamp())

        
        await c.execute("INSERT INTO Blacklisted(user_id, author_id, reason, time) VALUES(?, ?, ?, ?)", (user.id, ctx.author.id, reason, time))
        await ctx.send(f"Blacklisted **{user} ({user.id})**")

        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(url="https://discord.com/api/webhooks/1092049019141886033/3L7sZrMHYFbvRhnzmR7SFqmBLDqSpPLKa8FWjBvhNzloU35yeTLv7-nqt3xYR7P3VtL9", session=session)
            embed = discord.Embed(
                title="Blacklist Added",
                description=f"**Action By:** {ctx.author} ({ctx.author.id})\n**User:** {user} ({user.id})\n**Time:** <t:{time}:R> (<t:{time}:D>)\n**Reason:**\n```\n{reason}```",
                color=config.color
            )
            await webhook.send(embed=embed)

        await self.bot.db.commit()

    @user.command(name="remove", aliases=['rmv'], hidden=True)
    @commands.check_any(config.owner(), commands.is_owner())
    async def remove2(self, ctx, user: discord.User, *, reason=None):
        reason = reason or 'None'
        c = await self.bot.db.cursor()
        await c.execute("SELECT user_id FROM Blacklisted")
        ids_raw = await c.fetchall()

        if ids_raw != []:
           ids = [int(i[0]) for i in ids_raw]
           if user.id not in ids:
            await ctx.send("That user is not blacklisted.")
            return

        time = round(datetime.datetime.now().timestamp())
        
        await c.execute("DELETE FROM Blacklisted WHERE user_id = ?", (user.id,))
        await ctx.send(f"Unblacklisted **{user} ({user.id})**")
        
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(url="https://discord.com/api/webhooks/1092049019141886033/3L7sZrMHYFbvRhnzmR7SFqmBLDqSpPLKa8FWjBvhNzloU35yeTLv7-nqt3xYR7P3VtL9", session=session)
            embed = discord.Embed(
                title="Blacklist Removed",
                description=f"**Action By:** {ctx.author} ({ctx.author.id})\n**User:** {user} ({user.id})\n**Time:** <t:{time}:R> (<t:{time}:D>)\n**Reason:**\n```\n{reason}```",
                color=config.color
            )
            await webhook.send(embed=embed)
        await self.bot.db.commit()


    
    @guild.command(name="add", hidden=True)
    @commands.check_any(config.owner(), commands.is_owner())
    async def add3(self, ctx, guild: discord.Guild, *, reason=None):
        reason = reason or 'None'

        c = await self.bot.db.cursor()
        await c.execute("SELECT guild_id FROM G_bl")
        ids_raw = await c.fetchall()

        if ids_raw != []:
           ids = [int(i[0]) for i in ids_raw]
           if guild.id in ids:
            await ctx.send("That guild is already blacklisted.")
            return

        time = round(datetime.datetime.now().timestamp())

        
        await c.execute("INSERT INTO G_bl(guild_id, author_id, reason, time) VALUES(?, ?, ?, ?)", (guild.id, ctx.author.id, reason, time))
        await ctx.send(f"Blacklisted **{guild} ({guild.id})**")

        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(url="https://discord.com/api/webhooks/1107289063721009292/dYF8MjSmvw_VRhJTIsCwBRue2pi3KUIlrneVHUsb-Bvh-avwGOJYqMD_bRKPoRS0qhGB", session=session)
            embed = discord.Embed(
                title="Blacklist Added",
                description=f"**Action By:** {ctx.author} ({ctx.author.id})\n**Guild:** {guild} ({guild.id})\n**Time:** <t:{time}:R> (<t:{time}:D>)\n**Reason:**\n```\n{reason}```",
                color=config.color
            )
            await webhook.send(embed=embed)

        await self.bot.db.commit()


    @guild.command(name="remove", aliases=['rmv'], hidden=True)
    @commands.check_any(config.owner(), commands.is_owner())
    async def remove3(self, ctx, guild: discord.Guild, *, reason=None):
        reason = reason or 'None'
        c = await self.bot.db.cursor()
        await c.execute("SELECT user_id FROM Blacklisted")
        ids_raw = await c.fetchall()

        if ids_raw != []:
           ids = [int(i[0]) for i in ids_raw]
           if guild.id not in ids:
            await ctx.send("That guild is not blacklisted.")
            return

        time = round(datetime.datetime.now().timestamp())
        
        await c.execute("DELETE FROM G_bl WHERE guild_id = ?", (guild.id,))
        await ctx.send(f"Unblacklisted **{guild} ({guild.id})**")
        
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(url="https://discord.com/api/webhooks/1107289063721009292/dYF8MjSmvw_VRhJTIsCwBRue2pi3KUIlrneVHUsb-Bvh-avwGOJYqMD_bRKPoRS0qhGB", session=session)

            embed = discord.Embed(
                title="Blacklist Removed",
                description=f"**Action By:** {ctx.author} ({ctx.author.id})\n**User:** {guild} ({guild.id})\n**Time:** <t:{time}:R> (<t:{time}:D>)\n**Reason:**\n```\n{reason}```",
                color=config.color
            )
            await webhook.send(embed=embed)
        await self.bot.db.commit()































    @commands.group(hidden=True, invoke_without_command=True)
    @commands.is_owner()
    async def owner(self, ctx):
        await ctx.send_help(ctx.command)

    @owner.command(hidden=True, name="add")
    @commands.is_owner()
    async def add3(self, ctx, user: discord.User):
        await ctx.typing()
        c = await self.bot.db.cursor()
        await c.execute("SELECT user_id FROM Owner")
        re = await c.fetchall()

        if re != []:
            ids = [int(i[0]) for i in re]
            if user.id in ids:
                await ctx.send("That user is already owner.")
                return
            

        await c.execute("INSERT INTO Owner(user_id) VALUES(?)", (user.id,))
        await ctx.send(f"Added **{user} ({user.id})** to owners.")
        await self.bot.db.commit()

    @owner.command(hidden=True, name="remove", aliases=['rmv'])
    @commands.is_owner()
    async def remove3(self, ctx, user: discord.User):
        await ctx.typing()
        c = await self.bot.db.cursor()
        await c.execute("SELECT user_id FROM Owner")
        re = await c.fetchall()

        if re == []:
            await ctx.send("There are no owners.")
            return
        ids = [int(i[0]) for i in re]
        if user.id not in ids:
            await ctx.send("That user is not owner.")
            return
            

        await c.execute("DELETE FROM Owner WHERE user_id = ?", (user.id,))
        await ctx.send(f"Removed **{user} ({user.id})** from owners.")
        await self.bot.db.commit()

    @owner.command(hidden=True, name="list", aliases=['show'])
    @commands.is_owner()
    async def list3(self, ctx):
        c = await self.bot.db.cursor()
        await c.execute("SELECT user_id FROM Owner")
        re = await c.fetchall()

        if re == []:
            await ctx.send("There are no owners.")
            return
        
        ids_ = [int(i[0]) for i in re]

        ids = []
        for i in ids_:
            z = await self.bot.fetch_user(i)
            ids.append(z)
        enumerate(ids, start=1)

        embeds = []
        embed = discord.Embed(description="```\n", color=config.color)
        embed.set_author(
                name=ctx.author,
                icon_url=ctx.author.display_avatar.url
            )
        chunk = discord.utils.as_chunks(ids, 20)
        for n, user in chunk:

            embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
            embed.description += "".join(f'[{n}] {i}\t({i.id})\n\n' for i in user)

            embed.description += '```'
            embeds.append(embed)

        view = PaginatorView(embeds, bot=self.bot, author=ctx.author)
        if len(embeds) > 1:
            return view.message == await ctx.send(embed=view.initial, view=view)

        view.message = await ctx.send(embed=view.initial)

        
        
        
        
        
        
        

    @commands.hybrid_group(aliases=['mp'],invoke_without_command=True) 
    @commands.is_owner()
    async def managepremium(self, ctx):
        await ctx.send_help(ctx.command)


    @managepremium.command()
    @commands.is_owner()
    async def add(self, ctx, user: discord.User):
        c = await self.bot.db.cursor()
        await c.execute("select end_time from userpremium where user_id = ?", (user.id,))
        re = await c.fetchone()

        if re is not None:
            return await ctx.send(f"This is user is already having premium")
        
        class PlanView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=60)

            @discord.ui.select(placeholder="Choose Premium Plan.",
                            options=[
                                discord.SelectOption(label="Bronze Plan | 1MONTH"),
                                discord.SelectOption(label="Silver Plan | 3MONTH"),
                                discord.SelectOption(label="Gold Plan | 6MONTH"),
                                discord.SelectOption(label='Platinum Plan | 1YEAR'),

discord.SelectOption(label='Diamond Plan | 2YEARS'),

discord.SelectOption(label='Legendary Plan | 3YEARS'),

discord.SelectOption(label='Ultimate Plan | 5YEARS'),

discord.SelectOption(label='Lifetime Plan | LIFETIME'),
                            ])
            async def callback(self, interaction: discord.Interaction, select: discord.ui.Select):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message("This menu cannot be controlled by you", ephemeral=True)
            
                if select.values[0] == "Bronze Plan | 1MONTH":
                    time = round((datetime.timedelta(days=30)+datetime.datetime.now()).timestamp())

                    await c.execute("insert into userpremium(user_id, end_time, prime_count, tier) values(?,?,?,?)", (user.id, time, 3, 1))

                    embed = discord.Embed(
                        description=f"Successfully added **Bronze Plan** to **{user} ({user.id})**",
                        color=config.color
                    )
                    await interaction.response.edit_message(embed=embed, view=None)
                    
                
                if select.values[0] == 'Silver Plan | 3MONTH':
                    time = round((datetime.timedelta(days=90)+datetime.datetime.now()).timestamp())

                    await c.execute("insert into userpremium(user_id, end_time, prime_count, tier) values(?,?,?,?)", (user.id, time, 9, 2))

                    embed = discord.Embed(
                        description=f"Successfully added **Silver Plan** to **{user} ({user.id})**",
                        color=config.color
                    )
                    await interaction.response.edit_message(embed=embed, view=None)
                    
                
                if select.values[0] == 'Gold Plan | 6MONTH':
                    time = round((datetime.timedelta(days=180)+datetime.datetime.now()).timestamp())
                    await c.execute("insert into userpremium(user_id, end_time, prime_count, tier) values(?,?,?,?)", (user.id, time, 18, 3))

                    embed = discord.Embed(
                        description=f"Successfully added **Gold Plan** to **{user} ({user.id})**",
                        color=config.color
                    )
                    await interaction.response.edit_message(embed=embed, view=None)
                  

                if select.values[0] == 'Platinum Plan | 1YEAR':
                    time = round((datetime.timedelta(days=360)+datetime.datetime.now()).timestamp())
                    await c.execute("insert into userpremium(user_id, end_time, prime_count, tier) values(?,?,?,?)", (user.id, time, 36, 4))

                    embed = discord.Embed(
                        description=f"Successfully added **Platinum Plan** to **{user} ({user.id})**",
                        color=config.color
                    )
                    await interaction.response.edit_message(embed=embed, view=None)
                    

                if select.values[0] == "Diamond Plan | 2YEARS":
                    time = round((datetime.timedelta(days=720)+datetime.datetime.now()).timestamp())

                    await c.execute("insert into userpremium(user_id, end_time, prime_count, tier) values(?,?,?,?)", (user.id, time, 72, 5))

                    embed = discord.Embed(
                        description=f"Successfully added **Diamond Plan** to **{user} ({user.id})**",
                        color=config.color
                    )
                    await interaction.response.edit_message(embed=embed, view=None)
                  
                if select.values[0] == "Legendary Plan | 3YEARS":
                    time = round((datetime.timedelta(days=1080)+datetime.datetime.now()).timestamp())

                    await c.execute("insert into userpremium(user_id, end_time, prime_count, tier) values(?,?,?,?)", (user.id, time, 108, 6))

                    embed = discord.Embed(
                        description=f"Successfully added **Legendary Plan** to **{user} ({user.id})**",
                        color=config.color
                    )
                    await interaction.response.edit_message(embed=embed, view=None)    

                if select.values[0] == "Ultimate Plan | 5YEARS":
                    time = round((datetime.timedelta(days=1825)+datetime.datetime.now()).timestamp())

                    await c.execute("insert into userpremium(user_id, end_time, prime_count, tier) values(?,?,?,?)", (user.id, time, 180, 7))

                    embed = discord.Embed(
                        description=f"Successfully added **Ultimate Plan** to **{user} ({user.id})**",
                        color=config.color
                    )
                    await interaction.response.edit_message(embed=embed, view=None) 

              
                if select.values[0] == "Lifetime Plan | LIFETIME":
                    

                    await c.execute("insert into userpremium(user_id, end_time, prime_count, tier) values(?,?,?,?)", (user.id, 'none', 1000, 8))

                    embed = discord.Embed(
                        description=f"Successfully added **Lifetime Plan** to **{user} ({user.id})**",
                        color=config.color
                    )
                    await interaction.response.edit_message(embed=embed, view=None) 
            async def on_timeout(self):
                if self.message is None: return
                if self.children == []: return

                for child in self.children:
                    child.disabled = True
                await self.message.edit(view=self)


        view = PlanView()
        embed = discord.Embed(
            description=f"Select the plan from menu.",
            color=config.color
        )
        view.message = await ctx.send(embed=embed, view=view)
        await view.wait()
        await self.bot.db.commit()
        
    @managepremium.command()
    async def remove(self, ctx, user: discord.User):
        c = await self.bot.db.cursor()
        await c.execute("select end_time from userpremium where user_id = ?", (user.id,))
        re = await c.fetchone()

        if re is None:
            return await ctx.send(f"This is user is not having premium")
        
        await c.execute("delete from userpremium where user_id = ?", (user.id,))

        embed = discord.Embed(
            description=f"Successfully removed premium from them.",
            color=config.color
        )
        await ctx.send(embed=embed)
        await self.bot.db.commit()



        
        
        
        
        
        
        
        
        
        
        
        
        

    @commands.group(name="badge", aliases=['bdg'], invoke_without_command=True)
    @commands.check_any(commands.is_owner(), config.owner())
    async def badge_(self, ctx):
        await ctx.send_help(ctx.command)

    

    @badge_.command(name="add")
    @commands.check_any(commands.is_owner(), config.owner())
    async def bdg_add(self, ctx: commands.Context, *, user: discord.User):
        

        embed = discord.Embed(description="Select badge", color=config.color)
        view = BadgeView(user=user, author=ctx.author)
        view.msg = await ctx.send(embed=embed, view=view)



    @badge_.command(name="remove")
    @commands.is_owner()
    async def bdg_remove(self, ctx: commands.Context, *, user: discord.User):

        embed = discord.Embed(description="Which one do you want to remove?", color=config.color)
        view = BadgeViewRemover(user=user, author=ctx.author)
        view.msg = await ctx.send(embed=embed, view=view)

    @badge_.command(name="removeall")
    @commands.check_any(commands.is_owner(), config.owner())
    async def bdg_remove_all(self, ctx: commands.Context, *, user: discord.User):
        c = await self.bot.db.cursor()
        await c.execute("select badge from badge where user_id = ?", (user.id,))
        re = await c.fetchall()

        if re == []:
            return await ctx.send(f"This user is having no badge")
        
        await c.execute("delete from badge where user_id = ?", (user.id,))
        await self.bot.db.commit()
        await ctx.send(f"{config.Tick} Successfully reset them.")






















async def setup(bot):
    await bot.add_cog(Owner(bot))