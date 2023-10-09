from typing import Optional
import discord
from discord.ext import commands, tasks
import pytz, typing, datetime, asyncio

from Extra import config

from Views.paginator import PaginatorView











class RoleConverter(commands.RoleConverter):
    async def convert(self, ctx: commands.Context, argument: str) -> discord.Role:
        try:
            return await super().convert(ctx, argument)
        except commands.RoleNotFound:
            for role in ctx.guild.roles:
                if argument.lower() in role.name.lower():
                    return role
            raise commands.RoleNotFound(argument)














class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.hybrid_command(description="Locks a specfic channel.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_channels=True))
    async def lock(self, ctx, channel: discord.TextChannel=None):
        if channel is None:
            channel = ctx.message.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send(f"{config.Tick} | Successfully locked {channel.mention}.")

    @commands.hybrid_command(description="Unlocks a specfic channel.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_channels=True))
    async def unlock(self, ctx, channel: discord.TextChannel=None):
        if channel is None:
            channel = ctx.message.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=None)
        await ctx.send(f"{config.Tick} | Successfully unlocked {channel.mention}.")

    @commands.hybrid_command(description="Locks all the channels of the server.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_channels=True))
    async def lockall(self, ctx):
        m = await ctx.send(f"{config.Load} Processing the command.")
        channels = [i for i in ctx.guild.channels]

        unlocked_channels = [i for i in channels if i.permissions_for(ctx.guild.default_role).send_messages]
       
        class Confirmation(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=30)

            @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
            async def callback(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if ctx.author.id != interaction.user.id:
                    await interaction.followup.send(content=f"{config.Cross} | Its not your interaction.", ephemeral=True)
                    return

                await interaction.message.delete()
                embed=discord.Embed(
                    description=f"Locking {len(unlocked_channels)} channels.",
                    color=config.color
                )
                await ctx.send(embed=embed)

                for c in unlocked_channels:
                    await c.set_permissions(ctx.guild.default_role, send_messages=False)

                await ctx.send(f"{config.Tick} | Successfully locked the channels.")
                self.stop()

            @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
            async def callback2(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if ctx.author.id != interaction.user.id:
                    await interaction.followup.send(content=f"{config.Cross} | Its not your interaction.", ephemeral=True)
                    return
                await interaction.message.delete()
                await ctx.send(f"{ctx.author.mention} command execution cancelled.")
                self.stop()
            
            async def on_timeout(self):
                if ctx.channel or self.message is None:
                    return
                await self.message.delete()
                await ctx.send(f"{ctx.author.mention} Alright, I won't lock the channels.")
                self.stop()


        notch = 0
        for channel in channels:
            if channel.permissions_for(ctx.guild.default_role).send_messages:
                notch += 1
        await m.delete()
        embed = discord.Embed(
            description=f"**Are you sure you want to lock {notch} channels?**",
            color=config.color
        )
        view = Confirmation()
        view.message = await ctx.send(embed=embed, view=view)
        await view.wait()

    @commands.hybrid_command(description="Unhides all the channels of the server.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_channels=True))
    async def unlockall(self, ctx):
        m = await ctx.send(f"{config.Load} Processing the command.")
        channels = [i for i in ctx.guild.channels]

        locked_channels = [i for i in channels if not i.permissions_for(ctx.guild.default_role).send_messages]
       
        class Confirmation(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=30)

            @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
            async def callback(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if ctx.author.id != interaction.user.id:
                    await interaction.followup.send(content=f"{config.Cross} | Its not your interaction.", ephemeral=True)
                    return

                await interaction.message.delete()
                embed=discord.Embed(
                    description=f"Unlocking {len(locked_channels)} channels.",
                    color=config.color
                )
                await ctx.send(embed=embed)

                for c in locked_channels:
                    await c.set_permissions(ctx.guild.default_role, send_messages=None)

                await ctx.send(f"{config.Tick} | Successfully unlocked the channels.")
                self.stop()

            @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
            async def callback2(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if ctx.author.id != interaction.user.id:
                    await interaction.followup.send(content=f"{config.Cross} | Its not your interaction.", ephemeral=True)
                    return
                await interaction.message.delete()
                await ctx.send(f"{ctx.author.mention} command execution cancelled.")
                self.stop()
            
            async def on_timeout(self):
                if ctx.channel or self.message is None:
                    return
                await self.message.delete()
                await ctx.send(f"{ctx.author.mention} Alright, I won't unlock the channels.")
                self.stop()


        notch = 0
        for channel in channels:
            if not channel.permissions_for(ctx.guild.default_role).send_messages:
                notch += 1
        await m.delete()
        embed = discord.Embed(
            description=f"**Are you sure you want to unlock {notch} channels?**",
            color=config.color
        )
        view = Confirmation()
        view.message = await ctx.send(embed=embed, view=view)
        await view.wait()





    @commands.hybrid_command(description="Hides a specfic channel.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_channels=True))
    async def hide(self, ctx, channel: discord.TextChannel=None):
        if channel is None:
            channel = ctx.channel
        await channel.set_permissions(ctx.guild.default_role, view_channel=False)
        await ctx.send(f"{config.Tick} | Successfully hidden {channel.mention}.")

    @commands.hybrid_command(description="Unhides a specfic channel.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_channels=True))
    async def unhide(self, ctx, channel: discord.TextChannel=None):
        if channel is None:
            channel = ctx.channel
        await channel.set_permissions(ctx.guild.default_role, view_channel=None)
        await ctx.send(f"{config.Tick} | Successfully unhidden {channel.mention}.")


    @commands.hybrid_command(description="Hides all the channels of the server.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_channels=True))
    async def hideall(self, ctx):
        m = await ctx.send(f"{config.Load} Processing the command.")
        channels = [i for i in ctx.guild.channels]

        unhidden_channels = [i for i in channels if i.permissions_for(ctx.guild.default_role).view_channel]
       
        class Confirmation(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=30)

            @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
            async def callback(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if ctx.author.id != interaction.user.id:
                    await interaction.followup.send(content=f"{config.Cross} | Its not your interaction.", ephemeral=True)
                    return

                await interaction.message.delete()
                embed=discord.Embed(
                    description=f"Hiding {len(unhidden_channels)} channels.",
                    color=config.color
                )
                await ctx.send(embed=embed)

                for c in unhidden_channels:
                    await c.set_permissions(ctx.guild.default_role, view_channel=False)

                await ctx.send(f"{config.Tick} | Successfully hidden the channels.")
                self.stop()

            @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
            async def callback2(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if ctx.author.id != interaction.user.id:
                    await interaction.followup.send(content=f"{config.Cross} | Its not your interaction.", ephemeral=True)
                    return
                await interaction.message.delete()
                await ctx.send(f"{ctx.author.mention} command execution cancelled.")
                self.stop()
            
            async def on_timeout(self):
                if ctx.channel or self.message is None:
                    return
                await self.message.delete()
                await ctx.send(f"{ctx.author.mention} Alright, I won't hide the channels.")
                self.stop()

        notch = 0
        for channel in channels:
            if channel.permissions_for(ctx.guild.default_role).view_channel:
                notch += 1
        await m.delete()
        embed = discord.Embed(
            description=f"**Are you sure you want to hide {notch} channels?**",
            color=config.color
        )
        view = Confirmation()
        view.message = await ctx.send(embed=embed, view=view)
        await view.wait()

    @commands.hybrid_command(description="Hides all the channels of the server.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_channels=True))
    async def unhideall(self, ctx):
        m = await ctx.send(f"{config.Load} Processing the command.")
        channels = [i for i in ctx.guild.channels]

        unhidden_channels = [i for i in channels if not i.permissions_for(ctx.guild.default_role).view_channel]
       
        class Confirmation(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=30)

            @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
            async def callback(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if ctx.author.id != interaction.user.id:
                    await interaction.followup.send(content=f"{config.Cross} | Its not your interaction.", ephemeral=True)
                    return

                await interaction.message.delete()
                embed=discord.Embed(
                    description=f"Unhiding {len(unhidden_channels)} channels.",
                    color=config.color
                )
                await ctx.send(embed=embed)

                for c in unhidden_channels:
                    await c.set_permissions(ctx.guild.default_role, view_channel=None)

                await ctx.send(f"{config.Tick} | Successfully hidden the channels.")
                self.stop()

            @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
            async def callback2(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if ctx.author.id != interaction.user.id:
                    await interaction.followup.send(content=f"{config.Cross} | Its not your interaction.", ephemeral=True)
                    return
                await interaction.message.delete()
                await ctx.send(f"{ctx.author.mention} command execution cancelled.")
                self.stop()
            
            async def on_timeout(self):
                if ctx.channel or self.message is None:
                    return
                await self.message.delete()
                await ctx.send(f"{ctx.author.mention} Alright, I won't unhide the channels.")
                self.stop()

        notch = 0
        for channel in channels:
            if not channel.permissions_for(ctx.guild.default_role).view_channel:
                notch += 1
        await m.delete()
        embed = discord.Embed(
            description=f"**Are you sure you want to unhide {notch} channels?**",
            color=config.color
        )
        view = Confirmation()
        view.message = await ctx.send(embed=embed, view=view)
        await view.wait()










    @commands.hybrid_group(invoke_without_command=True, description="Adds role to a user.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_roles=True))
    async def role(self, ctx, user: discord.Member, role: RoleConverter):
        if ctx.author != ctx.guild.owner:
            if ctx.author.top_role <= user.top_role:
                await ctx.send(f"{config.Cross} | Your highest role must be above user's role.")
                return
        if ctx.guild.me.top_role <= user.top_role:
            await ctx.send(f"{config.Cross} | My highest role is below their role.")
            return
        if ctx.guild.me.top_role <= role:
            await ctx.send(f"{config.Cross} | My highest role is below the role.")
            return
        
        if role in user.roles:
            await user.remove_roles(role)
            await ctx.send(f"{config.Tick} | Successfully removed **{role}** from {user}")
        elif role not in user.roles:
            await user.add_roles(role)
            await ctx.send(f"{config.Tick} | Successfully added **{role}** to {user}")
        
    @role.command(name="bots", description="Adds role to only bots.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_roles=True))
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def bots1(self, ctx, role: RoleConverter):
        m = await ctx.send(f"{config.Load} Processing the command.")
        botv = [member for member in ctx.guild.members if member.bot]
        bots = [i for i in botv if not role in i.roles]

        if ctx.guild.me.top_role <= role:
           await ctx.send(f"{config.Cross} | My highest role is below the role.")
           return
        
        class ConfirmationView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=30)

            @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
            async def callback(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if ctx.author.id != interaction.user.id:
                    await interaction.followup.send(content=f"{config.Cross} | Its not your interaction.", ephemeral=True)
                    return

                await interaction.message.delete()
                embed=discord.Embed(
                    description=f"Adding the role to {len(bots)} bots.",
                    color=config.color
                )
                await ctx.send(embed=embed)

                for bot in bots:
                    await bot.add_roles(role)
                await ctx.send(f"{config.Tick} | Successfully added the roles.")
                self.stop()

            @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
            async def callback2(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if ctx.author.id != interaction.user.id:
                    await interaction.followup.send(content=f"{config.Cross} | Its not your interaction.", ephemeral=True)
                    return
                await interaction.message.delete()
                await ctx.send(f"{ctx.author.mention} command execution cancelled.")
                self.stop()
            
            async def on_timeout(self):
                if ctx.channel or self.message is None:
                    return
                await self.message.delete()
                await ctx.send(f"{ctx.author.mention} Alright, I'll not add the roles.")
                self.stop()

        notrole = 0
        for i in bots:
            if not role in i.roles:
                notrole += 1
        await m.delete()
        embed = discord.Embed(description=f"**Are you sure you want to add {role.mention} to {notrole} bots?**", color=config.color)
        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
        view = ConfirmationView()
        view.message = await ctx.send(embed=embed, view=view)
        await view.wait()

    @role.command(description="Adds role to all the users in the server.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_roles=True))
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def all(self, ctx, role: RoleConverter):
        m = await ctx.send(f"{config.Load} Processing the command.")
        users = [i for i in ctx.guild.members if not role in i.roles]

        if ctx.guild.me.top_role <= role:
           await ctx.send(f"{config.Cross} | My highest role is below the role.")
           return
        
        class ConfirmationView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=30)

            @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
            async def callback(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if ctx.author.id != interaction.user.id:
                    await interaction.followup.send(content=f"{config.Cross} | Its not your interaction.", ephemeral=True)
                    return

                await interaction.message.delete()
                embed=discord.Embed(
                    description=f"Adding the role to {len(users)} users.",
                    color=config.color
                )
                await ctx.send(embed=embed)

                for user in users:
                    await user.add_roles(role)

                await ctx.send(f"{config.Tick} | Successfully added the role.")
                self.stop()

            @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
            async def callback2(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if ctx.author.id != interaction.user.id:
                    await interaction.followup.send(content=f"{config.Cross} | Its not your interaction.", ephemeral=True)
                    return
                await interaction.message.delete()
                await ctx.send(f"{ctx.author.mention} command execution cancelled.")
                self.stop()
            
            async def on_timeout(self):
                if ctx.channel or self.message is None:
                    return
                await self.message.delete()
                await ctx.send(f"{ctx.author.mention} Alright, I'll not add the role.")
                self.stop()

        notrole = 0
        for i in users:
            if not role in i.roles:
                notrole += 1
        await m.delete()
        embed = discord.Embed(description=f"**Are you sure you want to add {role.mention} to {notrole} users?**", color=config.color)
        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
        view = ConfirmationView()
        view.message = await ctx.send(embed=embed, view=view)
        await view.wait()

    @role.command(name="humans", description="Adds role to only humans.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_roles=True))
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def humans1(self, ctx, role: RoleConverter):
        m = await ctx.send(f"{config.Load} Processing the command.")

        hv = [member for member in ctx.guild.members if not member.bot]
        humans = [i for i in hv if not role in i.roles]

        if ctx.guild.me.top_role <= role:
           await ctx.send(f"{config.Cross} | My highest role is below the role.")
           return
        
        class ConfirmationView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=30)

            @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
            async def callback(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if ctx.author.id != interaction.user.id:
                    await interaction.followup.send(f"{config.Cross} | Its not your interaction.", ephemeral=True)
                    return

                await interaction.message.delete()
                embed=discord.Embed(description=f"Adding the role to {len(humans)} humans", color=config.color)
                await ctx.send(embed=embed)

                for bot in humans:
                    await bot.add_roles(role)
                await ctx.send(f"{config.Tick} | Successfully added the role.")
                self.stop()

            @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
            async def callback2(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if ctx.author.id != interaction.user.id:
                    await interaction.response.send_message(f"{config.Cross} | Its not your interaction.", ephemeral=True)
                    return
                await interaction.message.delete()
                await ctx.send(f"{ctx.author.mention} command execution cancelled.")
                self.stop()
            
            async def on_timeout(self):
                if ctx.channel or self.message is None:
                    return
                await self.message.delete()
                await ctx.send(f"{ctx.author.mention} Alright, I'll not add the roles.")

        notrole = 0
        for i in humans:
            if not role in i.roles:
                notrole += 1
        await m.delete()
        embed = discord.Embed(description=f"**Are you sure you want to add {role.mention} to {notrole} humans?**", color=config.color)
        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
        view = ConfirmationView()
        view.message = await ctx.send(embed=embed, view=view)
        await view.wait()


    

    @commands.hybrid_group(description="Remove role commands.", invoke_without_command=True)
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_roles=True))
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def rrole(self, ctx, role: RoleConverter):
        m = await ctx.send(f"{config.Load} Processing the command.")

        users = [i for i in ctx.guild.members]
        notusers = [i for i in users if role in i.roles]

        if role >= ctx.guild.me.top_role:
            await ctx.send(f"{config.Cross} | My highest role is below the role")

        class ConfirmationView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=30)

            @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
            async def callback(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if ctx.author.id != interaction.user.id:
                    await interaction.followup.send(f"{config.Cross} | Its not your interaction.", ephemeral=True)
                    return

                await interaction.message.delete()
                embed=discord.Embed(description=f"Removing the role from {len(notusers)} users.", color=config.color)
                await ctx.send(embed=embed)

                for user in notusers:
                    await user.remove_roles(role)
                await ctx.send(f"{config.Tick} | Successfully removed the role.")
                self.stop()

            @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
            async def callback2(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if ctx.author.id != interaction.user.id:
                    await interaction.response.send_message(f"{config.Cross} | Its not your interaction.", ephemeral=True)
                    return
                await interaction.message.delete()
                await ctx.send(f"{ctx.author.mention} command execution cancelled.")
                self.stop()
            
            async def on_timeout(self):
                if ctx.channel or self.message is None:
                    return
                await self.message.delete()
                await ctx.send(f"{ctx.author.mention} Alright, I'll not remove the role.")

        notrole = 0
        for i in users:
            if role in i.roles:
                notrole += 1
        await m.delete()
        embed = discord.Embed(description=f"**Are you sure you want to remove {role.mention} from {notrole} users?**", color=config.color)
        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
        view = ConfirmationView()
        view.message = await ctx.send(embed=embed, view=view)
        await view.wait()


    @rrole.command(name="humans", description="Removes role from humans.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_roles=True))
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def humans2(self, ctx, role: RoleConverter):
        m = await ctx.send(f"{config.Load} Processing the command.")

        users = [i for i in ctx.guild.members if not i.bot]
        notusers = [i for i in users if role in i.roles]

        if role >= ctx.guild.me.top_role:
            await ctx.send(f"{config.Cross} | My highest role is below the role.")

        class ConfirmationView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=30)

            @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
            async def callback(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if ctx.author.id != interaction.user.id:
                    await interaction.followup.send(f"{config.Cross} | Its not your interaction.", ephemeral=True)
                    return

                await interaction.message.delete()
                embed=discord.Embed(description=f"Removing the role from {len(notusers)} humans.", color=config.color)
                await ctx.send(embed=embed)

                for user in notusers:
                    await user.remove_roles(role)

                await ctx.send(f"{config.Tick} | Successfully removed the role.")
                self.stop()

            @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
            async def callback2(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if ctx.author.id != interaction.user.id:
                    await interaction.response.send_message(f"{config.Cross} | Its not your interaction.", ephemeral=True)
                    return
                await interaction.message.delete()
                await ctx.send(f"{ctx.author.mention} command execution cancelled.")
                self.stop()
            
            async def on_timeout(self):
                if ctx.channel or self.message is None:
                    return
                await self.message.delete()
                await ctx.send(f"{ctx.author.mention} Alright, I'll not remove the role.")

        notrole = 0
        for i in users:
            if role in i.roles:
                notrole += 1
        await m.delete()
        embed = discord.Embed(description=f"**Are you sure you want to remove {role.mention} from {notrole} humans?**", color=config.color)
        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
        view = ConfirmationView()
        view.message = await ctx.send(embed=embed, view=view)
        await view.wait()

 
    @rrole.command(name="bots", description="Removes role from humans.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_roles=True))
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def bots2(self, ctx, role: RoleConverter):
        m = await ctx.send(f"{config.Load} Processing the command.")

        users = [i for i in ctx.guild.members if i.bot]
        notusers = [i for i in users if role in i.roles]

        if role >= ctx.guild.me.top_role:
            return await ctx.send(f"{config.Cross} | My highest role is below the role.")

        class ConfirmationView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=30)

            @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
            async def callback(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if ctx.author.id != interaction.user.id:
                    await interaction.followup.send(f"{config.Cross} | Its not your interaction.", ephemeral=True)
                    return

                await interaction.message.delete()
                embed=discord.Embed(description=f"Removing the role from {len(notusers)} bots.", color=config.color)
                await ctx.send(embed=embed)

                for user in notusers:
                    await user.remove_roles(role)

                await ctx.send(f"{config.Tick} | Successfully removed the role.")
                self.stop()

            @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
            async def callback2(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if ctx.author.id != interaction.user.id:
                    await interaction.response.send_message(f"{config.Cross} | Its not your interaction.", ephemeral=True)
                    return
                await interaction.message.delete()
                await ctx.send(f"{ctx.author.mention} command execution cancelled.")
                self.stop()
            
            async def on_timeout(self):
                if ctx.channel or self.message is None:
                    return
                await self.message.delete()
                await ctx.send(f"{ctx.author.mention} Alright, I'll not remove the role.")

        notrole = 0
        for i in users:
            if role in i.roles:
                notrole += 1
        await m.delete()
        embed = discord.Embed(description=f"**Are you sure you want to remove {role.mention} from {notrole} bots?**", color=config.color)
        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
        view = ConfirmationView()
        view.message = await ctx.send(embed=embed, view=view)
        await view.wait()













    @commands.command(description="Changes nickname of users")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_nicknames=True))
    async def nick(self, ctx, member: discord.Member, *, nick: str = None):
        nick = nick or None
        await member.edit(nick=nick)
        await ctx.send(f"{config.Tick} | Successfully changed their nick.")

    @commands.command(description=f"Kick a member if they are breaking rules.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(kick_members=True))
    async def kick(self, ctx, user : discord.Member, *, reason=None):
        reason = reason or "[No reason]"
        if ctx.author.top_role <= user.top_role or not user.guild.owner:
            await ctx.send(f"{config.Cross} | You cannot kick them.")
        elif ctx.guild.me.top_role.position <= user.top_role.position:
            await ctx.send(f"{config.Cross} | My highest role is below their role.")
        elif user == ctx.author:
            await ctx.send(f"{config.Cross} | You cannot kick yourself.")
            return
        else:
            try:
                await user.send(f"{config.Red} | You have been **Kicked** from {ctx.guild.name}\n**__Reason__**: `{reason}`")
            except:
                pass
            await ctx.guild.kick(user=user, reason=f"By {ctx.author}: {reason}")
            await ctx.message.add_reaction(config.Tick)
            await ctx.send(f"{config.Tick} | Successfully kicked **{user}** `{reason}`")

    @commands.command(aliases=['fuckban', 'hackban', 'fuckyou'], description=f"Ban a user if they are breaking rules again and again.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(ban_members=True))
    async def ban(self, ctx, user: discord.User, *, reason=None):
        reason = reason or "[No reason]"

        if user in ctx.guild.members:
            user = ctx.guild.get_member(user.id)
            if ctx.author.top_role <= user.top_role or not user.guild.owner:
                await ctx.send(f"{config.Cross} | You cannot ban them.")
                return
            elif ctx.guild.me.top_role.position <= user.top_role.position:
                await ctx.send(f"{config.Cross} | My highest role is below their role.")
                return
            
        if user.id == ctx.author.id:
            await ctx.send(f"You cannot ban yourself.")
            return
        else:
            try:
                await user.send(f"{config.Red} | You have been **Banned** from {ctx.guild.name}\n**__Reason__**: `{reason}`")
            except:
                pass
            await ctx.guild.ban(user=user, reason=f"By {ctx.author}: {reason}", delete_message_seconds=0)
            await ctx.message.add_reaction(config.Tick)
            await ctx.send(f"{config.Tick} | Successfully banned **{user}** `{reason}`")

    @commands.command(description="Unban a user using this command.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(ban_members=True))
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, user: discord.User, *, reason=None):
        reason = reason or "[No reason]"
        try:
           await ctx.guild.fetch_ban(user)
        except discord.NotFound:
            return await ctx.send(f"{config.Cross} | That user is not banned.")
        
        await ctx.guild.unban(user=user, reason=f"By {ctx.author}: {reason}")
        await ctx.message.add_reaction(config.Tick)
        await ctx.send(f"{config.Tick} | Successfully unbanned **{user}** `{reason}`")

    @commands.command(description="Warn a user if they are breaking rules. | Warnings aren't stored")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_messages=True))
    async def warn(self, ctx, member: discord.Member, *, reason):
        if ctx.author.top_role <= member.top_role or not member.guild.owner:
            await ctx.send(f"{config.Cross} | You cannot warn them.")
            return
        elif member.id == ctx.author.id:
            await ctx.send(f"{config.Cross} | You cannot warn yourself.")
            return
        try:
            await member.send(f"{config.Red} | You have been **Warned** in **{ctx.guild.name}**\n**__Reason__**: `{reason}`.")
            await ctx.send(f"{config.Tick} | Successfully warned **{member}** `{reason}`")
        except:
            await ctx.send(f"{config.Cross} | Their DM is closed.")
        
    @commands.command(description="Stops a user from writing in channels.", aliases=['stfu', 'timeout', 'tempmute'])
    @commands.check_any(commands.is_owner(),commands.has_permissions(moderate_members=True))
    @commands.bot_has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, duration, *, reason: str = None):
        reason = reason or 'No reason provided.'

        if ctx.author is member:
            await ctx.send(f"{config.Cross} | You cannot mute yourself.")
            return
        delta = None
        if duration[-1] == "s":
            wait = 1 * int(duration[:-1])
            delta = datetime.timedelta(seconds=wait)
        elif duration[-1] == "m":
            wait = 60 * int(duration[:-1])
            if wait > 40320:
                await ctx.send(f"{config.Cross} | The max limit is 28 days.")
                return
            delta = datetime.timedelta(seconds=wait)
        elif duration[-1] == "h":
            wait = 60 * 60 * int(duration[:-1])
            if wait > 672:
                await ctx.send(f"{config.Cross} | The max limit is 28 days.")
                return
            delta = datetime.timedelta(seconds=wait)
        elif duration[-1] == "d":
            wait = 60 * 60 * 24 * int(duration[:-1])
            if wait > 28:
                await ctx.send(f"{config.Cross} | The max limit is 28 days.")
                return
            delta = datetime.timedelta(seconds=wait)

        if member.is_timed_out():
          await ctx.send(f"{config.Cross} | The user is already timed out.")
          return

        if ctx.author is not ctx.guild.owner:
            if ctx.author.top_role > member.top_role:
                await member.timeout(delta, reason=f"By {ctx.author}: {reason}")
                await ctx.send(f"{config.Tick} | Successfully muted {member} for {duration} `{reason}`.")
                return
            else:
                await ctx.send(f"{config.Cross} | You don't have permission to do it.", delete_after=5)
                return
        await member.timeout(delta, reason=f"By {ctx.author}: {reason}")
        await ctx.send(f"{config.Tick} | Successfully muted {member} for {duration} `{reason}`.")

    @commands.command(description="Unmutes a user so that they can write in the channels.", aliases=['unshut'])
    @commands.check_any(commands.is_owner(), commands.has_permissions(moderate_members=True))
    async def unmute(self, ctx, member: discord.Member, *, reason: str = None):
        reason = reason or 'No reason provided.'
        if ctx.author is member:
            await ctx.send(f"{config.Cross} | You cannot unmute yourself.")
            return
        
        if not member.is_timed_out():
          await ctx.send(f"{config.Cross} | The user is not timed out.")
          return
        
        if ctx.author is not ctx.guild.owner:
            if ctx.author.top_role > member.top_role:
                await member.timeout(None, reason=reason)
                await ctx.send(f"{config.Tick} | Successfully unmuted {member} `{reason}`.")
                return
            else:
                await ctx.send(f"{config.Cross} | You don't have permission to do it.", delete_after=5)
                return

        await member.timeout(None, reason=reason)
        await ctx.send(f"{config.Tick} | Successfully unmuted {member} `{reason}`.")

    
    @commands.command(description="Deletes a channel")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_channels=True))
    async def delchannel(self, ctx, channel: typing.Optional[discord.CategoryChannel]):
        channel = channel or ctx.channel

        class Confirmation(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=30)

            @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
            async def confirm(self, interaction: discord.Interaction, btn: discord.ui.Button):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message(f"{config.Cross} | Its not your interaction.", ephemeral=True)
                
                await channel.delete(reason=f"Deleted By {ctx.author}")

            @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
            async def cancel(self, interaction: discord.Interaction, btn: discord.ui.Button):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message(f"{config.Cross} | Its not your interaction.", ephemeral=True)
                
                await interaction.delete_original_response()
                await ctx.send(f"{ctx.author.mention} command execution cancelled.")

            async def on_timeout(self):
                for i in self.children: i.disabled = True
                try:
                   await self.message.edit(view=self)
                except Exception:
                    pass
            
        view = Confirmation()
        embed = discord.Embed(description=f"**Are you sure you want to delete the channel?**", color=config.color)
        view.message = await ctx.send(embed=embed, view=view)
        await view.wait()

    @commands.command(description="Gives a role to all the provided users.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_roles=True))
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def giverole(self, ctx, role: RoleConverter, users: commands.Greedy[discord.Member]):

        if ctx.guild.me.top_role < role:
            return await ctx.send(f"{config.Cross} | Your top role must be above the role.", delete_after=5)

        if ctx.author != ctx.guild.owner:
            if ctx.author.top_role > role:
                for user in users:
                    if user.top_role < ctx.author.top_role:
                        for user in users:
                            await user.add_roles(role)
                        await ctx.send(f"{config.Tick} | Successfully added the role to all the listed users.")
                    else:
                        await ctx.send(f"{config.Cross} | Your top role must be above all the user's top role.", delete_after=5)
            else:
                await ctx.send(f"{config.Cross} | Your top role must be above the role.")
        else:
            for user in users:
                if user.top_role < ctx.author.top_role:
                    for user in users:
                        await user.add_roles(role)
                    await ctx.send(f"{config.Tick} | Successfully added the role to all the listed users.")


    @commands.command(description="Shows logs of audit log.")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check_any(commands.is_owner(), commands.has_permissions(view_audit_log=True))
    @commands.bot_has_permissions(view_audit_log=True)
    async def audit(self, ctx, limit):
        try:
            int(limit)
        except TypeError:
            return await ctx.send(f"Invalid limit.")
        
        await ctx.typing()
        embeds = []

        entry = [entry async for entry in ctx.guild.audit_logs(limit=int(limit))]


        for chunk in discord.utils.as_chunks(entry, 5):
            embed = discord.Embed(color=config.color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url, url=f'https://discord.com/users/{ctx.author.id}')
            embed.description = ''

            for entry in chunk:
                user = entry.user
                target = entry.target
                action = str(entry.action.name).replace('_', ' ').title()
                time = f'<t:{round(entry.created_at.timestamp())}:R>'
                entry_id = entry.id


                embed.description += f'\n**Action By:** {user} ({user.mention})\n**Target:** {target}\n**Action:** {action}\n**Time:** {time}\n**ID:** {entry_id}\n\n'
            embeds.append(embed)

        view = PaginatorView(embeds, self.bot, ctx.author)
        if len(embeds) > 1:
            view.message = await ctx.send(embed=view.initial, view=view)
        else:
            view.message = await ctx.send(embed=view.initial)
        




































































async def setup(bot):
    await bot.add_cog(Moderation(bot))