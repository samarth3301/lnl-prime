import discord
from discord.ext import commands
import datetime
import pytz
import aiosqlite


from Extra import config





class Button(discord.ui.Button):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(label="Create Ticket", style=discord.ButtonStyle.secondary, emoji='📩', custom_id='persistent_view:grey')

    async def callback(self, interaction: discord.Interaction) -> discord.ui.Button:
      await interaction.response.defer()
      cur = await self.bot.db.cursor()
      await cur.execute("SELECT user_id FROM TicketUser WHERE guild_id = ?", (interaction.guild_id,))
      TicketMem = await cur.fetchall()

      if TicketMem != []:
         if interaction.user.id in [int(i[0]) for i in TicketMem]:
            await interaction.followup.send(f"{config.Cross} | You've already created a ticket, you cannot create more.", ephemeral=True)
            return


      await cur.execute(f"SELECT category_id, support_roleid FROM Ticket WHERE message_id = ?", (interaction.message.id,))
      result = await cur.fetchall()


      category = [int(i[0]) for i in result]
      support = [i[1] for i in result]

      cate = discord.utils.get(interaction.guild.categories, id=category[0])
      if cate is None:
         return await interaction.followup.send("Something went wrong while creating the ticket maybe the category was deleted.")
 
      roleobj = None
      if str(support).lower() in ['none', 'no', 'nah']:
         roleobj = None
      else:
         roleobj = interaction.guild.get_role(support[0])

      channel = await interaction.guild.create_text_channel(name=f"ticket-{interaction.user.name}", category=cate)
      await channel.set_permissions(interaction.user, view_channel=True)
      await channel.set_permissions(interaction.guild.default_role, view_channel=False, send_messages=True, add_reactions=True, embed_links=True)

      if roleobj is not None:
         await channel.set_permissions(roleobj, overwrite=discord.PermissionOverwrite(
            view_channel=True,
            read_messages=True
         ))

      await interaction.followup.send(f"{config.Tick} | Successfully created a ticket {channel.mention}", ephemeral=True)

      cur = await self.bot.db.cursor()
      await cur.execute(f"INSERT INTO TicketUser(user_id, guild_id, channel_id) VALUES(?, ?, ?)", (interaction.user.id, interaction.guild.id, channel.id))

      if support[0].lower() in ['none']:
         support_mention = None
      else:
         support_mention = f'<@&{int(support[0])}>'


      embed=discord.Embed(description="Support will be with you shortly.\nTo close this ticket click the 🔒 button.", color=config.color)
      embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)

      msg = await channel.send(f"{interaction.user.mention} Welcome"+"".join(f' {support_mention}' if support_mention is not None else ''), embed=embed, view=TicketView(bot=self.bot))
      await msg.pin()
      await self.bot.db.commit()

class ButtonView(discord.ui.View):
   def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)
        self.add_item(Button(self.bot))
   


class TicketView(discord.ui.View):
   def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)

   @discord.ui.button(label="Close", emoji='🔒', style=discord.ButtonStyle.danger, custom_id='close_ticket_button')
   async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
      cur = await self.bot.db.cursor()
      await cur.execute(f"SELECT user_id FROM TicketUser WHERE guild_id = ? AND channel_id = ?", (interaction.guild.id, interaction.channel_id))
      result = await cur.fetchone()
      user = interaction.guild.get_member(int(result[0]))
      await interaction.response.send_message("Closing the ticket, please wait...", ephemeral=True)
      await interaction.message.edit(view=None)

      await interaction.message.channel.set_permissions(user, overwrite=(
         discord.PermissionOverwrite(
         view_channel=False
         )))
      embed1=discord.Embed(title="📩 Ticket Closed", description=f"{interaction.channel.mention} has been closed by {interaction.user}", color=config.color)

      cur2 = await self.bot.db.cursor()
      await cur2.execute(f"SELECT channel_id, user_id FROM TicketUser WHERE guild_id = ? AND channel_id = ?", (interaction.guild.id, interaction.channel_id))
      re = await cur2.fetchall()
      channel_ = [i[0] for i in re]
      global user_
      user_ = [i[1] for i in re]
      c = self.bot.get_channel(int(channel_[0]))


      view = ClosePanel(bot=self.bot)
      await c.send(embed=embed1, view=view)
      await self.bot.db.commit()



