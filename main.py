from discord.ext import commands, tasks
import discord
import os
import jishaku
import aiosqlite
import datetime, pytz, time
from discord.ui import Button, View
import asyncio
import random, sys, wavelink
from wavelink.ext import spotify


from Extra import config




class MyContext(commands.Context):
    async def send(self, content: str = None, *args, **kwargs) -> discord.Message:
        return await super().send(content, *args, **kwargs)
    

    
    


intents = discord.Intents.all()

async def get_prefix(client, message):
    if str(message.channel.type) == 'private':
        return await message.channel.send("Currently Ultron is not available in DMs.")

    cursor = await client.db.execute(f"""SELECT prefix FROM Prefix WHERE guild_id = {message.guild.id}""")
    resultz = await cursor.fetchone()
    cursor = await client.db.execute(f"SELECT users FROM Np")
    NP = await cursor.fetchall()
    if resultz is None:
        await client.db.execute("INSERT INTO Prefix(prefix, guild_id) VALUES(?, ?)", ("$", message.guild.id,))
        await client.db.commit()

    c = await client.db.execute("SELECT prefix FROM Prefix WHERE guild_id = ?", (message.guild.id,))
    result = await c.fetchone()

    if message.author.id in ([int(i[0]) for i in NP]):
        a = commands.when_mentioned_or('', result[0])(client, message)
        return sorted(a, reverse=True)
    else:
        return commands.when_mentioned_or(result[0])(client, message)


class Bot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix=get_prefix,
                        intents=intents,
                        shards=2,
                        shard_count=2,
                        case_insensitive=True,
                        strip_after_prefix=True,
                        status=discord.Status.online,
                        activity=discord.Activity(type=discord.ActivityType.listening, name="$help"),
                        )

    async def setup_hook(self):
        self.db = await aiosqlite.connect("Main.db")
        self.cd = commands.CooldownMapping.from_cooldown(1, 10, commands.BucketType.user)
        cur = await self.db.cursor()
        
        await cur.execute("CREATE table if not exists guildpremium(guild_id TEXT NOT NULL, end_time TEXT, activator TEXT, tier TEXT)")
        await cur.execute("CREATE table if not exists Userpremium(user_id TEXT NOT NULL, end_time TEXT, prime_count TEXT, tier TEXT)")
        await cur.execute("create table if not exists badge(user_id TEXT, badge TEXT)")



        self.launch_time = datetime.datetime.utcnow()

        await self.load_extension("jishaku")
        await self.load_extension("HelpCog")
        await self.load_extension("Cogs.Utility")
        await self.load_extension("Cogs.ModerationCog")
        await self.load_extension("Cogs.welcome")
        await self.load_extension("Cogs.Logging")
        await self.load_extension("Cogs.media")
        await self.load_extension("Cogs.vc")
        await self.load_extension("Cogs.bot")
        await self.load_extension("Cogs.owner")
        await self.load_extension("Events.events")
        await self.load_extension("Events.events2")
        await self.load_extension("Cogs.ticket")
        await self.load_extension("Cogs.giveaway")
        await self.load_extension("Cogs.fun")
        await self.load_extension("Extra.persistent")
        await self.load_extension("Cogs.automod")
        await self.load_extension("Cogs.autoresponder")
        await self.load_extension("Cogs.errors")
        await self.load_extension("Cogs.music")
        
        await self.db.commit()
        asyncio.create_task(DBRefresher())
        print(f"Logged In As {client.user}\nID - {client.user.id}")

    

    

    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=cls or MyContext)


client = Bot()


client.owner_ids = [1099056487868924074, 1141024007727095898, 1112221047555629199]



client.Version = "v1.8"










async def DBRefresher():...
















@client.check
@commands.cooldown(1, 60.0, commands.BucketType.user)
async def bl(ctx):
    cur = await client.db.cursor()
    await cur.execute("SELECT user_id FROM Blacklisted")
    user = await cur.fetchall()
    if ctx.author.id in [int(i[0]) for i in user] and ctx.author.id not in client.owner_ids:
        bucket = client.cd.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()

        if retry_after: return
        
        embed = discord.Embed(description=f"{config.Cross} | You cannot use my commands as you're banned from using me.\n\nReach [Support Server](https://discord.gg/MS2Dd4mSXV) to appeal.")
        embed.color = config.color
        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text=client.user.name, icon_url=client.user.display_avatar.url)
        await ctx.channel.send(embed=embed)
        return False
    elif ctx.author.id not in [int(i[0]) for i in user]:
        return True




@client.event
async def on_message_edit(before, after):
    ctx: MyContext = await client.get_context(after, cls=MyContext)
    if before.content != after.content:
        if after.guild is None or after.author.bot:
            return
        if ctx.command is None:
            return
        if str(ctx.channel.type) == "public_thread":
            return
        await client.invoke(ctx)
    else:
        return


@client.check
async def PrimeCheck(ctx: commands.Context):
    cmd_list = ['help', 'managepremium', 'prime']

    if ctx.command.name.lower() in cmd_list:
        return True
    
    if ctx.command.root_parent:
        if ctx.command.root_parent.name.lower() in cmd_list:
            return True
    
    c = await client.db.cursor()
    await c.execute("SELECT end_time FROM GuildPremium WHERE guild_id = ?", (ctx.guild.id,))
    re = await c.fetchone()


    if re is not None:
        return True
    else:
        embed = discord.Embed(
            description=f"You need premium!",
            color=config.color
        )

        await ctx.send(embed=embed)



os.environ['JISHAKU_FORCE_PAGINATOR'] = 'True'
os.environ['JISHAKU_NO_UNDERSCORE'] = 'True'

 

ultron = ""


client.run(ultron, reconnect=True)
asyncio.run(client.db.close())