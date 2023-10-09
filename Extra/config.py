import discord, os
from discord.ext import commands


def owner():
    async def predicate(ctx: commands.Context):
        c = await ctx.bot.db.cursor()
        await c.execute("SELECT user_id FROM Owner")
        ids_ = await c.fetchall()
        if ids_ is None:
            return

        ids = [int(i[0]) for i in ids_]
        if ctx.author.id in ids:
            return True
        else:
            return False
    return commands.check(predicate)


def time(time):
    hours, remainder = divmod(time, 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)

    text = ''
    if days > 0:
        text += f"{hours} day{'s' if hours != 1 else ''}, "
    if hours > 0:
        text += f"{hours} hour{'s' if hours != 1 else ''}, "
    if minutes > 0:
        text += f"{minutes} minute{'s' if minutes != 1 else ''} and "
    text += f"{seconds} second{'s' if seconds != 1 else ''}"

    return text


def TimeConvert(time):
    pos = ["s","m","h","d"]
    time_dict = {"s" : 1, "m" : 60, "h" : 3600 , "d" : 3600*24}

    unit = time[-1]

    if unit not in pos:
        return -1
    try:
        val = int(time[:-1])
    except:
        return -2

    return val * time_dict[unit]









#EMBED
color = 0x2C2D31

#EMOJIS
Tick="<:tick_ultron:1099613531218911242>"
Cross="<:cross_ultron:1099613663775698994>"
Load = "<a:loading_ultron:1099612841390125067>"

TextChannel = "<:TextChannel_ultron:1099613755215724615>"
VoiceChannel = "<:VoiceChannel_ultron:1099618160702935071>"
StageChannel = "<:StageChannel_ultron:1099619854945898546>"


Red = "<:red_ultron:1099617876303958117>"
Green = "<:green_ultron:1099617960722714764>"
Yellow = "<:yellow_ultron:1099617972881997925>"


#LINKS
Support = "https://discord.gg/lnlhq"
Invite = "https://discord.com/api/oauth2/authorize?client_id=1103964690498998274&permissions=8&scope=bot"
Vote = "https://top.gg/bot/1059793976271577229/vote"