class ClosePanel(discord.ui.View):
   def __init__(self, bot):
      self.bot = bot
      super().__init__(timeout=None)

   @discord.ui.button(label='Open', emoji='🔓', custom_id="persistent:grey1")
   async def callback(self, interaction: discord.Interaction, button: discord.ui.Button):
      cur = await self.bot.db.cursor()
      await cur.execute(f"SELECT user_id FROM TicketUser WHERE guild_id = ? AND channel_id = ?", (interaction.guild.id, interaction.channel_id))
      re = await cur.fetchone()
      u = interaction.guild.get_member(int(re[0]))

      await interaction.message.channel.set_permissions(u, overwrite=(
         discord.PermissionOverwrite(
         view_channel=True
         )
      ))

      await interaction.response.send_message(f"{config.Tick} | Successfully opened the ticket", ephemeral=True)
      await interaction.message.delete()

      cha = interaction.channel
      embed=discord.Embed(description="Support will be with you shortly.\nTo close this ticket click the 🔒 button.", color=config.color)
      embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
      await cha.send(f"{interaction.user.mention} Welcome. This ticket has reopened", embed=embed, view=TicketView(bot=self.bot))

   @discord.ui.button(label='Delete', emoji='⛔', custom_id="persistent:grey2")
   async def callback2(self, interaction: discord.Interaction,  button: discord.ui.Button):
      await interaction.response.send_message(f"{config.Tick} | Deleting the ticket please wait...", ephemeral=True)

      cur3 = await self.bot.db.cursor()
      await cur3.execute(f"SELECT user_id FROM TicketUser WHERE guild_id = ? AND channel_id = ?", (interaction.guild.id, interaction.channel_id))
      re = await cur3.fetchone()
      u = self.bot.get_user(int(re[0]))


      await cur3.execute("DELETE FROM TicketUser WHERE guild_id = ? AND channel_id = ? AND user_id = ?", (interaction.guild.id, interaction.channel_id, u.id))
      await interaction.channel.delete(reason="Closed Ticket.")
      
      await self.bot.db.commit()




















