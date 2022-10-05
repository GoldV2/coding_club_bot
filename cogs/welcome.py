from textwrap import dedent

import discord
from discord.ext import commands
from discord.utils import get

from cogs.helpers import Helpers
# types
class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # TODO make this a nice little process you can do through discord, similar to display
    @commands.command()
    @commands.is_owner()
    async def update_welcome_message(self, ctx):
        title = 'Welcome'
        description = 'Coding Club Unnoficial Discord Server'
        field_1_name = 'About'
        field_1_value = dedent("""          The objective of this server is to bring all our members together and create a fun environment where you can display your favorite projects, challenge others on coding problems, play some tic-tac-toe, and ask for help regarding anything. In other words, have a good time!

            Important upcoming events will be listed under Events where you can mark yourself as interested

            The "announcements" channel is connected with our Google Classroom. Follow this channel to receive a Discord notification and never miss a post!

            The "bi-weekly-challenges" is also connected with the Google Classroom and posts all challenges.

            When participating in any activity in this server, you have a chance to win an award. Keep an eye on the leaderboard channels!

            Instructions on how to use each feature of the Coding Club bot is available in the respective channel.""")

        field_2_name = 'Geting Started'
        field_2_value = 'To get started, write out your full name completely in the "edit-name" channel or edit your server profile.'


        footer = "Classroom code: hgtqblw"
        
        color = discord.Color.yellow()

        embed = discord.Embed(color=color, title=title, description=description)
        embed.add_field(name=field_1_name, value=field_1_value, inline=False)
        embed.add_field(name=field_2_name, value=field_2_value, inline=False)
        embed.set_footer(text=footer)

        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def update_role_message(self, ctx):
        title = "Select Your School!"
        field_name = "Roles"
        field_value = """           :hospital: <@&925549119584473149>
            :computer: <@&925549255148593152>
            :performing_arts: <@&925549347582664734>
            :gear: <@&925552983771602984>
            :magnet: <@&925549484644134912>"""
        
        color = discord.Color.yellow()

        embed = discord.Embed(color=color, title=title)
        embed.add_field(name=field_name, value=field_value)
        embed.set_footer(text="Don't forget to write your name!")
        
        await ctx.send(embed=embed, view=RoleMessage())

class RoleMessage(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        schools = [('aahs', '🏥'), ('ait', '💻'),
            ('apa', '🎭'), ('uctech', '⚙️'),
            ('mhs', '🧲')]

        for school in schools:
            self.add_item(RoleButton(school[0], school[1]))

class RoleButton(discord.ui.Button):
    def __init__(self, label, emoji):
        super().__init__(style=discord.ButtonStyle.gray,
            label=label.upper(),
            custom_id=label,
            emoji=emoji)

    async def callback(self, interaction):
        role = self.label
        member = interaction.user
        if role in [r.name for r in member.roles]:
            await Helpers.remove_role(member, role)
            await interaction.response.send_message(content="Role removed. Press the button again to revert changes.", ephemeral=True)

        else:
            await Helpers.add_role(member, role)
            await interaction.response.send_message(content="Role added. Press the button again to revert changes.", ephemeral=True)

def setup(bot):
    bot.add_cog(Welcome(bot))