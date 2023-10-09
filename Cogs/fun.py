
from discord.ext import commands
import datetime, pytz
from discord.ui import Button, Select, View
import aiosqlite
import openai
import requests, aiohttp, asyncpraw, discord, random



from Views.paginator import PaginatorView
from Extra import config




SLAP_LINKS = [
    'https://cdn.weeb.sh/images/Sk0RmyYvb.gif.',
    'https://cdn.weeb.sh/images/Hk6JVkFPb.gif',
    'https://cdn.weeb.sh/images/HJKiX1tPW.gif',
    'https://cdn.weeb.sh/images/SkxGcmJKPb.gif',
    'https://cdn.weeb.sh/images/rkaqm1twZ.gif',
    'https://cdn.weeb.sh/images/SkZTQkKPZ.gif',
    'https://cdn.weeb.sh/images/SkNimyKvZ.gif',
    'https://cdn.weeb.sh/images/Bkj-oaV0Z.gif',
    'https://cdn.weeb.sh/images/BkzyEktv-.gif',
    'https://cdn.weeb.sh/images/BJ8o71tD-.gif',
    'https://cdn.discordapp.com/attachments/1107206863818338406/1107207605094453309/6-_UTFD.gif',
    'https://cdn.discordapp.com/attachments/1107206863818338406/1107207605492916244/E7cfJjs.gif',
    'https://cdn.discordapp.com/attachments/1107206863818338406/1107207605891379220/JOKXwLd.gif',
    'https://cdn.discordapp.com/attachments/1107206863818338406/1107207606277247046/r4jONxp.gif',
    'https://cdn.discordapp.com/attachments/1107206863818338406/1107207606663127040/CJRHy2-.gif'
    ]













class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
        




    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def waifu(self, ctx):
        embed = discord.Embed(
            description=f"Generating the image.",
            color=config.color
        )
        embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url, url=f'https://discord.com/users/{ctx.author.id}')
        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)
        m = await ctx.send(embed=embed)

        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.waifu.pics/sfw/waifu') as response:
                data = await response.json()

                embed = discord.Embed(color=config.color)
                embed.set_image(
                    url=data['url']
                )
                embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url, url=f'https://discord.com/users/{ctx.author.id}')

                embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.display_avatar.url)

                await m.edit(embed=embed)

    

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def meme(self, ctx):
        embed_ = discord.Embed(
            description="Generating the meme.",
            color=config.color
        )
        embed_.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url, url=f'https://discord.com/users/{ctx.author.id}')
        m = await ctx.send(embed=embed_)


        async with aiohttp.ClientSession() as session:
            reddit = asyncpraw.Reddit(client_id='a-Yj35cZYdsyQCNlk-nGSA',
                                client_secret='Ha2wVtRgp0dyyE59SFURCXmXiueVCQ',
                                user_agent='reddit:a-Yj35cZYdsyQCNlk-nGSA:AnnoMy9257',
                                session=session)

            memes = await reddit.subreddit('memes')
            await memes.load()

            submission = await memes.random()
            title = submission.title
            url = submission.url_overridden_by_dest

            embed = discord.Embed(color=config.color)
            embed.add_field(name="Title", value=title)
            embed.set_image(url=url)
            embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url, url=f'https://discord.com/users/{ctx.author.id}')

            await m.edit(embed=embed)


    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def slap(self, ctx, user: discord.User):
        if ctx.author == user:
            return await ctx.send(f"You cannot slap yourself dumbo.")
        await ctx.typing()

        url = random.choice(SLAP_LINKS)

        embed = discord.Embed(color=config.color)
        embed.add_field(name=f"{ctx.author} Slapped {user}", value='\u200b')
        embed.set_image(url=url)
        embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url, url=f'https://discord.com/users/{ctx.author.id}')

        await ctx.send(embed=embed)























































async def setup(bot):
    await bot.add_cog(Fun(bot))