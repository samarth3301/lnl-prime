
from typing import Optional
from discord.ext import commands
from discord.interactions import Interaction
from discord.ui import Button, View


from Extra import config
from Views.paginator import PaginatorView

import asyncio, os, random, sys, io, textwrap, traceback, discord, datetime, aiohttp, psutil, time


class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot =bot
    
    def cog_load(self):
        self.cd = commands.CooldownMapping.from_cooldown(1, 5, commands.BucketType.user)


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        error = getattr(error, 'original', error)
        if isinstance(error, discord.Forbidden):
            return
        
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send_help(ctx.command)
        
        if isinstance(error, commands.BotMissingPermissions):
            permissions = ', '.join(perm for perm in error.missing_permissions)

            Embed = discord.Embed(description=f"<:icons_no:1022533995327660083> | Bot needs {permissions} to execute this command.", color=config.color)
            Embed.set_author(name=self.bot.user.name + " Error", icon_url=self.bot.user.display_avatar.url)
            Embed.timestamp = datetime.datetime.utcnow()
            try: return await ctx.send(embed=Embed)
            except: return print(f'Unable to send bot missing permissions - {ctx.guild.name} ({ctx.guild.id})')

        if isinstance(error, commands.CommandOnCooldown):
            bucket = self.cd.get_bucket(ctx.message)
            retry_after = bucket.update_rate_limit()

            if retry_after: return

            Embed = discord.Embed(description=f"<:icons_no:1022533995327660083> | You're on cooldown try again in **{round(error.retry_after, 2)}** seconds.", color=config.color)
            Embed.set_author(name=self.bot.user.name + " Error", icon_url=self.bot.user.display_avatar.url)
            Embed.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=Embed)
        
        if isinstance(error, commands.UserNotFound):
            Embed = discord.Embed(description=f"<:icons_no:1022533995327660083> | This user was not found.", color=config.color)
            Embed.set_author(name=self.bot.user.name + " Error", icon_url=self.bot.user.display_avatar.url)
            Embed.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=Embed)
        
        if isinstance(error, commands.MemberNotFound):
            Embed = discord.Embed(description=f"<:icons_no:1022533995327660083> | This user was not found.", color=config.color)
            Embed.set_author(name=self.bot.user.name + " Error", icon_url=self.bot.user.display_avatar.url)
            Embed.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=Embed)
        
        if isinstance(error, commands.RoleNotFound):
            role = error.argument
            Embed = discord.Embed(description=f"<:icons_no:1022533995327660083> | Role `{role}` wasn't found.", color=config.color)
            Embed.set_author(name=self.bot.user.name + " Error", icon_url=self.bot.user.display_avatar.url)
            Embed.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=Embed)
        
        if isinstance(error, commands.ChannelNotFound):
            channel = error.argument
            Embed = discord.Embed(description=f"<:icons_no:1022533995327660083> | Channel '{channel}' wasn't found.", color=config.color)
            Embed.set_author(name=self.bot.user.name + " Error", icon_url=self.bot.user.display_avatar.url)
            Embed.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=Embed)
        
        if isinstance(error, commands.MaxConcurrencyReached):
            Embed = discord.Embed(description=f"<:icons_no:1022533995327660083> | **{ctx.author}** This command can only be used 1 once per server concurrently, please wait.", color=config.color)
            Embed.set_author(name=self.bot.user.name + " Error", icon_url=self.bot.user.display_avatar.url)
            Embed.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=Embed)
        
        if isinstance(error, commands.CommandNotFound):
            return
        
        if isinstance(error, commands.CheckAnyFailure):
            for error in error.errors:
                if isinstance(error, commands.MissingPermissions):
                    Embed = discord.Embed(description=f"<:icons_no:1022533995327660083> | You don't have enouh permissions to run the command `{ctx.command.qualified_name}`", color=config.color)
                    Embed.set_author(name=self.bot.user.name + " Error", icon_url=self.bot.user.display_avatar.url)
                    Embed.timestamp = datetime.datetime.utcnow()
                    return await ctx.send(embed=Embed, delete_after=5)
                
                if isinstance(error, commands.NotOwner):
                    return
                
                
        if isinstance(error, commands.CheckFailure):
            return
        else:
            raise error














































async def setup(bot):
    await bot.add_cog(Errors(bot))