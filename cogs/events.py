from discord.ext import commands
from discord.channel import DMChannel

from cogs.helpers import Helpers

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # if message.author == self.bot: == False
        if message.author.name == self.bot.user.name:
            return

        elif type(message.channel) == DMChannel:
            return

        elif message.channel.name == 'edit-name' and message.author.id != message.guild.owner:
            await message.author.edit(nick=message.content)

            roles = [role.name for role in message.author.roles]
            # subtracting one from roles because everyone has the @everyone role.
            if 'Member' not in roles:
                await Helpers.give_role(message, message.author, 'Member')

            # await message.delete()

        print("Message sent by", message.author.name)
        print("-", message.content)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot connected successfully!")

def setup(bot):
    bot.add_cog(Events(bot))