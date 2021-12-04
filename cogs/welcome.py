from discord import Embed, Color
from discord.utils import get
from discord.ext import commands

# types
class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    # TODO make this a nice little process you can do through discord, similar to display
    @commands.command()
    async def update_welcome_message(self, ctx):
        title = 'Welcome'
        description = 'Coding Club Unnoficial Discord Server'
        field_1_name = 'About'
        field_1_value = """The objective of this server is to bring all our members together and create a fun environment where you can display your favorite projects, challenge others on coding problems, play some tic-tac-toe, and ask for help regarding anything. In other words, have a good time!

Important upcoming events will be listed under Events where you can mark yourself as interested

The "announcements" channel is connected with our Google Classroom. Follow this channel to receive a Discord notification and never miss a post!

The "bi-weekly-challenges" is also connected with the Google Classroom and posts all challenges.

When participating in any activity in this server, you have a chance to win an award. Keep an eye on the leaderboard channels!

Instructions on how to use each feature of the Coding Club bot is available in the respective channel."""

        field_2_name = 'Geting Started'
        field_2_value = 'To get started, write out your full name completely in the "edit-name" channel or edit your server profile.'


        footer = "The Coding Club bot controls most of the server's features. If you believe you encountered a bug, leave a message in the \"bug-report\" channel."
        
        color = Color.yellow()

        embed = Embed(color=color, title=title, description=description)
        embed.add_field(name=field_1_name, value=field_1_value, inline=False)
        embed.add_field(name=field_2_name, value=field_2_value, inline=False)
        embed.set_footer(text=footer)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Welcome(bot))