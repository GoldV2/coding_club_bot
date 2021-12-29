from discord.utils import get
from discord.ext import commands

# types
from discord.channel import TextChannel
from discord.member import Member

class Helpers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def remove_role(member: Member, role_name: str) -> None:
        role = get(member.guild.roles, name=role_name)
        await member.remove_roles(role)

    @staticmethod
    async def add_role(member: Member, role_name: str) -> None:
        role = get(member.guild.roles, name=role_name)
        await member.add_roles(role)

    @staticmethod
    async def get_channel(guild, channel_name: str) -> TextChannel:
        for channel in guild.channels:
            if channel_name in channel.name:
                return channel

def setup(bot):
    bot.add_cog(Helpers(bot))