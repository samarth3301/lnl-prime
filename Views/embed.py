import discord
from discord.ext import commands
import datetime, asyncio
from discord.ui import Button, Select, View
import aiosqlite, re, json

from discord import Interaction as intr
from Extra import config



class Panel(discord.ui.View):
    def __init__(self, bot, embed, message, state, author):
        self.bot = bot
        self.embed = embed
        self.message = message
        self.state = state
        self.author = author

        super().__init__(timeout=300)

    @discord.ui.button(label="Edit", style=discord.ButtonStyle.green)
    async def EditCallback(self,
                        intr: intr,
                        button: Button):
        if intr.user != self.author:
            await intr.response.send_message(f"{config.Cross} | Its not your interaction.", ephemeral=True)
            return
        
        def check(m):
            return m.author == intr.user and m.channel == intr.channel
        
        if self.state == 'Title':
            await intr.message.delete()
            que = await intr.channel.send(f"What would you like to set the `{self.state}`?")
            try:
                m = await self.bot.wait_for('message', check=check, timeout=160)
                dict = self.embed.to_dict()
                dict['title'] = str(m.content)

                embed = self.embed.from_dict(dict)
                self.embed.title = embed.title
                await self.message.edit(
                    embed=embed
                )
                await m.delete()
                await que.delete()
            except asyncio.TimeoutError:
                embed = discord.Embed(
                    description=f"**{intr.user}** You took too long. Good bye.",
                    color=config.color
                )
                await intr.channel.send(embed=embed)

        if self.state == 'Description':
            await intr.message.delete()
            que = await intr.channel.send(f"What would you like to set the `{self.state}`?")
            try:
                m = await self.bot.wait_for('message', check=check, timeout=160)
                dict = self.embed.to_dict()
                dict['description'] = str(m.content)

                embed = self.embed.from_dict(dict)
                self.embed.description = embed.description
                await self.message.edit(
                    embed=embed
                )
                try:
                    await m.delete()
                    await que.delete()
                except:
                    pass
            except asyncio.TimeoutError:
                embed = discord.Embed(
                    description=f"**{intr.user}** You took too long. Good bye.",
                    color=config.color
                )
                await intr.channel.send(embed=embed)

        if self.state == 'Image':
            await intr.message.delete()
            que = await intr.channel.send(f"What would you like to set the `{self.state}`?")
            try:
                m = await self.bot.wait_for('message', check=check, timeout=160)
                urls = re.findall("(?P<url>https?://[^\s]+)", m.content)
                if not urls:
                    try:
                        await m.delete()
                        await que.delete()
                    except:
                        pass
                    await self.message.edit(embed=self.embed)
                    await intr.channel.send(f"{config.Cross} | The image is not an url. Please provide a proper url.", delete_after=5)
                    return
                dict = self.embed.to_dict()
                if 'image' not in dict:
                    dict['image'] = {}
                dict['image']['url'] = str(m.content)

                embed = self.embed.from_dict(dict)
                self.embed.set_image(url=embed.image.url)
                await self.message.edit(
                    embed=embed
                )
                try:
                    await m.delete()
                    await que.delete()
                except:
                    pass
            except asyncio.TimeoutError:
                embed = discord.Embed(
                    description=f"**{intr.user}** You took too long. Good bye.",
                    color=config.color
                )
                await intr.channel.send(embed=embed)
        
        if self.state == 'Thumbnail':
            await intr.message.delete()
            que = await intr.channel.send(f"What would you like to set the `{self.state}`?")
            try:
                m = await self.bot.wait_for('message', check=check, timeout=160)
                urls = re.findall("(?P<url>https?://[^\s]+)", m.content)
                if not urls:
                    try:
                        await m.delete()
                        await que.delete()
                    except:
                        pass
                    await self.message.edit(embed=self.embed)
                    await intr.channel.send(f"{config.Cross} | The image is not an url. Please provide a proper url.", delete_after=5)
                    return
                
                dict = self.embed.to_dict()
                if 'thumbnail' not in dict:
                    dict['thumbnail'] = {}
                dict['thumbnail']['url'] = str(m.content)

                embed = self.embed.from_dict(dict)
                self.embed.set_thumbnail(url=embed.thumbnail.url)
                await self.message.edit(
                    embed=embed
                )
                try:
                    await m.delete()
                    await que.delete()
                except:
                    pass
            except asyncio.TimeoutError:
                embed = discord.Embed(
                    description=f"**{intr.user}** You took too long. Good bye.",
                    color=config.color
                )
                await intr.channel.send(embed=embed)
        
        if self.state == 'Color':
            await intr.message.delete()
            que = await intr.channel.send(f"What would you like to set the `{self.state}`?")
            try:
                m = await self.bot.wait_for('message', check=check, timeout=160)
                try:
                    color = int(m.content.strip("#"), 16)
                except ValueError:
                    try:
                        await que.delete()
                        await m.delete()
                    except: pass
                    await self.message.edit(
                        embed=self.embed
                    )
                    await intr.channel.send(f"{config.Cross} | Color must be a hex code.", delete_after=5)
                    return
                dict = self.embed.to_dict()
                dict['color'] = color

                embed = self.embed.from_dict(dict)
                self.embed.color = embed.color
                await self.message.edit(
                    embed=embed
                )
                try:
                    await m.delete()
                    await que.delete()
                except:
                    pass
            except asyncio.TimeoutError:
                embed = discord.Embed(
                    description=f"**{intr.user}** You took too long. Good bye.",
                    color=config.color
                )
                await intr.channel.send(embed=embed)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.primary)
    async def CancelCallback(self,
                        intr: intr,
                        button: Button):
        await intr.response.defer()
        dict_ = self.embed.to_dict()
        embed = self.embed.from_dict(dict_)
        await self.message.edit(
            embed=embed
        )
        await intr.delete_original_response()


    @discord.ui.button(label="Delete", style=discord.ButtonStyle.red)
    async def DeleteCallback(self,
                        intr: intr,
                        button: Button):
        dict = self.embed.to_dict()
        if self.state == 'Title':
            del dict['title']
            embed = self.embed.from_dict(dict)
            self.embed.title = embed.title 
            await self.message.edit(
                embed=embed
            )
            await intr.message.delete()

        if self.state == 'Description':
            if dict['title']:
                del dict['description']
                embed=self.embed.from_dict(dict)
                self.embed.description = embed.description 
                await self.message.edit(
                    embed=embed
                )
                await intr.message.delete()
            await intr.message.delete()

        if self.state == 'Author':
            try:
               del dict['author']
            except Exception:
                pass
            embed=self.emb.from_dict(dict)
            self.embed = embed
            await self.message.edit(
                embed=embed
            )
            await intr.message.delete()

        if self.state == 'Author URL':
            try:
               del dict['author']['icon_url']
            except Exception:
                pass
            embed=self.embed.from_dict(dict)
            self.embed = embed
            await self.message.edit(
                embed=embed
            )
            await intr.message.delete()

        if self.state == 'Image':
            try:
               del dict['image']
            except Exception:
                pass
            embed=self.embed.from_dict(dict)
            self.embed = embed
            await self.message.edit(
                embed=embed
            )
            await intr.message.delete()

        if self.state == 'Thumbnail':
            try:
               del dict['thumbnail']
            except Exception:
                pass
            embed=self.embed.from_dict(dict)
            self.embed = embed
            await self.message.edit(
                embed=embed
            )
            await intr.message.delete()
        
        if self.state == 'Thumbnail':
            try:
               del dict['color']
            except Exception:
                pass
            embed=self.embed.from_dict(dict)
            self.embed = embed
            await self.message.edit(
                embed=embed
            )
            await intr.message.delete()

    async def on_timeout(self):
        if self.message or self.message.channel is None:
            return
        
        for i in self.children:
            i.disabled = True
        await self.message.edit()
        self.stop()



