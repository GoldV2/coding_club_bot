from discord.ext import commands

from db.user_management import view_db
from cogs.helpers import Helpers
from db.user_management import remove_user

class OfficerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def print_db(self, ctx):
        view_db()

    @commands.command()
    async def reset_user(self, ctx, id):
        user = ctx.guild.get_member(int(id))
        await Helpers.remove_role(ctx, user, "Member")
        remove_user(int(id))

def setup(bot):
    bot.add_cog(OfficerCommands(bot))