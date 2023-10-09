from typing import Optional
from discord.ext import commands
from discord.interactions import Interaction
from discord.ui import Button, View


from Extra import config
from Views.paginator import PaginatorView

import asyncio, os, random, sys, io, textwrap, traceback, discord, datetime, aiohttp, psutil, time





class AutoResponder(commands.Cog, name="Auto Responder"):
    def __init__(self, bot):
        self.bot = bot


    @commands.hybrid_group(description="Auto responder commands", aliases=['ar'])
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def autoresponder(self, ctx):
        await ctx.send_help(ctx.command)

   
    @autoresponder.command(name="create", description="Creates an auto responder.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def ar_create(self, ctx, trigger, *, content: str):
        c = await self.bot.db.cursor()
        await c.execute("SELECT name FROM auto_res WHERE guild_id = ?", (ctx.guild.id,))
        re = await c.fetchall()

        ar_list = [i[0].lower() for i in re]

        if len(ar_list) == 5:
            embed = discord.Embed(
                description=f"**{ctx.author}** This server has reached the maximum limit.",
                color=config.color
            )
            return await ctx.send(embed=embed)
        
        if trigger.lower() in ar_list:
            embed = discord.Embed(
                description=f"**{ctx.author}** An auto responder with the same name already exists. Try a different name.",
                color=config.color
            )
            return await ctx.send(embed=embed, delete_after=5)


        await c.execute("INSERT INTO auto_res(guild_id, name, content, time) VALUES(?, ?, ?, ?)", (ctx.guild.id, trigger.lower(), content, round(time.time())))
        await ctx.send(f"{config.Tick} | Successfully created the auto responder.")
        await self.bot.db.commit()


    @autoresponder.command(name="delete", description="Deletes an auto responder.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def ar_delete(self, ctx, autoresponder):
        c = await self.bot.db.cursor()
        await c.execute("SELECT name, id FROM auto_res WHERE guild_id = ?", (ctx.guild.id,))
        re = await c.fetchall()

        name_list = [i[0] for i in re]
        id_list = [str(i[1]) for i in re]

        if autoresponder.lower() in name_list:
            await c.execute("DELETE FROM auto_res WHERE name = ? AND guild_id = ?", (autoresponder.lower(), ctx.guild.id))
            await ctx.send(f"{config.Tick} | Successfully deleted the auto responder.")

        elif autoresponder.lower() in id_list:
            await c.execute("DELETE FROM auto_res WHERE id = ? AND guild_id = ?", (autoresponder.lower(), ctx.guild.id))
            await ctx.send(f"{config.Tick} | Successfully deleted the auto responder.")
        else:
            embed=discord.Embed(
                description=f"**{ctx.author}** Auto responder not found.",
                color=config.color
            )
            await ctx.send(embed=embed, delete_after=5)

        await self.bot.db.commit()

    @autoresponder.command(description="Edits an autoresponder.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def edit(self, ctx):
        ...


    
    @autoresponder.command(name="list", description="Deletes an auto responder.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def ar_list(self, ctx):
        c = await self.bot.db.cursor()
        await c.execute("SELECT name, id FROM auto_res WHERE guild_id = ?", (ctx.guild.id,))
        re = await c.fetchall()

        if re == []:
            await ctx.send("Auto responder has not been created for this server.")
            
        ar_list = enumerate([i for i in re], start=1)

        embeds = []

        for chunk in discord.utils.as_chunks(ar_list, 20):

            embed = discord.Embed(color=config.color)
            embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
            embed.description = ''

            for i, (name, id) in chunk:
                
                embed.description += f'`[{i}]` {name}   (ID - {id})\n'
            embeds.append(embed)

        print(embeds)
        view = PaginatorView(embeds, self.bot, ctx.author)
        if len(embeds) > 1:
            await ctx.send(embed=view.initial, view=view)
        else:
            await ctx.send(embed=view.initial)


















































































async def setup(bot):
    await bot.add_cog(AutoResponder(bot))