class EmbedBuilder(discord.ui.View):
    def __init__(self,
                 bot,
                 embed):
        self.bot = bot
        self.embed = embed
        super().__init__(timeout=300)

    @discord.ui.select(
        placeholder="Edit Embed",
        options=[
        discord.SelectOption(label="Title"),
        discord.SelectOption(label="Description"),
        discord.SelectOption(label="Image"),
        discord.SelectOption(label="Thumbnail"),
        discord.SelectOption(label="Color")
        ]
        )
    async def callback(self, intr: intr, select: Select):
        if intr.user != self.author:
            await intr.response.send_message(f"{config.Cross} | Its not your interaction.", ephemeral=True)
            return
        
        if select.values[0] == "Title":
            view = Panel(bot=self.bot, embed=self.embed, message=self.message, state=str(select.values[0]), author=self.author)
            await intr.response.send_message(f"What action would you like to do for `{select.values[0]}`?",
                                            view=view
                                            )
        if select.values[0] == "Description":
            view = Panel(bot=self.bot, embed=self.embed, message=self.message, state=str(select.values[0]), author=self.author)
            await intr.response.send_message(f"What action would you like to do for `{select.values[0]}`?",
                                            view=view
                                            )
        if select.values[0] == "Image":
            view = Panel(bot=self.bot, embed=self.embed, message=self.message, state=str(select.values[0]), author=self.author)
            await intr.response.send_message(f"What action would you like to do for `{select.values[0]}`?",
                                            view=view
                                            )
        if select.values[0] == "Thumbnail":
            view = Panel(bot=self.bot, embed=self.embed, message=self.message, state=str(select.values[0]), author=self.author)
            await intr.response.send_message(f"What action would you like to do for `{select.values[0]}`?",
                                            view=view
                                            )
        if select.values[0] == "Color":
            view = Panel(bot=self.bot, embed=self.embed, message=self.message, state=str(select.values[0]), author=self.author)
            await intr.response.send_message(f"What action would you like to do for `{select.values[0]}`?",
                                            view=view
                                            )
            
    @discord.ui.button(label="Save", style=discord.ButtonStyle.green)
    async def SaveEmbedCallback(self,
                                intr: intr,
                                btn: Button):
        await intr.response.defer()
        if intr.user != self.author:
            await intr.followup.send(f"{config.Cross} | Its not your interaction.", ephemeral=True)
            return
        cur = await self.bot.db.cursor()
        await cur.execute("SELECT embed, state FROM Embed WHERE guild_id = ?", (intr.guild_id,))
        checker = await cur.fetchone()

        embed_dict = self.embed.to_dict()
        embed = json.dumps(embed_dict)
        if checker is not None:
            await cur.execute("UPDATE Embed SET embed = ? WHERE guild_id = ?", (embed, intr.guild_id))
            await intr.followup.send(f"{config.Tick} | Successfully saved the embed.", ephemeral=True)
        else:
            await cur.execute("INSERT INTO Embed(embed, state, ping, guild_id) VALUES(?, ?, ?, ?)", (embed, "disabled", 'disabled',intr.guild_id))
            await intr.followup.send(f"{config.Tick} | Successfully saved the embed.", ephemeral=True)
        
        await self.bot.db.commit()
        
        for i in self.children:
            i.disabled = True
        await intr.message.edit(view=self)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def CancelEmbedCallback(self,
                                intr: intr,
                                btn: Button):
        if intr.user != self.author:
            await intr.response.send_message(f"{config.Cross} | Its not your interaction.", ephemeral=True)
            return
        await intr.response.defer()
        for i in self.children:
            i.disabled = True
        await intr.message.edit(view=self)
        self.stop()






    async def on_timeout(self):
        for i in self.children:
            i.disabled = True
        await self.message.edit(view=self)
        self.stop()


































