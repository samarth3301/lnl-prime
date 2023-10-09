from typing import Optional
import discord
from discord.ext import commands
import datetime, pytz
from discord.ui import Button, Select, View
import aiosqlite, sqlite3
from difflib import get_close_matches


#Cogs
from Views.paginator import PaginatorView
from Extra import config














class HelpCommand(commands.HelpCommand):

  async def send_bot_help(self, mapping):
    
    cursor = await self.context.bot.db.cursor()
    await cursor.execute(f"SELECT prefix FROM Prefix WHERE guild_id = ?", (self.context.guild.id,))
    self.context.prefix = await cursor.fetchone()

    self.embed = discord.Embed(description=f"""Hey!! {self.context.author.mention} 

[Invite]({config.Invite}) | [Support server]({config.Support}) 
• My prefix for this server is `{self.context.prefix[0]}`
• Type `{self.context.prefix[0]}help <command | module>` for more info.

""", color=config.color)
    
    self.embed.add_field(
        name="Main",
        value=f"**<:automod_blaze:1104654258462269480> : Auto Moderation\n<:Mod_blaze:1099609762578047006> : Moderation\n<:gw_blaze:1099611646541963346> : Giveaway\n<:ticket_blaze:1099612005557612545> : Ticket\n<:utility_blaze:1099613611976032316> : Utility\n<:wlc_blaze:1099613768943665202> : Welcome**"
    )
    self.embed.add_field(
        name="Extra",
        value=f"**<:ar_blaze:1104654920537346099> : Auto Responder\n<:logging_blaze:1099613895171256450> : Logging\n<:media_blaze:1104655023872430150> : Media\n<:vc_blaze:1099614421153759283> : Voice Command\n<:fun_blaze:1117354667152789546> : Fun\n<:Blaze:1117353780179107931> : Bot**"
    )
    
    class HelpPanel(discord.ui.View):
        def __init__(self, author, embed):
            self.author = author
            self.embed = embed
            super().__init__(timeout=10)

        @discord.ui.select(placeholder="Choose a menu for commands.",
                        options=[
            discord.SelectOption(label="Home", emoji="<:home_blaze:1099620633379344415>"),
            discord.SelectOption(label="Auto Moderation", emoji="<:automod_blaze:1104654258462269480>"),
            discord.SelectOption(label="Moderation", emoji="<:Mod_blaze:1099609762578047006>"),
            discord.SelectOption(label="Giveaway", emoji="<:gw_blaze:1099611646541963346>"),
            discord.SelectOption(label="Ticket", emoji="<:ticket_blaze:1099612005557612545>"),
            discord.SelectOption(label="Utility", emoji="<:utility_blaze:1099613611976032316>"),
            discord.SelectOption(label="Welcome", emoji="<:wlc_blaze:1099613768943665202>"),

            discord.SelectOption(label="Auto Responder", emoji="<:ar_blaze:1104654920537346099>"),
            discord.SelectOption(label="Logging", emoji="<:logging_blaze:1099613895171256450>"),
            discord.SelectOption(label="Media", emoji="<:media_blaze:1104655023872430150>"),
            discord.SelectOption(label="Voice Command", emoji="<:vc_blaze:1099614421153759283>"),
            discord.SelectOption(label="Fun", emoji="<:fun_blaze:1117354667152789546>"),
            discord.SelectOption(label="Bot", emoji="<:Blaze:1117353780179107931>")
            ])
        async def callback(self, interaction: discord.Interaction, select: Select):
            if interaction.user != self.author:
                await interaction.response.send_message(content=f"This interaction cannot be controlled by you.", ephemeral=True)
                return
            if select.values[0] == "Home":
                await interaction.response.edit_message(embed=self.embed, view=view)

            if select.values[0] == "Auto Moderation":
                cog = interaction.client.get_cog("Auto Moderation")
                embed = discord.Embed(title=cog.qualified_name + " <:New_1:1104675788957175818><:New_2:1104675830703063050>", description=f", ".join(f"`{i.qualified_name}`" for i in cog.walk_commands()), color=config.color)
                embed.set_author(name=self.author, icon_url=self.author.display_avatar.url)
                embed.set_footer(text="Powered By Ultron HQ", icon_url=interaction.client.user.display_avatar)
                await interaction.response.edit_message(embed=embed, view=view)

            if select.values[0] == "Moderation":
                cog = interaction.client.get_cog("Moderation")
                embed = discord.Embed(title=cog.qualified_name, description=f", ".join(f"`{i.qualified_name}`" for i in cog.walk_commands()), color=config.color)
                embed.set_author(name=self.author, icon_url=self.author.display_avatar.url)
                embed.set_footer(text="Powered By Ultron HQ", icon_url=interaction.client.user.display_avatar)
                await interaction.response.edit_message(embed=embed, view=view)

            if select.values[0] == "Giveaway":
                cog = interaction.client.get_cog("Giveaway")
                embed = discord.Embed(title=cog.qualified_name, description=f", ".join(f"`{i.qualified_name}`" for i in cog.walk_commands()), color=config.color)
                embed.set_author(name=self.author, icon_url=self.author.display_avatar.url)
                embed.set_footer(text="Powered By Lock n Loaded HQ", icon_url=interaction.client.user.display_avatar)
                await interaction.response.edit_message(embed=embed, view=view)

            if select.values[0] == "Ticket":
                cog = interaction.client.get_cog("Ticket")
                embed = discord.Embed(title="Ticket", description=", ".join(f"`{i.qualified_name}`" for i in cog.walk_commands()), color=config.color)
                embed.set_author(name=self.author, icon_url=self.author.display_avatar.url)
                embed.set_footer(text="Powered By Lock N Loaded HQ", icon_url=interaction.client.user.display_avatar)
                await interaction.response.edit_message(embed=embed, view=view)

            if select.values[0] == "Utility":
                cog = interaction.client.get_cog("Utility")
                embed = discord.Embed(title=cog.qualified_name, description=f", ".join(f"`{i.qualified_name}`" for i in cog.walk_commands()), color=config.color)
                embed.set_author(name=self.author, icon_url=self.author.display_avatar.url)
                embed.set_footer(text="Powered By Ultron HQ", icon_url=interaction.client.user.display_avatar)
                await interaction.response.edit_message(embed=embed)

            if select.values[0] == "Welcome":
                cog = interaction.client.get_cog("Welcome")
                embed = discord.Embed(title=cog.qualified_name, description=f", ".join(f"`{i.qualified_name}`" for i in cog.walk_commands()), color=config.color)
                embed.set_author(name=self.author, icon_url=self.author.display_avatar.url)
                embed.set_footer(text="Powered By Ultron HQ", icon_url=interaction.client.user.display_avatar)
                await interaction.response.edit_message(embed=embed, view=view)



            if select.values[0] == "Auto Responder":
                cog = interaction.client.get_cog("Auto Responder")
                embed = discord.Embed(title=cog.qualified_name + " <:New_1:1104675788957175818><:New_2:1104675830703063050>", description=f", ".join(f"`{i.qualified_name}`" for i in cog.walk_commands()), color=config.color)
                embed.set_author(name=self.author, icon_url=self.author.display_avatar.url)
                embed.set_footer(text="Powered By Ultron HQ", icon_url=interaction.client.user.display_avatar)
                await interaction.response.edit_message(embed=embed)

            if select.values[0] == "Logging":
                cog = interaction.client.get_cog("Logging")
                embed = discord.Embed(title=cog.qualified_name, description=f", ".join(f"`{i.qualified_name}`" for i in cog.walk_commands()), color=config.color)
                embed.set_author(name=self.author, icon_url=self.author.display_avatar.url)
                embed.set_footer(text="Powered By Ultron HQ", icon_url=interaction.client.user.display_avatar)
                await interaction.response.edit_message(embed=embed)

            if select.values[0] == "Media":
                cog = interaction.client.get_cog("Media")
                embed = discord.Embed(title=cog.qualified_name + " <:New_1:1104675788957175818><:New_2:1104675830703063050>", description=f", ".join(f"`{i.qualified_name}`" for i in cog.walk_commands()), color=config.color)
                embed.set_author(name=self.author, icon_url=self.author.display_avatar.url)
                embed.set_footer(text="Powered By Ultron HQ", icon_url=interaction.client.user.display_avatar)
                await interaction.response.edit_message(embed=embed)

            if select.values[0] == "Voice Command":
                cog = interaction.client.get_cog("Voice")
                embed = discord.Embed(title=cog.qualified_name + " Command", description=f", ".join(f"`{i.qualified_name}`" for i in cog.walk_commands()), color=config.color)
                embed.set_author(name=self.author, icon_url=self.author.display_avatar.url)
                embed.set_footer(text="Powered By Ultron HQ", icon_url=interaction.client.user.display_avatar)
                await interaction.response.edit_message(embed=embed)

            if select.values[0] == "Fun":
                cog = interaction.client.get_cog("Fun")
                embed = discord.Embed(title=cog.qualified_name, description=f", ".join(f"`{i.qualified_name}`" for i in cog.walk_commands()), color=config.color)
                embed.set_author(name=self.author, icon_url=self.author.display_avatar.url)
                embed.set_footer(text="Powered By Ultron HQ", icon_url=interaction.client.user.display_avatar)
                await interaction.response.edit_message(embed=embed)

            if select.values[0] == "Bot":
                cog = interaction.client.get_cog("Bot")
                embed = discord.Embed(title="Bot", description=f", ".join(f"`{i.qualified_name}`" for i in cog.walk_commands()), color=config.color)
                embed.set_author(name=self.author, icon_url=self.author.display_avatar.url)
                embed.set_footer(text="Powered By Ultron HQ", icon_url=interaction.client.user.display_avatar)
                await interaction.response.edit_message(embed=embed)


        async def on_timeout(self):
            if len(self.children) == 0: return
            
            for i in self.children:
                i.disabled = True
            try:
                await self.message.edit(view=self)
            except Exception:
                pass

    inv = discord.ui.Button(label="Invite Lock N Loaded Prime", url=config.Invite)
    support = discord.ui.Button(label="Support Server", url=config.Support)
    view = HelpPanel(author=self.context.author, embed=self.embed).add_item(inv).add_item(support)

    self.embed.set_author(name=self.context.author, icon_url=self.context.author.display_avatar.url)
    self.embed.set_footer(text=f"Powered by BlaZe HQ", icon_url=self.context.bot.user.display_avatar.url)
    self.embed.set_image(url="https://cdn.discordapp.com/attachments/1129434939973177344/1129527008834105354/standard_-_2023-05-26T134214.453.gif")
    if self.context.guild.icon:
        self.embed.set_thumbnail(url=self.context.guild.icon.url)
    else:
        self.embed.set_thumbnail(url=self.context.bot.user.display_avatar.url)

    view.message = await self.context.send(embed=self.embed, view=view)







  async def send_command_help(self, command):
    await self.filter_commands(self.context.bot.commands)
    if len(command.description) == 0:
      command.description = "No description provided."
    embed = discord.Embed(description=f"```diff\n- [] = optional argument\n- <> = required argument\n- Do NOT type these when using commands.```\n>>> {command.description}", color=config.color)
    alias = command.aliases
    if alias:
        embed.add_field(name="Aliases", value=", ".join(f"`{x}`" for x in alias))
    embed.add_field(name="Usage", value=f"`{self.get_command_signature(command)}`", inline=False)
    embed.set_author(name=self.context.bot.user.name, icon_url=self.context.bot.user.display_avatar.url)
    embed.timestamp = datetime.datetime.utcnow()
    embed.set_footer(text=self.context.bot.user.name, icon_url=self.context.bot.user.display_avatar.url)
    channel = self.get_destination()
    await channel.send(embed=embed)
    

  def get_command_signature(self, command):
          db = sqlite3.connect("Main.db")
          cur = db.cursor()
          cur.execute("SELECT prefix FROM Prefix WHERE guild_id = ?", (self.context.guild.id,))
          p = cur.fetchone()
          parent = command.parent
          entries = []
          while parent is not None:
              if not parent.signature or parent.invoke_without_command:
                  entries.append(parent.name)
              else:
                  entries.append(parent.name + ' ' + parent.signature)
              parent = parent.parent
          parent_sig = ' '.join(reversed(entries))
          alias = command.name if not parent_sig else parent_sig + ' ' + command.name

          return f'{p[0]}{alias} {command.signature}'
  

  async def send_group_help(self, group):
    z = await self.filter_commands(group.commands)
    
    if len(z) == 0:
        return self.command_not_found(group)

    embeds = []
    str1 = [self.get_command_signature(i) for i in group.commands]
    str2 = [i.description if len(i.description) != 0 else 'No description provided.' for i in group.commands]


    for chunk in discord.utils.as_chunks(zip(str1, str2), 10):
        embed = discord.Embed(title=f"`{self.get_command_signature(group)}`", color=config.color)
        embed.description = ''
        embed.set_author(name=self.context.bot.user.name, icon_url=self.context.bot.user.display_avatar.url)
        embed.set_footer(text=f"{self.context.author}", icon_url=self.context.author.display_avatar.url)
        for i, z in chunk:
            embed.description += f"".join(f"`{i}`\n{z}\n\n");
        embeds.append(embed)
    
    
    channel = self.get_destination()
    if len(embeds) > 1:
        view = PaginatorView(embeds, bot=self.context.bot, author=self.context.author)
        view.message = await channel.send(embed=view.initial, view=view)
    else:
        view2 = PaginatorView(embeds, bot=self.context.bot, author=self.context.author)
        view2.message = await channel.send(embed=view2.initial)
  


  async def send_cog_help(self, cog):
    await self.filter_commands(self.context.bot.commands, show_hidden=False)

    embed = discord.Embed(description=f", ".join(f"`{i.qualified_name}`" for i in cog.walk_commands()), color=config.color)

    embed.set_author(name=self.context.bot.user.name, icon_url=self.context.bot.user.display_avatar.url)
    embed.timestamp = datetime.datetime.now()
    embed.set_footer(text=f"Requested By {self.context.author}", icon_url=self.context.author.display_avatar.url)
    channel = self.get_destination()
    await channel.send(embed=embed)





  async def command_not_found(self, string):
      cmds_list = [cmd.name for cmd in self.context.bot.commands]
      matches = get_close_matches(string, cmds_list)

      if len(matches) > 0: 
          match_list = enumerate([f"{match}" for match in matches], start=1)

          embed = discord.Embed(description=f"Could not find `{string}` command.\n\nDid you mean:\n"+ "".join(f'`[{i}]` {z}\n' for i, z in match_list), color=config.color)
          embed.set_author(name=self.context.bot.user.name + " Error", icon_url=self.context.bot.user.display_avatar.url)
          embed.timestamp = datetime.datetime.utcnow()
          await self.context.send(embed=embed)

      else:
          embed2 = discord.Embed(description=f"Could not find `{string}` command.", color=config.color)
          embed2.set_author(name=self.context.bot.user.name + " Error", icon_url=self.context.bot.user.display_avatar.url)
          embed2.timestamp = datetime.datetime.utcnow()
          await self.context.send(embed=embed2)


  async def subcommand_not_found(self, command, string):
      cmds_list = [cmd.name for cmd in self.context.bot.commands]
      matches = get_close_matches(string, cmds_list)

      if len(matches) > 0:
          match_list = enumerate([f"{match}" for match in matches], start=1)
          embed = discord.Embed(description=f"Could not find `{string}` command.\n\nDid you mean:\n"+ "".join(f'`[{i}]` {z}\n' for i, z in match_list), color=config.color)
          embed.set_author(name=self.context.bot.user.name + " Error", icon_url=self.context.bot.user.display_avatar.url)
          embed.timestamp = datetime.datetime.utcnow()
          await self.context.send(embed=embed)

      else:
          embed2 = discord.Embed(description=f"Could not find `{string}` subcommand for `{command}` command.", color=config.color)
          embed2.set_author(name=self.context.bot.user.name + " Error", icon_url=self.context.bot.user.display_avatar.url)
          embed2.timestamp = datetime.datetime.utcnow()
          await self.context.send(embed=embed2)


  async def send_error_message(self, error):
      if isinstance(error, commands.BadArgument):
        embed = discord.Embed(description=str(error))
        embed.set_author(name=self.context.bot.user.name + " Error", icon_url=self.context.bot.user.display_avatar.url, color=config.color)
        embed.timestamp = datetime.datetime.utcnow()
        await self.context.send(embed=embed)

     



        

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        for i in self.bot.commands:
           if len(i.description) == 0:
              i.description = "No description provided."
        attributes = {
        'aliases': ["h"],
        'cooldown': commands.CooldownMapping.from_cooldown(1, 3.0, commands.BucketType.user),
      } 
              
        Help = HelpCommand(command_attrs=attributes)
        bot.help_command = Help
        bot.help_command.cog = self
        "bot._BotBase__cogs = commands.core._CaseInsensitiveDict()"
        
    def cog_unload(self):
        self.bot.help_command = self._original_help_command






async def setup(bot):
  await bot.add_cog(Help(bot))