from discord.ext import commands
from discord.channel import DMChannel

from cogs.helpers import Helpers
from cogs.project_display import EditProject
from db.user_management import add_user, update_user_name, get_user_by_id

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.name == self.bot.user.name:
            return

        elif type(message.channel) == DMChannel:
            return

        elif message.channel.name == 'edit-name' and message.author.id != message.guild.owner:
            await message.author.edit(nick=message.content)

        print("Message sent by", message.author.name)
        print("-", message.content)
    
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.nick != after.nick:
            user = get_user_by_id(after.id)
            if not user:
                add_user(after.id, after.nick)
                await Helpers.give_role(self.bot.guilds[0], after, 'Member')
                print(f"{after.nick} added to db")

            else:
                update_user_name(after.id, after.nick)

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(EditProject())
        print("Bot connected successfully!")


def setup(bot):
    bot.add_cog(Events(bot))