from discord.utils import get
from discord.ext import commands

class Helpers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def remove_role(ctx, member, name):
        role = get(ctx.guild.roles, name=name)
        await member.remove_roles(role)

    @staticmethod
    async def give_role(ctx, member, name):
        role = get(ctx.guild.roles, name=name)
        await member.add_roles(role)

    @staticmethod
    async def get_channel(bot, channel_name):
        for channel in bot.guilds[0].channels:
            if channel_name in channel.name:
                return channel

def setup(bot):
    bot.add_cog(Helpers(bot))