class Ticket(commands.Cog):
   def __init__(self, bot):
      self.bot = bot

   @commands.group(invoke_without_command=True, description="Ticket commands.")
   @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
   async def ticket(self, ctx):
      await ctx.send_help(ctx.command)
   
   @ticket.group(invoke_without_command=True, description="Ticket panel commands.")
   @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
   async def panel(self, ctx):
      await ctx.send_help(ctx.command)
   
   @panel.command(description="Creates a panel of ticket.")
   @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
   async def setup(self, ctx):
         cur = await self.bot.db.cursor()
         await cur.execute("SELECT message_id, channel_id FROM Ticket WHERE guild_id = ?", (ctx.guild.id,))
         ms04 = await cur.fetchall()

         msg__ = [int(i[0]) for i in ms04]
         ch__ = [int(i[1]) for i in ms04]

         if ms04 != []:
            channel = ctx.guild.get_channel(ch__[0])
            if channel is None:
               await cur.execute("DELETE FROM Ticket WHERE guild_id = ? AND channel_id = ?", (ctx.guild.id, ch__[0]))
               await self.bot.db.commit()
            else:
               try:
                  message = await channel.fetch_message(msg__[0])
               except discord.NotFound:
                  await cur.execute("DELETE FROM Ticket WHERE guild_id = ? AND channel_id = ?", (ctx.guild.id, ch__[0]))
                  await self.bot.db.commit()

         await cur.execute("SELECT message_id FROM Ticket WHERE guild_id = ?", (ctx.guild.id,))
         re = await cur.fetchall()

         if re != []:
            await ctx.send(f"{config.Cross} | This server has reached the maximum limit. No more panels can be created")
            return
         
         def check(message):
            return message.channel == ctx.channel and message.author == ctx.author
         
         embed = discord.Embed(title="📩 Ticket Setup", color=config.color, description="`In which channel should the panel be created? | Please provide the id.`")
         embed.set_footer(text="Type 'cancel' to cancel the process.", icon_url=self.bot.user.display_avatar.url)
         await ctx.send(embed=embed)
         
         channel_message = await self.bot.wait_for('message', check=check, timeout=40)

         if str(channel_message.content).lower() == 'cancel':
            em = discord.Embed(description=f"**{ctx.author}** Alright, I've stopped the process.", color=config.color)
            em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
            em.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=em)
            return

         try:
           channel_ = await commands.TextChannelConverter().convert(ctx=ctx, argument=str(channel_message.content))
         except commands.ChannelNotFound:
            await ctx.send(f"{config.Cross} | Channel '{channel_message.content}' wasn't found.")
            return
         
         embed = discord.Embed(title="📩 Ticket Setup", color=config.color, description="`Provide a support role for the ticket. If not type 'None' | Please provide the id.`")
         embed.set_footer(text="Type 'cancel' to cancel the process.", icon_url=self.bot.user.display_avatar.url)
         await ctx.send(embed=embed)
         
         support_role_message = await self.bot.wait_for('message', check=check, timeout=40)

         if str(support_role_message.content).lower() == 'cancel':
            em = discord.Embed(description=f"**{ctx.author}** Alright, I've stopped the process.", color=config.color)
            em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
            em.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=em)
            return
         
         support_role = None
         if str(support_role_message.content).lower() not in ['no', 'none', 'nah']:
            try:
               support_role = await commands.RoleConverter().convert(ctx=ctx, argument=str(support_role_message.content))
            except commands.RoleNotFound:
               await ctx.send(f"{config.Cross} | Role '{support_role_message.content}' wasn't found.")
               return

   
         
         embed = discord.Embed(title="📩 Ticket Setup", color=config.color, description="`In which category should tickets be created? | Please provide the id.`")
         embed.set_footer(text="Type 'cancel' to cancel the process.", icon_url=self.bot.user.display_avatar.url)
         await ctx.send(embed=embed)
         
         category_message = await self.bot.wait_for('message', check=check, timeout=40)

         if str(category_message.content).lower() == 'cancel':
            em = discord.Embed(description=f"**{ctx.author}** Alright, I've stopped the process.", color=config.color)
            em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
            em.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=em)
            return
         

         try:
           category = await commands.CategoryChannelConverter().convert(ctx=ctx, argument=str(category_message.content))
         except commands.ChannelNotFound:
            await ctx.send(f"{config.Cross} | Category '{category_message.content}' wasn't found.")
            return
         
         curr = await self.bot.db.cursor() 

         em = discord.Embed(title="Ticket", description="To create a ticket click the 📩 button.", color=config.color)
         em.set_footer(text=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
         view = ButtonView(bot=self.bot)

         message = await channel_.send(embed=em, view=view)


         support_role_id = support_role.id if support_role is not None else 'none'

         await curr.execute(f"INSERT INTO Ticket(guild_id, support_roleid, channel_id, category_id, message_id) VALUES(?, ?, ?, ?, ?)", (ctx.guild.id, support_role_id, channel_.id, category.id, message.id))
         
         await ctx.send(f"{config.Tick} | Successfully created a ticket in {channel_.mention}.")
         await self.bot.db.commit()


   @ticket.command(description="Adds a user to ticket.")
   @commands.check_any(commands.is_owner(), commands.has_permissions(manage_channels=True))
   async def add(self, ctx, member: discord.Member):
      cur = await self.bot.db.cursor() 

      await cur.execute(f"SELECT user_id, channel_id FROM TicketUser WHERE guild_id = ?", (ctx.guild.id, ))
      re = await cur.fetchall()
      if re != []:
         try:
            dbuser = [int(i[0]) for i in re]
            channeldb = [int(i[1]) for i in re]
            u = ctx.guild.get_member(int(dbuser[0]))
         except: pass

      if not member in ctx.guild.members:
         await ctx.send(f"{config.Cross} | This user is not in this server.")
         return
      if ctx.channel.id not in channeldb:
         await ctx.send(f"{config.Cross} | This channel isn't a ticket.")
         return
      if u.id == member.id:
         await ctx.send(f"{config.Cross} | The user is already the owner of the ticket.")
         return
      
      await ctx.channel.set_permissions(member, overwrite=(
         discord.PermissionOverwrite(
         view_channel=True
         )
      ))
      await ctx.send(f"{config.Tick} | Successfully added {member} to {ctx.channel.mention}")

   @ticket.command(description="Removes a user from the ticket.")
   @commands.check_any(commands.is_owner(), commands.has_permissions(manage_channels=True))
   async def remove(self, ctx, member: discord.Member):
      cur = await self.bot.db.cursor() 
      await cur.execute(f"SELECT user_id, channel_id FROM TicketUser WHERE guild_id = ?", (ctx.guild.id, ))
      re = await cur.fetchall()
      dbuser = [int(i[0]) for i in re]
      channelObj = [int(i[1]) for i in re]


      if ctx.channel.id != channelObj[0]:
         await ctx.send(f"{config.Cross} | This channel isn't a ticket.")
         return
      if dbuser[0] == member.id:
         await ctx.send(f"{config.Cross} | The user is the owner of the ticket.")
         return
      await ctx.channel.set_permissions(member, overwrite=(
         discord.PermissionOverwrite(
         view_channel=False
         )
      ))
      await ctx.send(f"{config.Tick} | Successfully removed {member} from {ctx.channel.mention}")




   @commands.Cog.listener("on_guild_channel_delete")
   async def TicketChannelDelete(self, channel: discord.TextChannel):
      c = await self.bot.db.cursor()
      await c.execute("SELECT channel_id FROM TicketUser where guild_id = ?", (channel.guild.id,))
      channel_ids_raw = await c.fetchall()

      channel_ids = [int(i[0]) for i in channel_ids_raw]

      if channel.id in channel_ids:
         await c.execute("DELETE FROM TicketUser WHERE guild_id = ? AND channel_id = ?", (channel.guild.id, channel.id))
      await self.bot.db.commit()








async def setup(bot):
    await bot.add_cog(Ticket(bot))