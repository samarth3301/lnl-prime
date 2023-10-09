import discord
from discord.ext import commands
import datetime
import pytz


from Extra import config

class Voice(commands.Cog):
    def __init__(self,  bot):
        self.bot = bot

    @commands.group(description="Voice commands.", invoke_without_command=True)
    @commands.check_any(commands.is_owner(), commands.has_permissions(moderate_members=True))
    async def voice(self, ctx):
        await ctx.send_help(ctx.command)
  
    @voice.command(description="Mute a user in the voice channel.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(moderate_members=True))
    async def mute(self, ctx, member: discord.Member, *, reason: str=None):
        reason = reason or "[No reason]"

        await member.edit(mute=True, reason=f"By {ctx.author}: {reason}")
        await ctx.send(f"{config.Tick} | Successfully voice muted {member.mention}", allowed_mentions=discord.AllowedMentions.none())

    @voice.command(description="Unmute a user in the voice channel.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(moderate_members=True))
    async def unmute(self, ctx, member: discord.Member, *, reason: str=None):
        reason = reason or "[No reason]"

        await member.edit(mute=False, reason=f"By {ctx.author}: {reason}")
        await ctx.send(f"{config.Tick} | Successfully voice unmuted {member.mention}", allowed_mentions=discord.AllowedMentions.none())

    @voice.command(description="Deafen a user in the voice channel.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(moderate_members=True))
    async def deafen(self, ctx, member: discord.Member, *, reason: str=None):
        reason = reason or "[No reason]"

        await member.edit(deafen=True, reason=f"By {ctx.author}: {reason}")
        await ctx.send(f"{config.Tick} | Successfully voice deafened {member.mention}", allowed_mentions=discord.AllowedMentions.none())

    @voice.command(description="Undeafen a user in the voice channel.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(moderate_members=True))
    async def undeafen(self, ctx, member: discord.Member, *, reason: str=None):
        reason = reason or "[No reason]"

        await member.edit(deafen=False, reason=f"By {ctx.author}: {reason}")
        await ctx.send(f"{config.Tick} | Successfully voice undeafened {member.mention}", allowed_mentions=discord.AllowedMentions.none())

    @voice.command(description="Mutes all the users in the voice channel.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(moderate_members=True))
    async def muteall(self, ctx, *, reason: str=None):
        reason = reason or "[No reason]"
        if ctx.author.voice is None:
            await ctx.send(f"You're not in any voice channel.")
            return
        voice_channel = ctx.author.voice.channel
        unmuted_len = 0
        for user in voice_channel.members:
            if not user.voice.mute:
                unmuted_len += 1
        await ctx.send(f"{config.Tick} | Voice muting {unmuted_len} users...")
        muted_len = 0
        for user in voice_channel.members:
            if not user.voice.mute:
                muted_len += 1
            await user.edit(mute=True, reason=f"By {ctx.author}: {reason}")

        await ctx.send(f"{config.Tick} | Successfully voice muted {muted_len} users")

    @voice.command(description="Mutes all the users in the voice channel.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(moderate_members=True))
    async def unmuteall(self, ctx, *, reason: str=None):
        reason = reason or "[No reason]"
        if ctx.author.voice is None:
            await ctx.send(f"You're not in any voice channel.")
            return
        voice_channel = ctx.author.voice.channel
        muted_len = 0
        for user in voice_channel.members:
            if user.voice.mute:
                muted_len += 1
        await ctx.send(f"{config.Tick} | Voice unmuting {muted_len} users...")
        _len = 0
        for user in voice_channel.members:
            if user.voice.mute:
                _len += 1
            await user.edit(mute=False, reason=f"By {ctx.author}: {reason}")

        await ctx.send(f"{config.Tick} | Successfully voice unmuted {_len} users")

    @voice.command(description="Deafens all the users in the voice channel.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(moderate_members=True))
    async def deafenall(self, ctx, *, reason: str=None):
        reason = reason or "[No reason]"
        if ctx.author.voice is None:
            await ctx.send(f"You're not in any voice channel.")
            return
        voice_channel = ctx.author.voice.channel
        undeafened_len = 0
        for user in voice_channel.members:
            if not user.voice.deaf:
                undeafened_len += 1
        await ctx.send(f"{config.Tick} | Voice deafening {undeafened_len} users...")
        deafened_len = 0
        for user in voice_channel.members:
            if not user.voice.deaf:
                deafened_len += 1
            await user.edit(deafen=True, reason=f"By {ctx.author}: {reason}")

        await ctx.send(f"{config.Tick} | Successfully voice deafened {deafened_len} users")

    @voice.command(description="Undeafens all the users in the voice channel.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(moderate_members=True))
    async def undeafenall(self, ctx, *, reason: str=None):
        reason = reason or "[No reason]"
        if ctx.author.voice is None:
            await ctx.send(f"You're not in any voice channel.")
            return
        voice_channel = ctx.author.voice.channel
        undeafened_len = 0
        for user in voice_channel.members:
            if user.voice.deaf:
                undeafened_len += 1
        await ctx.send(f"{config.Tick} | Voice undeafening {undeafened_len} users...")
        deafened_len = 0
        for user in voice_channel.members:
            if user.voice.deaf:
                deafened_len += 1
            await user.edit(deafen=False, reason=f"By {ctx.author}: {reason}")

        await ctx.send(f"{config.Tick} | Successfully voice undeafened {deafened_len} users")

async def setup(bot):
    await bot.add_cog(Voice(bot))