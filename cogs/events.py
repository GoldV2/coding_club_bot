from discord.ext import commands
from discord.channel import DMChannel

from cogs.helpers import Helpers
from cogs.project_display import EditProject, ProjectDisplayView
from cogs.welcome import RoleMessage
from db.user_management import add_user, remove_user, increment_on, update_user_name, get_user_by_id

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.name == self.bot.user.name:
            return

        elif type(message.channel) == DMChannel:
            return

        elif message.channel.name == 'edit-name' and message.author.id != message.guild.owner.id:
            await message.delete()
            await message.author.edit(nick=message.content)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.nick != after.nick:
            user = get_user_by_id(after.id)
            if not user:
                add_user(after.id, after.nick)
                await Helpers.add_role(after, 'Member')
                print(f"{after.nick} added to db")

            else:
                update_user_name(after.id, after.nick)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        remove_user(member.id)

    # TODO when adding more reactions, refactor so each reaction has its own function
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # checking if someone gave a thumbs up to someone else's message in the help channel
        help_channel = await Helpers.get_channel(self.bot.guilds[0], '🆘general-help🆘')
        if payload.channel_id == help_channel.id:
            if str(payload.emoji) == '👍':
                msg = await help_channel.fetch_message(payload.message_id)
                increment_on(msg.author.id, 'thumbs_ups')

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(EditProject())
        self.bot.add_view(RoleMessage())
        self.bot.add_view(ProjectDisplayView())

        print("Bot connected successfully!")

def setup(bot):
    bot.add_cog(Events(bot))