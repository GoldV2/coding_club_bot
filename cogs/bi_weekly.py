from os import path

from google.oauth2 import service_account
from gspread import authorize
from discord.ext import tasks, commands

class BiWeekly(commands.Cog):

    medals = ['🥇', '🥈', '🥉']
    
    SPREADSHEET_ID = "1mBX_5twvCYDQgXVxoEoaGwvBbT6U7nkCXr4lxufabV0"
    SHEET_NAME = "Points"
    
    CREDENTIALS = service_account.Credentials.from_service_account_file(
        path.dirname(path.realpath(__file__)) + '/' + 'keys.json',
        scopes=['https://www.googleapis.com/auth/spreadsheets'])
    
    def __init__(self, bot):
        self.bot = bot
        self.spreadsheet = self.get_spreadsheet()
        self.update_name_points()

        self.write_podium.start()

    @staticmethod
    def get_spreadsheet():
        client = authorize(BiWeekly.CREDENTIALS)
        spreadsheet = client.open_by_key(BiWeekly.SPREADSHEET_ID)

        return spreadsheet

    def get_and_format_sheet_data(self):    
        sheet = self.spreadsheet.worksheet(BiWeekly.SHEET_NAME)
        data = sheet.get_all_values()[1:]

        NAME = 0
        POINTS = 1
        name_points = {row[NAME]: int(row[POINTS]) for row in data}
        
        return name_points

    def update_name_points(self):
        self.name_points = self.get_and_format_sheet_data()

    def get_podium_channels(self):
        for category in self.bot.guilds[0].categories:
            if category.name == 'Bi-Weekly Challenges':
                break

        channels = category.channels[1:]
        return channels

    def determine_medalists(self, position):
        points_needed = sorted(list(set(self.name_points.values())), reverse=True)[position]
        medalists = [name for name, points in self.name_points.items() if points == points_needed]

        return medalists

    async def update_channel_name(self, channel, medalists, plural):
        if plural:
            await channel.edit(name=f"{channel.name[:2]}{medalists[0]} and Co")
        else:
            await channel.edit(name=f"{channel.name[:2]}{medalists[0]}")

    async def update_congrats_msg(self, channel, medalists, plural):
        msgs = await channel.history(limit=1).flatten()
        medalist = medalists[0]
        if len(msgs):
            if plural:
                await msgs[0].edit(content=f"Congratulations to {', '.join(medalists[:-1])}, and {medalists[-1]} for holding the {channel.name[0]} medal with {self.name_points[medalists[0]]} points!")
            
            else:
                await msgs[0].edit(content=f"Congratulations to {medalist} for holding the {channel.name[0]} medal with {self.name_points[medalist]} points!")

        else:
            if plural:
                await channel.send(content=f"Congratulations to {', '.join(medalists[:-1])}, and {medalists[-1]} for holding the {channel.name[0]} medal with {self.name_points[medalists[0]]} points!")

            else:
                await channel.send(content=f"Congratulations to {medalist} for holding the {channel.name[0]} medal with {self.name_points[medalist]} points!")

    async def update_channel_name_and_congrats_message(self, channels):
        for position, channel in enumerate(channels):
            medalists = self.determine_medalists(position)
            if len(medalists) > 1:
                await self.update_channel_name(channel, medalists, True)
                await self.update_congrats_msg(channel, medalists, True)

            else:
                await self.update_channel_name(channel, medalists, False)
                await self.update_congrats_msg(channel, medalists, False)

    @tasks.loop(minutes=60)
    async def write_podium(self):
        self.update_name_points()

        channels = self.get_podium_channels()
        await self.update_channel_name_and_congrats_message(channels)

    @commands.command()
    @commands.is_owner()
    async def update_podium(self, ctx):
        await self.write_podium()

    @write_podium.before_loop
    async def before_tasks(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(BiWeekly(bot))