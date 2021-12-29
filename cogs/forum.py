from discord.embeds import Embed
from discord.ext import tasks, commands

from cogs.helpers import Helpers
from db.user_management import get_db

class Forum(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.write_best_helper_channel_name.start()

    # TODO refactor
    @tasks.loop(minutes=60)
    async def write_best_helper_channel_name(self):
        channel = await Helpers.get_channel(self.bot.guilds[0], '🦮│')

        THUMBS_UPS = 7
        db = sorted([user.split(', ') for user in get_db().split('\n')], key=lambda user: user[THUMBS_UPS], reverse=True)

        ID = 0
        first = await channel.guild.fetch_member(db[0][ID])

        new_name = channel.name[:2] + first.nick
        await channel.edit(name=new_name)

        second = await channel.guild.fetch_member(db[1][ID])
        third = await channel.guild.fetch_member(db[2][ID])
        
        embed = Embed(title="Forum Leaderboard", description="Thank you to all helpers!")
        embed.add_field(name="🥇 First Place 🥇", value=f"{first.nick} helped {db[0][THUMBS_UPS]} people", inline=False)
        embed.add_field(name="🥈 Second Place 🥈", value=f"{second.nick} helped {db[1][THUMBS_UPS]} people", inline=False)
        embed.add_field(name="🥉 Third Place 🥉", value=f"{third.nick} helped {db[2][THUMBS_UPS]} people", inline=False)
        embed.set_footer(text='Never forget to react with a "👍" when you are helped in the "general-help" channel. That is how you can give credit to who helped you.')

        msgs = await channel.history(limit=1).flatten()
        if len(msgs) > 0:
            msg = msgs[0]

            await msg.edit(embed=embed)

        else:
            await channel.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def update_best_helper_channel_name(self, ctx):
        await self.write_best_helper_channel_name()

    @write_best_helper_channel_name.before_loop
    async def before_tasks(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(Forum(bot))